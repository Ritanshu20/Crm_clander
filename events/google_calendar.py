"""
Google Calendar API integration module.
Handles OAuth authentication and calendar operations.
"""
import os
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings
from django.utils import timezone


class GoogleCalendarService:
    """
    Service class for Google Calendar API operations.
    Handles authentication and CRUD operations.
    """
    
    SCOPES = settings.GOOGLE_CALENDAR_SCOPES
    
    def __init__(self, user):
        """
        Initialize Google Calendar service for a user.
        
        Args:
            user: Django User instance
        """
        self.user = user
        self.credentials = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """
        Authenticate with Google Calendar API using OAuth 2.0.
        Uses credentials.json for initial auth and token.json for refresh.
        """
        creds = None
        token_file = settings.GOOGLE_TOKEN_FILE
        credentials_file = settings.GOOGLE_CREDENTIALS_FILE
        
        # Check if token.json exists (user has already authenticated)
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_file):
                    raise FileNotFoundError(
                        f"credentials.json not found at {credentials_file}. "
                        "Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.credentials = creds
        self.service = build('calendar', 'v3', credentials=creds)
    
    def create_event(self, event):
        """
        Create an event in Google Calendar.
        
        Args:
            event: Django Event instance
            
        Returns:
            str: Google Calendar event ID
        """
        try:
            # Convert Django datetime to RFC3339 format for Google Calendar
            start_time = event.start_datetime.isoformat()
            end_time = event.end_datetime.isoformat()
            
            # Build the event body
            event_body = {
                'summary': event.title,
                'description': event.description or '',
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                },
            }
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event_body
            ).execute()
            
            return created_event.get('id')
            
        except HttpError as error:
            raise Exception(f"An error occurred while creating Google Calendar event: {error}")
    
    def update_event(self, event):
        """
        Update an existing event in Google Calendar.
        
        Args:
            event: Django Event instance with google_event_id set
        """
        if not event.google_event_id:
            raise ValueError("Event does not have a Google Calendar event ID")
        
        try:
            # Convert Django datetime to RFC3339 format
            start_time = event.start_datetime.isoformat()
            end_time = event.end_datetime.isoformat()
            
            # Build the event body
            event_body = {
                'summary': event.title,
                'description': event.description or '',
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                },
            }
            
            # Update the event
            self.service.events().update(
                calendarId='primary',
                eventId=event.google_event_id,
                body=event_body
            ).execute()
            
        except HttpError as error:
            raise Exception(f"An error occurred while updating Google Calendar event: {error}")
    
    def delete_event(self, google_event_id):
        """
        Delete an event from Google Calendar.
        
        Args:
            google_event_id: Google Calendar event ID
        """
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=google_event_id
            ).execute()
        except HttpError as error:
            # If event not found, it's already deleted - that's okay
            if error.resp.status != 404:
                raise Exception(f"An error occurred while deleting Google Calendar event: {error}")

