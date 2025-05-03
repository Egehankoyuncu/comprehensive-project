from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .models import Profile, Session, Review, Message as ChatMessage
from .forms import UserRegistrationForm, ProfileUpdateForm, SessionBookingForm, ReviewForm, MessageForm
import json
from django.core.paginator import Paginator

def home(request):
    return redirect('tutor_search')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user=user,
                user_type=form.cleaned_data.get('user_type')
            )
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'core/profile.html', {'form': form, 'profile': profile})

def tutor_search(request):
    query = request.GET.get('q', '')
    subject = request.GET.get('subject', '')
    min_rating = request.GET.get('min_rating', 0)
    
    tutors = Profile.objects.filter(user_type='tutor')
    
    if query:
        tutors = tutors.filter(
            Q(user__username__icontains=query) |
            Q(subjects__icontains=query)
        )
    
    if subject:
        tutors = tutors.filter(subjects__icontains=subject)
    
    if min_rating:
        tutors = tutors.filter(user__tutor_sessions__review__rating__gte=min_rating).distinct()
    
    paginator = Paginator(tutors, 10)
    page = request.GET.get('page')
    tutors = paginator.get_page(page)
    
    return render(request, 'core/tutor_search.html', {
        'tutors': tutors,
        'query': query,
        'subject': subject,
        'min_rating': min_rating
    })

@login_required
def book_session(request, tutor_id):
    tutor = get_object_or_404(User, id=tutor_id)
    
    # Check if the user is trying to book themselves
    if tutor == request.user:
        messages.error(request, "You cannot book a session with yourself.")
        return redirect('tutor_search')
        
    if request.method == 'POST':
        form = SessionBookingForm(request.POST)
        if form.is_valid():
            # Check for time conflicts
            new_date = form.cleaned_data['date']
            new_start = form.cleaned_data['start_time']
            new_end = form.cleaned_data['end_time']
            
            # Check if the end time is after the start time
            if new_end <= new_start:
                messages.error(request, 'End time must be after start time.')
                return render(request, 'core/book_session.html', {'form': form, 'tutor': tutor})
            
            # Check for conflicts with existing sessions
            conflicts = Session.objects.filter(
                Q(tutor=tutor) | Q(student=request.user),
                date=new_date,
                status__in=['pending', 'confirmed'],
            ).filter(
                Q(start_time__lt=new_end, end_time__gt=new_start) |
                Q(start_time=new_start) |
                Q(end_time=new_end)
            )
            
            if conflicts.exists():
                messages.error(request, 'This time slot conflicts with an existing session.')
                return render(request, 'core/book_session.html', {'form': form, 'tutor': tutor})
            
            session = form.save(commit=False)
            session.student = request.user
            session.tutor = tutor
            session.save()
            messages.success(request, 'Session booked successfully!')
            return redirect('my_sessions')
    else:
        form = SessionBookingForm()
    return render(request, 'core/book_session.html', {'form': form, 'tutor': tutor})

@login_required
def my_sessions(request):
    if request.user.profile.user_type == 'student':
        sessions = Session.objects.filter(student=request.user).order_by('date', 'start_time')
    else:
        sessions = Session.objects.filter(tutor=request.user).order_by('date', 'start_time')
    return render(request, 'core/my_sessions.html', {'sessions': sessions})

@login_required
def session_detail(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    if request.method == 'POST':
        if 'action' in request.POST:
            action = request.POST.get('action')
            if action == 'confirm' and request.user == session.tutor:
                session.status = 'confirmed'
                session.save()
                messages.success(request, 'Session confirmed successfully!')
            elif action == 'cancel':
                session.status = 'cancelled'
                session.save()
                messages.warning(request, 'Session cancelled.')
            return redirect('session_detail', session_id=session.id)
        
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.session = session
            review.save()
            messages.success(request, 'Review submitted successfully!')
            return redirect('session_detail', session_id=session.id)
    else:
        form = ReviewForm()
    return render(request, 'core/session_detail.html', {
        'session': session,
        'form': form
    })

@login_required
def messages_view(request):
    conversations = ChatMessage.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-timestamp')
    return render(request, 'core/messages.html', {'conversations': conversations})

@login_required
def send_message(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('messages')
    else:
        form = MessageForm()
    return render(request, 'core/send_message.html', {'form': form, 'receiver': receiver})

def load_sample_tutors():
    try:
        with open('core/fixtures/sample_tutors.json', 'r') as f:
            tutors_data = json.load(f)
            for tutor_data in tutors_data:
                if not User.objects.filter(username=tutor_data['name']).exists():
                    user = User.objects.create_user(
                        username=tutor_data['name'],
                        password='tutor123'  # Default password for sample tutors
                    )
                    Profile.objects.create(
                        user=user,
                        user_type='tutor',
                        subjects=tutor_data['subject'],
                        availability=tutor_data['availability'],
                        hourly_rate=tutor_data['hourly_rate']
                    )
    except FileNotFoundError:
        print("Sample tutors file not found")
