# CRM Event Calendar

A complete, production-structured Django application for managing events with CRM-style reminders.

## Features

- ✅ **User Authentication**: Secure login and registration system
- ✅ **Event Management**: Create, read, update, and delete events
- ✅ **CRM-Style Reminders**: Browser popup alerts with configurable reminder times
- ✅ **Dashboard**: Overview of today's events, upcoming events, and pending reminders
- ✅ **Calendar View**: FullCalendar.js integration with month/week/day views
- ✅ **User Isolation**: Each user can only view and manage their own events
- ✅ **Modern UI**: Clean, professional CRM-style interface

## Project Structure

```
crm_calendar/
├── crm_calendar/          # Django project settings
│   ├── settings.py        # Project configuration
│   ├── urls.py            # Main URL routing
│   └── ...
├── events/                 # Main application
│   ├── models.py          # Event model
│   ├── views.py           # View functions
│   ├── forms.py           # Event forms
│   ├── urls.py            # App URL routing
│   └── ...
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   └── events/            # Event-related templates
├── static/                 # Static files (CSS, JS, images)
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Installation & Setup

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Usage Guide

### Creating an Event

1. Log in to the application
2. Click **"New Event"** in the navigation bar
3. Fill in the event details:
   - Title (required)
   - Description/Notes (optional)
   - Start date & time (required)
   - End date & time (required)
   - Reminder time (5 min, 10 min, 30 min, 1 hour, or 1 day before)
4. Click **"Save Event"**

### Reminder System

The CRM-style reminder system works as follows:

- **Reminder Options**: 5 minutes, 10 minutes, 30 minutes, 1 hour, or 1 day before the event
- **Trigger Mechanism**: Reminders trigger when you visit the dashboard page
- **Browser Alert**: A popup alert appears in your browser showing event details
- **One-Time Trigger**: Each reminder triggers only once per event
- **Automatic Marking**: After triggering, the reminder is automatically marked as "triggered"

### Dashboard

The dashboard shows:
- **Today's Events**: All events scheduled for today
- **Upcoming Events**: Next 10 upcoming events
- **Pending Reminders**: Events with reminders that need attention

### Calendar View

- **FullCalendar.js Integration**: Professional calendar interface
- **Multiple Views**: Month, Week, and Day views
- **Event Details**: Click any event to view full details
- **Real-time Updates**: Events are loaded from the local database

## Event Model Fields

Each event contains:
- `title`: Event title
- `description`: Event description/notes
- `start_datetime`: Event start date and time
- `end_datetime`: Event end date and time
- `reminder_minutes`: Reminder time before event (5, 10, 30, 60, or 1440 minutes)
- `reminder_triggered`: Boolean flag indicating if reminder was triggered
- `created_by`: User who created the event (foreign key)
- `created_at`: Timestamp when event was created
- `updated_at`: Timestamp when event was last updated

## Security Features

- **User Authentication**: Django's built-in authentication system
- **User Isolation**: Users can only access their own events
- **CSRF Protection**: All forms are protected against CSRF attacks
- **Credentials Protection**: Sensitive files are excluded from version control

## Technology Stack

- **Backend**: Django 4.2+
- **Frontend**: Django Templates, HTML, CSS, JavaScript
- **Calendar Library**: FullCalendar.js 6.1.10
- **UI Framework**: Bootstrap 5.3.0
- **Icons**: Bootstrap Icons
- **Database**: SQLite (development)

## Development Notes

### Database

The application uses SQLite by default. For production, consider switching to PostgreSQL or MySQL.

### Static Files

Static files are served from the `static/` directory. In production, use `python manage.py collectstatic` and configure a web server (nginx, Apache) to serve static files.

### Time Zone

The application uses UTC by default. To change the time zone, modify `TIME_ZONE` in `settings.py`.

## Troubleshooting

### Reminder Not Triggering

- Reminders only trigger when you visit the dashboard
- Make sure the reminder time has passed but the event hasn't started yet
- Check that `reminder_triggered` is `False` in the database

## Production Deployment

Before deploying to production:

1. Set `DEBUG = False` in `settings.py`
2. Generate a new `SECRET_KEY` and keep it secure
3. Configure `ALLOWED_HOSTS`
4. Set up a production database (PostgreSQL recommended)
5. Configure static file serving
6. Set up HTTPS
7. Use environment variables for sensitive settings

## License

This project is open source and available for educational and commercial use.

## Support

For issues or questions, please refer to the Django documentation.

---

**Built with ❤️ using Django**

