"""
Admin configuration for Event model.
"""
from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_datetime', 'end_datetime', 'created_by', 'reminder_triggered', 'created_at']
    list_filter = ['reminder_triggered', 'start_datetime', 'created_by']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'start_datetime', 'end_datetime')
        }),
        ('Reminder Settings', {
            'fields': ('reminder_minutes', 'reminder_triggered')
        }),
        ('User & Timestamps', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
        ('Google Calendar', {
            'fields': ('google_event_id',)
        }),
    )

