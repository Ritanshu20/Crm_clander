"""
Views for CRM Event Calendar application.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Event
from .forms import EventForm
from .google_calendar import GoogleCalendarService
from django.views.decorators.http import require_POST

from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def logout_view(request):
    """
    Handles both GET and POST for logout.
    GET request → silently redirect to login
    POST request → logout and redirect to login
    """
    if request.method == "POST":
        logout(request)
    return redirect('login')


def register_view(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'events/register.html', {'form': form})


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'events/login.html')


@login_required
def dashboard_view(request):
    """
    Dashboard view showing today's events, upcoming events, and pending reminders.
    Implements CRM-style reminder popup logic.
    """
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    # Get user's events only (user isolation)
    user_events = Event.objects.filter(created_by=request.user)
    
    # Today's events (all events scheduled for today, including past and future events today)
    todays_events = user_events.filter(
        start_datetime__gte=today_start,
        start_datetime__lt=today_end
    ).order_by('start_datetime')
    
    # Upcoming events (all events that start after current time, including events later today)
    # This will show events later today and future days
    upcoming_events = user_events.filter(
        start_datetime__gt=now
    ).order_by('start_datetime')[:10]  # Limit to 10 upcoming events
    
    # Pending reminders (not triggered, reminder time has passed, event hasn't started)
    pending_reminders = []
    for event in user_events.filter(reminder_triggered=False):
        if event.should_trigger_reminder():
            pending_reminders.append(event)
    
    context = {
        'todays_events': todays_events,
        'upcoming_events': upcoming_events,
        'pending_reminders': pending_reminders,
    }
    
    return render(request, 'events/dashboard.html', context)


@login_required
def calendar_view(request):
    """Calendar view using FullCalendar.js."""
    return render(request, 'events/calendar.html')


@login_required
def events_json(request):
    """
    API endpoint to return events as JSON for FullCalendar.
    Returns only events for the logged-in user.
    """
    events = Event.objects.filter(created_by=request.user)
    events_list = []
    
    for event in events:
        events_list.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_datetime.isoformat(),
            'end': event.end_datetime.isoformat(),
            'description': event.description or '',
            'reminder_minutes': event.reminder_minutes,
            'reminder_triggered': event.reminder_triggered,
        })
    
    return JsonResponse(events_list, safe=False)


@login_required
def event_create_view(request):
    """Create a new event."""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            
            # Handle Google Calendar sync
            sync_with_google = form.cleaned_data.get('sync_with_google', False)
            if sync_with_google:
                try:
                    google_service = GoogleCalendarService(request.user)
                    google_event_id = google_service.create_event(event)
                    event.google_event_id = google_event_id
                    event.save()
                    messages.success(request, 'Event created and synced with Google Calendar!')
                except Exception as e:
                    messages.warning(
                        request,
                        f'Event created locally, but Google Calendar sync failed: {str(e)}'
                    )
            else:
                messages.success(request, 'Event created successfully!')
            
            return redirect('dashboard')
    else:
        form = EventForm()
    
    return render(request, 'events/event_form.html', {
        'form': form,
        'title': 'Create Event'
    })


@login_required
def event_update_view(request, pk):
    """Update an existing event."""
    event = get_object_or_404(Event, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            # Check if Google sync was previously enabled
            had_google_sync = bool(event.google_event_id)
            sync_with_google = form.cleaned_data.get('sync_with_google', False)
            
            event = form.save()
            
            # Handle Google Calendar sync
            if sync_with_google:
                try:
                    google_service = GoogleCalendarService(request.user)
                    if had_google_sync:
                        # Update existing Google Calendar event
                        google_service.update_event(event)
                        messages.success(request, 'Event updated and synced with Google Calendar!')
                    else:
                        # Create new Google Calendar event
                        google_event_id = google_service.create_event(event)
                        event.google_event_id = google_event_id
                        event.save()
                        messages.success(request, 'Event updated and synced with Google Calendar!')
                except Exception as e:
                    messages.warning(
                        request,
                        f'Event updated locally, but Google Calendar sync failed: {str(e)}'
                    )
            elif had_google_sync:
                # User unchecked sync, but event was previously synced
                # Optionally delete from Google Calendar or just leave it
                # For now, we'll just remove the local reference
                event.google_event_id = None
                event.save()
                messages.info(request, 'Event updated. Google Calendar sync disabled.')
            else:
                messages.success(request, 'Event updated successfully!')
            
            return redirect('dashboard')
    else:
        form = EventForm(instance=event)
        # Pre-check sync checkbox if event has Google event ID
        form.fields['sync_with_google'].initial = bool(event.google_event_id)
    
    return render(request, 'events/event_form.html', {
        'form': form,
        'event': event,
        'title': 'Update Event'
    })


@login_required
def event_delete_view(request, pk):
    """Delete an event."""
    event = get_object_or_404(Event, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        # Delete from Google Calendar if synced
        if event.google_event_id:
            try:
                google_service = GoogleCalendarService(request.user)
                google_service.delete_event(event.google_event_id)
            except Exception as e:
                messages.warning(
                    request,
                    f'Event deleted locally, but Google Calendar deletion failed: {str(e)}'
                )
        
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'events/event_confirm_delete.html', {'event': event})


@login_required
def event_detail_view(request, pk):
    """View event details."""
    event = get_object_or_404(Event, pk=pk, created_by=request.user)
    return render(request, 'events/event_detail.html', {'event': event})


@login_required
def trigger_reminder_view(request, pk):
    """
    API endpoint to trigger a reminder and mark it as triggered.
    Called via AJAX when reminder popup is shown.
    """
    event = get_object_or_404(Event, pk=pk, created_by=request.user)
    
    if event.should_trigger_reminder():
        event.mark_reminder_triggered()
        return JsonResponse({'success': True, 'message': 'Reminder triggered'})
    
    return JsonResponse({'success': False, 'message': 'Reminder cannot be triggered'})
