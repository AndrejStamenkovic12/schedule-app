# Appointment Scheduler Web App

A modern web application for scheduling personal appointments like hair salon, nail salon, massage therapy, personal training, and more. Built with Flask and Bootstrap for a beautiful, responsive user interface.

## 🌟 Features

- **Modern Web Interface**: Beautiful, responsive design that works on desktop and mobile
- **Multiple Appointment Types**: Hair salon, nail salon, massage therapy, personal training, spa treatments, and custom appointments
- **Smart Scheduling**: Prevents double-booking with conflict detection
- **Date-based Filtering**: View appointments by specific dates
- **Data Persistence**: Saves appointments to a JSON file
- **Real-time Validation**: Form validation with helpful error messages
- **Easy Management**: Intuitive web interface for scheduling, viewing, and canceling appointments

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Web App**:
   ```bash
   python run.py
   ```
   Or alternatively:
   ```bash
   python app.py
   ```

3. **Open Your Browser**:
   Go to `http://localhost:5000` to access the web application

## 📱 Web Interface

### Home Page
- View upcoming appointments at a glance
- Quick access to schedule new appointments
- Appointment type reference guide

### Schedule Appointment
- Easy-to-use form with validation
- Dropdown menus for appointment types and durations
- Date/time pickers with future-only validation
- Optional notes field

### View Appointments
- Complete list of all scheduled appointments
- Filter by specific dates
- Cancel appointments with confirmation dialog
- Color-coded appointment types

## 🎨 Appointment Types

- **Hair Salon** - Haircuts, coloring, styling
- **Nail Salon** - Manicures, pedicures, nail art
- **Massage Therapy** - Relaxation and therapeutic massage
- **Personal Training** - Fitness and workout sessions
- **Spa Treatment** - Facials, body treatments, wellness
- **Other** - Custom appointment types

## 💾 Data Storage

Appointments are automatically saved to `appointments.json` in the same directory as the application. This file will be created automatically when you schedule your first appointment.

## 🛠️ Technical Details

- **Backend**: Flask (Python web framework)
- **Frontend**: Bootstrap 5 + Custom CSS
- **Icons**: Font Awesome
- **Data**: JSON file storage
- **Validation**: Client-side and server-side validation

## 📋 Requirements

- Python 3.6 or higher
- Flask 2.3.3
- Werkzeug 2.3.7

## 🔧 Development

The application structure:
```
├── app.py                 # Main Flask application
├── run.py                 # Simple runner script
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── schedule.html     # Schedule appointment
│   └── appointments.html # View appointments
├── static/               # Static files
│   ├── style.css         # Custom styles
│   └── script.js         # JavaScript functionality
└── appointments.json     # Data storage (created automatically)
```

## 🌐 Access

Once running, the web app will be available at:
- **Local**: http://localhost:5000
- **Network**: http://[your-ip]:5000 (accessible from other devices on your network)

The application includes a modern, mobile-responsive interface that works great on phones, tablets, and desktop computers!
