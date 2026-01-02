"""
Forms for Event creation and editing.
"""
from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    """
    Form for creating and editing events.
    Includes checkbox for Google Calendar sync.
    """
    sync_with_google = forms.BooleanField(
        required=False,
        initial=False,
        label="Sync with Google Calendar",
        help_text="Check this to sync this event with your Google Calendar"
    )
    
    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'start_datetime',
            'end_datetime',
            'reminder_minutes',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter event title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter event description or notes'
            }),
            'start_datetime': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'end_datetime': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'reminder_minutes': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def clean(self):
        """Validate that end_datetime is after start_datetime."""
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        
        if start_datetime and end_datetime:
            if end_datetime <= start_datetime:
                raise forms.ValidationError(
                    "End date and time must be after start date and time."
                )
        
        return cleaned_data

