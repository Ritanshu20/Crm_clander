"""
Event model for CRM Event Calendar.
Each event represents a scheduled activity with reminder functionality.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Event(models.Model):
    """
    Event model representing a calendar event with CRM-style reminders.
    
    All events are stored locally in Django database.
    Google Calendar sync is optional via google_event_id field.
    """
    
    # Reminder choices (in minutes before event)
    REMINDER_CHOICES = [
        (5, '5 minutes before'),
        (10, '10 minutes before'),
        (30, '30 minutes before'),
        (60, '1 hour before'),
        (1440, '1 day before'),
    ]
    
    # Basic event information
    title = models.CharField(max_length=200, help_text="Event title")
    description = models.TextField(blank=True, null=True, help_text="Event description/notes")
    
    # Date and time
    start_datetime = models.DateTimeField(help_text="Event start date and time")
    end_datetime = models.DateTimeField(help_text="Event end date and time")
    
    # Reminder settings
    reminder_minutes = models.IntegerField(
        choices=REMINDER_CHOICES,
        default=30,
        help_text="Reminder time before event"
    )
    reminder_triggered = models.BooleanField(
        default=False,
        help_text="Whether the reminder has been triggered"
    )
    
    # User and timestamps
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='events',
        help_text="User who created this event"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Google Calendar integration (optional)
    google_event_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Google Calendar event ID for synchronization"
    )
    
    class Meta:
        ordering = ['start_datetime']
        indexes = [
            models.Index(fields=['created_by', 'start_datetime']),
            models.Index(fields=['reminder_triggered', 'start_datetime']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.start_datetime.strftime('%Y-%m-%d %H:%M')}"
    
    def get_reminder_datetime(self):
        """
        Calculate when the reminder should trigger.
        Returns the datetime when reminder should fire.
        """
        from datetime import timedelta
        return self.start_datetime - timedelta(minutes=self.reminder_minutes)
    
    def should_trigger_reminder(self):
        """
        Check if reminder should be triggered now.
        Returns True if:
        - Reminder hasn't been triggered yet
        - Current time is past the reminder time
        - Event hasn't started yet
        """
        if self.reminder_triggered:
            return False
        
        now = timezone.now()
        reminder_time = self.get_reminder_datetime()
        
        # Trigger if current time is past reminder time but before event start
        return reminder_time <= now < self.start_datetime
    
    def mark_reminder_triggered(self):
        """Mark the reminder as triggered."""
        self.reminder_triggered = True
        self.save(update_fields=['reminder_triggered'])

