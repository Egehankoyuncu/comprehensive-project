from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('tutors/', views.tutor_search, name='tutor_search'),
    path('book-session/<int:tutor_id>/', views.book_session, name='book_session'),
    path('my-sessions/', views.my_sessions, name='my_sessions'),
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
    path('messages/', views.messages_view, name='messages'),
    path('send-message/<int:receiver_id>/', views.send_message, name='send_message'),
] 