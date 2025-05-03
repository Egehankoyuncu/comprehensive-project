from django.contrib import admin
from .models import Profile, Session, Review, Message

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'subjects', 'hourly_rate')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'subjects')

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('student', 'tutor', 'subject', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('student__username', 'tutor__username', 'subject')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('session', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__username', 'receiver__username', 'content')
