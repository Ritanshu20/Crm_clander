"""
URL configuration for events app.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    #path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard and Calendar
    path('', views.dashboard_view, name='dashboard'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('events/json/', views.events_json, name='events_json'),
    
    # Event CRUD
    path('event/create/', views.event_create_view, name='event_create'),
    path('event/<int:pk>/', views.event_detail_view, name='event_detail'),
    path('event/<int:pk>/update/', views.event_update_view, name='event_update'),
    path('event/<int:pk>/delete/', views.event_delete_view, name='event_delete'),
    
    # Reminder API
    path('event/<int:pk>/trigger-reminder/', views.trigger_reminder_view, name='trigger_reminder'),
]

