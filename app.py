from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import json
import os
import hashlib
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from functools import wraps

app = Flask(__name__)
# Use a consistent secret key to prevent session loss on app restart
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-12345678')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# Session configuration for persistent login
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Session lasts 7 days

# Simple authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Simple User Manager
class SimpleUserManager:
    def __init__(self, users_file: str = "users.json"):
        self.users_file = users_file
        self.users = self.load_users()
    
    def load_users(self) -> List[Dict]:
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, password: str, email: str = "", 
                   role: str = "consumer", **kwargs) -> bool:
        if any(user['username'].lower() == username.lower() for user in self.users):
            return False
        
        user = {
            'id': len(self.users) + 1,
            'username': username,
            'password': self.hash_password(password),
            'email': email,
            'phone': kwargs.get('phone', ''),
            'name': kwargs.get('name', username),
            'profile_picture': '',
            'role': role,  # 'consumer' or 'provider'
            'created_at': datetime.now().isoformat()
        }
        
        # Provider-specific fields
        if role == 'provider':
            user['business_name'] = kwargs.get('business_name', '')
            user['business_description'] = kwargs.get('business_description', '')
            user['service_category'] = kwargs.get('service_category', '')
            user['services_offered'] = kwargs.get('services_offered', '')
            user['address'] = kwargs.get('address', '')
            user['availability'] = kwargs.get('availability', {
                'monday': {'enabled': True, 'start': '09:00', 'end': '17:00'},
                'tuesday': {'enabled': True, 'start': '09:00', 'end': '17:00'},
                'wednesday': {'enabled': True, 'start': '09:00', 'end': '17:00'},
                'thursday': {'enabled': True, 'start': '09:00', 'end': '17:00'},
                'friday': {'enabled': True, 'start': '09:00', 'end': '17:00'},
                'saturday': {'enabled': False, 'start': '09:00', 'end': '17:00'},
                'sunday': {'enabled': False, 'start': '09:00', 'end': '17:00'}
            })
        
        self.users.append(user)
        self.save_users()
        return True
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        user = next((u for u in self.users if u['username'].lower() == username.lower()), None)
        if user and user['password'] == self.hash_password(password):
            user_data = {
                'id': user['id'], 
                'username': user['username'], 
                'email': user.get('email', ''),
                'phone': user.get('phone', ''),
                'name': user.get('name', user['username']),
                'profile_picture': user.get('profile_picture', ''),
                'role': user.get('role', 'consumer')
            }
            
            # Add provider-specific fields
            if user.get('role') == 'provider':
                user_data['business_name'] = user.get('business_name', '')
                user_data['business_description'] = user.get('business_description', '')
                user_data['service_category'] = user.get('service_category', '')
                user_data['services_offered'] = user.get('services_offered', '')
                user_data['address'] = user.get('address', '')
                user_data['availability'] = user.get('availability', {})
            
            return user_data
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        user = next((u for u in self.users if u['id'] == user_id), None)
        if user:
            user_data = {
                'id': user['id'], 
                'username': user['username'], 
                'email': user.get('email', ''),
                'phone': user.get('phone', ''),
                'name': user.get('name', user['username']),
                'profile_picture': user.get('profile_picture', ''),
                'role': user.get('role', 'consumer')
            }
            
            # Add provider-specific fields
            if user.get('role') == 'provider':
                user_data['business_name'] = user.get('business_name', '')
                user_data['business_description'] = user.get('business_description', '')
                user_data['service_category'] = user.get('service_category', '')
                user_data['services_offered'] = user.get('services_offered', '')
                user_data['address'] = user.get('address', '')
                user_data['availability'] = user.get('availability', {})
            
            return user_data
        return None
    
    def update_user(self, user_id: int, name: str = None, email: str = None, 
                   phone: str = None, profile_picture: str = None, **kwargs) -> bool:
        user = next((u for u in self.users if u['id'] == user_id), None)
        if not user:
            return False
        
        if name is not None:
            user['name'] = name
        if email is not None:
            user['email'] = email
        if phone is not None:
            user['phone'] = phone
        if profile_picture is not None:
            user['profile_picture'] = profile_picture
        
        # Provider-specific fields
        if user.get('role') == 'provider':
            if 'business_name' in kwargs:
                user['business_name'] = kwargs['business_name']
            if 'business_description' in kwargs:
                user['business_description'] = kwargs['business_description']
            if 'service_category' in kwargs:
                user['service_category'] = kwargs['service_category']
            if 'services_offered' in kwargs:
                user['services_offered'] = kwargs['services_offered']
            if 'address' in kwargs:
                user['address'] = kwargs['address']
        
        self.save_users()
        return True

# Initialize managers
user_manager = SimpleUserManager()


class AppointmentScheduler:
    def __init__(self, data_file: str = "appointments.json"):
        self.data_file = data_file
        self.appointments = self.load_appointments()
        self.appointment_types = {
            "hair": "Hair Salon",
            "nails": "Nail Salon", 
            "massage": "Massage Therapy",
            "training": "Personal Training",
            "spa": "Spa Treatment",
            "other": "Other"
        }
    
    def load_appointments(self) -> List[Dict]:
        """Load appointments from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    # Convert datetime strings back to datetime objects
                    for apt in data:
                        apt['datetime'] = datetime.fromisoformat(apt['datetime'])
                        apt['created_at'] = datetime.fromisoformat(apt['created_at'])
                    return data
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_appointments(self):
        """Save appointments to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.appointments, f, indent=2, default=str)
    
    def add_appointment(self, appointment_type: str, date: str, time: str, 
                       duration: int, notes: str = "", user_id: int = None, 
                       provider_id: int = None) -> bool:
        """Add a new appointment"""
        try:
            # Parse date and time
            appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            
            # Check for conflicts
            if self.has_conflict(appointment_datetime, duration):
                return False
            
            appointment = {
                "id": len(self.appointments) + 1,
                "type": appointment_type,
                "datetime": appointment_datetime,
                "duration": duration,
                "notes": notes,
                "created_at": datetime.now(),
                "user_id": user_id,
                "provider_id": provider_id,
                "status": "pending"  # pending, confirmed, declined
            }
            
            self.appointments.append(appointment)
            self.save_appointments()
            return True
            
        except ValueError:
            return False
    
    def has_conflict(self, appointment_datetime: datetime, duration: int) -> bool:
        """Check if appointment conflicts with existing ones"""
        end_time = appointment_datetime + timedelta(minutes=duration)
        
        for existing in self.appointments:
            existing_start = existing["datetime"]
            existing_end = existing_start + timedelta(minutes=existing["duration"])
            
            # Check for overlap
            if (appointment_datetime < existing_end and end_time > existing_start):
                return True
        return False
    
    def get_appointments(self, date: Optional[str] = None) -> List[Dict]:
        """Get appointments, optionally filtered by date"""
        if date:
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d").date()
                return [apt for apt in self.appointments 
                       if apt["datetime"].date() == target_date]
            except ValueError:
                return []
        return sorted(self.appointments, key=lambda x: x["datetime"])
    
    def cancel_appointment(self, appointment_id: int) -> bool:
        """Cancel an appointment by ID"""
        for i, appointment in enumerate(self.appointments):
            if appointment["id"] == appointment_id:
                del self.appointments[i]
                self.save_appointments()
                return True
        return False
    
    def get_appointment_types(self) -> Dict[str, str]:
        """Get available appointment types"""
        return self.appointment_types

# Initialize scheduler
scheduler = AppointmentScheduler()

# Simple Review Manager
class ReviewManager:
    def __init__(self, reviews_file: str = "reviews.json"):
        self.reviews_file = reviews_file
        self.reviews = self.load_reviews()
    
    def load_reviews(self) -> List[Dict]:
        if os.path.exists(self.reviews_file):
            try:
                with open(self.reviews_file, 'r') as f:
                    data = json.load(f)
                    # Convert datetime strings back to datetime objects
                    for review in data:
                        review['created_at'] = datetime.fromisoformat(review['created_at'])
                    return data
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_reviews(self):
        with open(self.reviews_file, 'w') as f:
            json.dump(self.reviews, f, indent=2, default=str)
    
    def add_review(self, provider_id: int, customer_id: int, appointment_id: int, 
                   rating: int, comment: str = "") -> bool:
        # Check if review already exists for this appointment
        existing = next((r for r in self.reviews if r['appointment_id'] == appointment_id), None)
        if existing:
            return False
        
        review = {
            'id': len(self.reviews) + 1,
            'provider_id': provider_id,
            'customer_id': customer_id,
            'appointment_id': appointment_id,
            'rating': rating,
            'comment': comment,
            'created_at': datetime.now()
        }
        
        self.reviews.append(review)
        self.save_reviews()
        return True
    
    def get_provider_reviews(self, provider_id: int) -> List[Dict]:
        return [r for r in self.reviews if r['provider_id'] == provider_id]
    
    def get_average_rating(self, provider_id: int) -> float:
        provider_reviews = self.get_provider_reviews(provider_id)
        if not provider_reviews:
            return 0.0
        return sum(r['rating'] for r in provider_reviews) / len(provider_reviews)
    
    def has_reviewed(self, appointment_id: int) -> bool:
        return any(r['appointment_id'] == appointment_id for r in self.reviews)

# Initialize review manager
review_manager = ReviewManager()

def get_current_user():
    if 'user_id' in session:
        return user_manager.get_user_by_id(session['user_id'])
    return None

def get_providers_by_service(service_key):
    """Get all providers offering a specific service type"""
    providers = []
    for user in user_manager.users:
        if user.get('role') == 'provider' and user.get('service_category') == service_key:
            providers.append({
                'name': user.get('business_name', user.get('name')),
                'username': user.get('username'),
                'description': user.get('business_description', ''),
                'address': user.get('address', ''),
                'rating': 4.5  # Placeholder for future rating system
            })
    return providers

@app.route('/')
def index():
    """Home page - show upcoming appointments"""
    current_user = get_current_user()
    appointments = scheduler.get_appointments()
    # Show only future appointments for logged-in user
    now = datetime.now()
    if current_user:
        upcoming = [apt for apt in appointments if apt['datetime'] >= now and apt.get('user_id') == current_user['id']]
    else:
        upcoming = []
    return render_template('index.html', appointments=upcoming[:5], current_user=current_user)

@app.route('/schedule')
@login_required
def schedule():
    """Schedule appointment page"""
    current_user = get_current_user()
    
    # Get all providers with their availability
    all_providers = [user for user in user_manager.users if user.get('role') == 'provider']
    providers_data = []
    for provider in all_providers:
        providers_data.append({
            'id': provider['id'],
            'name': provider.get('name', ''),
            'business_name': provider.get('business_name', ''),
            'service_category': provider.get('service_category', ''),
            'availability': provider.get('availability', {})
        })
    
    return render_template('schedule.html', 
                         types=scheduler.get_appointment_types(), 
                         current_user=current_user,
                         providers=providers_data)

@app.route('/appointments')
@login_required
def appointments():
    """View all appointments"""
    current_user = get_current_user()
    all_appointments = scheduler.get_appointments()
    # Show only user's appointments
    appointments = [apt for apt in all_appointments if apt.get('user_id') == current_user['id']]
    return render_template('appointments.html', appointments=appointments, current_user=current_user)

@app.route('/appointments/<date>')
@login_required
def appointments_by_date(date):
    """View appointments by date"""
    current_user = get_current_user()
    all_appointments = scheduler.get_appointments(date)
    appointments = [apt for apt in all_appointments if apt.get('user_id') == current_user['id']]
    return render_template('appointments.html', appointments=appointments, selected_date=date, current_user=current_user)

@app.route('/history')
@login_required
def history():
    """View appointment history and orders"""
    current_user = get_current_user()
    all_appointments = scheduler.get_appointments()
    # Show only user's appointments
    appointments = [apt for apt in all_appointments if apt.get('user_id') == current_user['id']]
    # Sort by date descending (most recent first)
    appointments.sort(key=lambda x: x['datetime'], reverse=True)
    now = datetime.now()
    return render_template('history.html', appointments=appointments, now=now, current_user=current_user)

@app.route('/profile')
@login_required
def profile():
    """View user profile and information"""
    current_user = get_current_user()
    all_appointments = scheduler.get_appointments()
    user_appointments = [apt for apt in all_appointments if apt.get('user_id') == current_user['id']]
    
    user_profile = {
        'id': current_user['id'],
        'username': current_user['username'],
        'name': current_user.get('name', current_user['username']),
        'email': current_user.get('email', ''),
        'phone': current_user.get('phone', ''),
        'profile_picture': current_user.get('profile_picture', ''),
        'member_since': current_user.get('created_at', '')[:10] if current_user.get('created_at') else 'N/A',
        'total_appointments': len(user_appointments),
        'upcoming_appointments': len([apt for apt in user_appointments if apt['datetime'] > datetime.now()]),
        'completed_appointments': len([apt for apt in user_appointments if apt['datetime'] <= datetime.now()])
    }
    
    return render_template('profile.html', user=user_profile, current_user=current_user)

@app.route('/profile/edit', methods=['POST'])
@login_required
def edit_profile():
    """Update user profile"""
    current_user = get_current_user()
    
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    
    # Handle profile picture upload
    profile_picture = current_user.get('profile_picture', '')
    if 'profile_picture' in request.files:
        file = request.files['profile_picture']
        if file and file.filename:
            # Read and encode image as base64
            try:
                image_data = file.read()
                if len(image_data) > 0:
                    # Get file extension
                    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
                    if ext in ['jpg', 'jpeg', 'png', 'gif']:
                        profile_picture = f"data:image/{ext};base64,{base64.b64encode(image_data).decode()}"
                    else:
                        flash('Invalid image format. Please use JPG, PNG, or GIF.', 'error')
                        return redirect(url_for('profile'))
            except Exception as e:
                flash('Error uploading image. Please try again.', 'error')
                return redirect(url_for('profile'))
    
    # Provider-specific fields
    provider_data = {}
    if current_user.get('role') == 'provider':
        provider_data = {
            'business_name': request.form.get('business_name', '').strip(),
            'business_description': request.form.get('business_description', '').strip(),
            'service_category': request.form.get('service_category', '').strip(),
            'services_offered': request.form.get('services_offered', '').strip(),
            'address': request.form.get('address', '').strip()
        }
    
    # Update user
    if user_manager.update_user(current_user['id'], name=name, email=email, 
                                phone=phone, profile_picture=profile_picture, **provider_data):
        flash('Profile updated successfully!', 'success')
    else:
        flash('Error updating profile.', 'error')
    
    return redirect(url_for('profile'))

@app.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    """Delete user account and all associated data"""
    try:
        current_user = get_current_user()
        user_id = current_user['id']
        
        # Delete user from the user manager
        user_manager.users = [user for user in user_manager.users if user['id'] != user_id]
        user_manager.save_users()
        
        # Delete all appointments for this user
        all_appointments = scheduler.get_appointments()
        scheduler.appointments = [apt for apt in all_appointments if apt.get('user_id') != user_id]
        scheduler.save_appointments()
        
        # Clear session
        session.clear()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/help')
def help():
    """View help and support page"""
    current_user = get_current_user()
    # Sample FAQ data
    faqs = [
        {
            'category': 'General',
            'questions': [
                {
                    'question': 'How do I schedule an appointment?',
                    'answer': 'Click on "Schedule Appointment" in the navigation menu or on the home page. Fill out the form with your preferred service, date, time, and duration.'
                },
                {
                    'question': 'Can I cancel my appointment?',
                    'answer': 'Yes, you can cancel upcoming appointments from the "All Appointments" or "History" page. Click the trash icon next to the appointment you want to cancel.'
                },
                {
                    'question': 'How far in advance can I book?',
                    'answer': 'You can book appointments up to 3 months in advance. We recommend booking at least 24 hours ahead for the best availability.'
                }
            ]
        },
        {
            'category': 'Refunds & Cancellations',
            'questions': [
                {
                    'question': 'What is your refund policy?',
                    'answer': 'We offer full refunds for cancellations made at least 24 hours in advance. Cancellations within 24 hours may be subject to a 50% cancellation fee.'
                },
                {
                    'question': 'How do I request a refund?',
                    'answer': 'Contact our support team through the chat below or email support@appointmentscheduler.com. Include your appointment ID and reason for the refund request.'
                },
                {
                    'question': 'How long does it take to process refunds?',
                    'answer': 'Refunds are typically processed within 3-5 business days and will appear on your original payment method.'
                }
            ]
        },
        {
            'category': 'Technical Support',
            'questions': [
                {
                    'question': 'I forgot my password. How do I reset it?',
                    'answer': 'Click "Forgot Password" on the login page or contact support. We\'ll send you a secure reset link to your registered email address.'
                },
                {
                    'question': 'The website is not loading properly. What should I do?',
                    'answer': 'Try refreshing the page or clearing your browser cache. If the problem persists, contact our technical support team through the chat below.'
                },
                {
                    'question': 'Can I use the app on my mobile device?',
                    'answer': 'Yes! Our website is fully responsive and works great on mobile phones and tablets. No app download required.'
                }
            ]
        }
    ]
    
    # Sample support topics
    support_topics = [
        {'id': 'refund', 'title': 'Request Refund', 'icon': 'fas fa-money-bill-wave', 'color': 'danger'},
        {'id': 'reschedule', 'title': 'Reschedule Appointment', 'icon': 'fas fa-calendar-alt', 'color': 'warning'},
        {'id': 'technical', 'title': 'Technical Issue', 'icon': 'fas fa-bug', 'color': 'info'},
        {'id': 'billing', 'title': 'Billing Question', 'icon': 'fas fa-credit-card', 'color': 'primary'},
        {'id': 'general', 'title': 'General Inquiry', 'icon': 'fas fa-question-circle', 'color': 'secondary'}
    ]
    
    return render_template('help.html', faqs=faqs, support_topics=support_topics, current_user=current_user)

def get_services_data():
    """Get all services data - centralized for reuse"""
    # Get real provider counts from database
    return [
        {
            'category': 'Hair & Beauty',
            'icon': 'fas fa-cut',
            'color': 'primary',
            'description': 'Professional hair styling, coloring, and beauty treatments',
            'services': [
                {
                    'name': 'Hair Salon',
                    'description': 'Haircuts, styling, coloring, and treatments',
                    'duration': '60-180 min',
                    'price_range': '$50-$200',
                    'providers': ['Style Studio', 'Hair Masters', 'Beauty Lounge'],
                    'provider_details': get_providers_by_service('hair_salon'),
                    'popular': True
                },
                {
                    'name': 'Nail Salon',
                    'description': 'Manicures, pedicures, nail art, and nail care',
                    'duration': '30-90 min',
                    'price_range': '$25-$80',
                    'providers': ['Nail Art Studio', 'Perfect Nails', 'Luxury Nails'],
                    'provider_details': get_providers_by_service('nail_salon'),
                    'popular': True
                },
                {
                    'name': 'Eyebrow & Eyelash',
                    'description': 'Eyebrow shaping, lash extensions, and tinting',
                    'duration': '45-120 min',
                    'price_range': '$30-$150',
                    'providers': ['Brow Studio', 'Lash Lounge', 'Beauty Bar'],
                    'provider_details': get_providers_by_service('eyebrow_eyelash'),
                    'popular': False
                }
            ]
        },
        {
            'category': 'Wellness & Spa',
            'icon': 'fas fa-spa',
            'color': 'success',
            'description': 'Relaxation, wellness, and therapeutic treatments',
            'services': [
                {
                    'name': 'Massage Therapy',
                    'description': 'Swedish, deep tissue, hot stone, and therapeutic massage',
                    'duration': '60-120 min',
                    'price_range': '$80-$200',
                    'providers': ['Serenity Spa', 'Wellness Center', 'Therapeutic Touch'],
                    'provider_details': get_providers_by_service('massage_therapy'),
                    'popular': True
                },
                {
                    'name': 'Spa Treatment',
                    'description': 'Facials, body wraps, scrubs, and luxury spa services',
                    'duration': '90-240 min',
                    'price_range': '$100-$400',
                    'providers': ['Luxury Spa', 'Zen Wellness', 'Pamper Palace'],
                    'provider_details': get_providers_by_service('spa_treatment'),
                    'popular': True
                },
                {
                    'name': 'Aromatherapy',
                    'description': 'Essential oil treatments and aromatherapy sessions',
                    'duration': '45-90 min',
                    'price_range': '$60-$120',
                    'providers': ['Aroma Wellness', 'Essential Spa', 'Scent Studio'],
                    'provider_details': get_providers_by_service('aromatherapy'),
                    'popular': False
                }
            ]
        },
        {
            'category': 'Fitness & Training',
            'icon': 'fas fa-dumbbell',
            'color': 'warning',
            'description': 'Personal training, fitness classes, and wellness coaching',
            'services': [
                {
                    'name': 'Personal Training',
                    'description': 'One-on-one fitness training and workout sessions',
                    'duration': '60-90 min',
                    'price_range': '$60-$150',
                    'providers': ['FitLife Gym', 'Elite Training', 'Power Fitness'],
                    'provider_details': get_providers_by_service('personal_training'),
                    'popular': True
                },
                {
                    'name': 'Yoga Classes',
                    'description': 'Group and private yoga sessions for all levels',
                    'duration': '60-90 min',
                    'price_range': '$20-$80',
                    'providers': ['Zen Yoga Studio', 'Mindful Movement', 'Peaceful Practice'],
                    'provider_details': get_providers_by_service('yoga_classes'),
                    'popular': True
                },
                {
                    'name': 'Pilates',
                    'description': 'Pilates classes and private sessions',
                    'duration': '45-60 min',
                    'price_range': '$30-$100',
                    'providers': ['Core Pilates', 'Balance Studio', 'Flex Fitness'],
                    'provider_details': get_providers_by_service('pilates'),
                    'popular': False
                }
            ]
        },
        {
            'category': 'Health & Medical',
            'icon': 'fas fa-user-md',
            'color': 'info',
            'description': 'Medical and health-related appointments and treatments',
            'services': [
                {
                    'name': 'Dermatology',
                    'description': 'Skin consultations, treatments, and cosmetic procedures',
                    'duration': '30-90 min',
                    'price_range': '$100-$500',
                    'providers': ['Skin Care Clinic', 'Derma Solutions', 'Beauty Med'],
                    'provider_details': get_providers_by_service('dermatology'),
                    'popular': True
                },
                {
                    'name': 'Physical Therapy',
                    'description': 'Rehabilitation, injury recovery, and mobility improvement',
                    'duration': '45-60 min',
                    'price_range': '$80-$150',
                    'providers': ['Rehab Center', 'Mobility Plus', 'Healing Hands'],
                    'provider_details': get_providers_by_service('physical_therapy'),
                    'popular': True
                },
                {
                    'name': 'Nutrition Counseling',
                    'description': 'Diet planning, nutritional guidance, and wellness coaching',
                    'duration': '60-90 min',
                    'price_range': '$75-$200',
                    'providers': ['Nutrition Plus', 'Healthy Living', 'Wellness Coach'],
                    'provider_details': get_providers_by_service('nutrition_counseling'),
                    'popular': False
                }
            ]
        },
        {
            'category': 'Specialty Services',
            'icon': 'fas fa-star',
            'color': 'secondary',
            'description': 'Unique and specialized personal care services',
            'services': [
                {
                    'name': 'Makeup Artist',
                    'description': 'Professional makeup application for special events',
                    'duration': '60-180 min',
                    'price_range': '$80-$300',
                    'providers': ['Glamour Studio', 'Beauty Artistry', 'Makeup Masters'],
                    'provider_details': get_providers_by_service('makeup_artist'),
                    'popular': True
                },
                {
                    'name': 'Photography',
                    'description': 'Portrait, event, and lifestyle photography sessions',
                    'duration': '60-240 min',
                    'price_range': '$150-$800',
                    'providers': ['Photo Studio Pro', 'Creative Lens', 'Memory Makers'],
                    'provider_details': get_providers_by_service('photography'),
                    'popular': True
                },
                {
                    'name': 'Life Coaching',
                    'description': 'Personal development and life guidance sessions',
                    'duration': '60-90 min',
                    'price_range': '$100-$300',
                    'providers': ['Life Solutions', 'Growth Coaching', 'Success Partners'],
                    'provider_details': get_providers_by_service('life_coaching'),
                    'popular': False
                }
            ]
        }
    ]

@app.route('/services')
def services():
    """View available services and providers"""
    current_user = get_current_user()
    services_data = get_services_data()
    return render_template('services.html', services=services_data, current_user=current_user)

@app.route('/add_appointment', methods=['POST'])
@login_required
def add_appointment():
    """Add new appointment"""
    current_user = get_current_user()
    appointment_type_key = request.form.get('type')
    date = request.form.get('date')
    time = request.form.get('time')
    duration = int(request.form.get('duration'))
    notes = request.form.get('notes', '')
    provider_id = request.form.get('provider_id')
    
    # Convert to integer if provided
    provider_id = int(provider_id) if provider_id else None
    
    # Convert key to display name (e.g., "hair" -> "Hair Salon")
    appointment_type = scheduler.appointment_types.get(appointment_type_key, appointment_type_key)
    
    if scheduler.add_appointment(appointment_type, date, time, duration, notes, 
                                 user_id=current_user['id'], provider_id=provider_id):
        flash('Appointment request submitted! Waiting for provider confirmation.', 'success')
    else:
        flash('Failed to schedule appointment. Time slot may be unavailable.', 'error')
    
    return redirect(url_for('appointments'))

@app.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    if scheduler.cancel_appointment(appointment_id):
        flash('Appointment cancelled successfully!', 'success')
    else:
        flash('Appointment not found.', 'error')
    
    return redirect(url_for('appointments'))

@app.route('/api/appointments')
def api_appointments():
    """API endpoint for appointments"""
    date = request.args.get('date')
    appointments = scheduler.get_appointments(date)
    return jsonify(appointments)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for customers and providers"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')
        
        user = user_manager.authenticate(username, password)
        if user:
            session.permanent = True  # Make session persistent
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user.get('role', 'consumer')
            
            name = user.get('name', user['username'])
            flash(f'Welcome back, {name}!', 'success')
            
            # Redirect based on role
            if user.get('role') == 'provider':
                return redirect(url_for('provider_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page for customers and providers"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'consumer')
        
        # Basic validation
        if not username or not password or not name or not email:
            flash('Username, name, email, and password are required.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if len(password) < 4:
            flash('Password must be at least 4 characters long.', 'error')
            return render_template('register.html')
        
        # Provider-specific validation and fields
        provider_data = {}
        if role == 'provider':
            business_name = request.form.get('business_name', '').strip()
            business_description = request.form.get('business_description', '').strip()
            service_category = request.form.get('service_category', '').strip()
            services_offered = request.form.get('services_offered', '').strip()
            address = request.form.get('address', '').strip()
            
            if not business_name:
                flash('Business name is required for service providers.', 'error')
                return render_template('register.html')
            
            provider_data = {
                'business_name': business_name,
                'business_description': business_description,
                'service_category': service_category,
                'services_offered': services_offered,
                'address': address
            }
        
        # Create user
        if user_manager.create_user(username, password, email, role, name=name, phone=phone, **provider_data):
            if role == 'provider':
                flash('Provider account created successfully! Please log in to access your dashboard.', 'success')
            else:
                flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists.', 'error')
    
    return render_template('register.html')

@app.route('/providers/hair-salon')
def hair_providers():
    """View hair salon providers"""
    current_user = get_current_user()
    all_providers = [user for user in user_manager.users if user.get('role') == 'provider']
    hair_providers = []
    for provider in all_providers:
        if provider.get('service_category') == 'hair_salon':
            provider_data = {k: v for k, v in provider.items() if k != 'password'}
            provider_data['average_rating'] = review_manager.get_average_rating(provider['id'])
            provider_data['total_reviews'] = len(review_manager.get_provider_reviews(provider['id']))
            hair_providers.append(provider_data)
    return render_template('hair_providers.html', providers=hair_providers, current_user=current_user)

@app.route('/providers/nail-salon')
def nail_providers():
    """View nail salon providers"""
    current_user = get_current_user()
    all_providers = [user for user in user_manager.users if user.get('role') == 'provider']
    nail_providers = [
        {k: v for k, v in provider.items() if k != 'password'}
        for provider in all_providers
        if provider.get('service_category') == 'nail_salon'
    ]
    return render_template('nail_providers.html', providers=nail_providers, current_user=current_user)

@app.route('/providers/massage-therapy')
def massage_providers():
    """View massage therapy providers"""
    current_user = get_current_user()
    all_providers = [user for user in user_manager.users if user.get('role') == 'provider']
    massage_providers = [
        {k: v for k, v in provider.items() if k != 'password'}
        for provider in all_providers
        if provider.get('service_category') == 'massage_therapy'
    ]
    return render_template('massage_providers.html', providers=massage_providers, current_user=current_user)

@app.route('/providers/spa-treatment')
def spa_providers():
    """View spa treatment providers"""
    current_user = get_current_user()
    all_providers = [user for user in user_manager.users if user.get('role') == 'provider']
    spa_providers = [
        {k: v for k, v in provider.items() if k != 'password'}
        for provider in all_providers
        if provider.get('service_category') == 'spa_treatment'
    ]
    return render_template('spa_providers.html', providers=spa_providers, current_user=current_user)

@app.route('/providers/personal-training')
def training_providers():
    """View personal training providers"""
    current_user = get_current_user()
    all_providers = [user for user in user_manager.users if user.get('role') == 'provider']
    training_providers = [
        {k: v for k, v in provider.items() if k != 'password'}
        for provider in all_providers
        if provider.get('service_category') == 'personal_training'
    ]
    return render_template('training_providers.html', providers=training_providers, current_user=current_user)

@app.route('/providers/yoga-classes')
def yoga_providers():
    """View yoga classes providers"""
    current_user = get_current_user()
    all_providers = [user for user in user_manager.users if user.get('role') == 'provider']
    yoga_providers = [
        {k: v for k, v in provider.items() if k != 'password'}
        for provider in all_providers
        if provider.get('service_category') == 'yoga_classes'
    ]
    return render_template('yoga_providers.html', providers=yoga_providers, current_user=current_user)

@app.route('/providers/eyebrow-eyelash')
def eyebrow_providers():
    """View eyebrow & eyelash providers"""
    current_user = get_current_user()
    all_providers = [user for user in user_manager.users if user.get('role') == 'provider']
    eyebrow_providers = [
        {k: v for k, v in provider.items() if k != 'password'}
        for provider in all_providers
        if provider.get('service_category') == 'eyebrow_eyelash'
    ]
    return render_template('eyebrow_providers.html', providers=eyebrow_providers, current_user=current_user)

@app.route('/providers/aromatherapy')
def aromatherapy_providers():
    """View aromatherapy providers"""
    current_user = get_current_user()
    all_providers = [user for user in user_manager.users if user.get('role') == 'provider']
    aromatherapy_providers = [
        {k: v for k, v in provider.items() if k != 'password'}
        for provider in all_providers
        if provider.get('service_category') == 'aromatherapy'
    ]
    return render_template('aromatherapy_providers.html', providers=aromatherapy_providers, current_user=current_user)

@app.route('/providers/pilates')
def pilates_providers():
    """View pilates providers"""
    current_user = get_current_user()
    all_providers = [user for user in user_manager.users if user.get('role') == 'provider']
    pilates_providers = [
        {k: v for k, v in provider.items() if k != 'password'}
        for provider in all_providers
        if provider.get('service_category') == 'pilates'
    ]
    return render_template('pilates_providers.html', providers=pilates_providers, current_user=current_user)

@app.route('/providers/dermatology')
def dermatology_providers():
    """View dermatology providers"""
    current_user = get_current_user()
    all_providers = [user for user in user_manager.users if user.get('role') == 'provider']
    dermatology_providers = [
        {k: v for k, v in provider.items() if k != 'password'}
        for provider in all_providers
        if provider.get('service_category') == 'dermatology'
    ]
    return render_template('dermatology_providers.html', providers=dermatology_providers, current_user=current_user)

@app.route('/providers/physical-therapy')
def physical_therapy_providers():
    """View physical therapy providers"""
    current_user = get_current_user()
    all_providers = [user for user in user_manager.users if user.get('role') == 'provider']
    physical_therapy_providers = [
        {k: v for k, v in provider.items() if k != 'password'}
        for provider in all_providers
        if provider.get('service_category') == 'physical_therapy'
    ]
    return render_template('physical_therapy_providers.html', providers=physical_therapy_providers, current_user=current_user)

@app.route('/providers/nutrition-consulting')
def nutrition_providers():
    """View nutrition consulting providers"""
    current_user = get_current_user()
    all_providers = [user for user in user_manager.users if user.get('role') == 'provider']
    nutrition_providers = [
        {k: v for k, v in provider.items() if k != 'password'}
        for provider in all_providers
        if provider.get('service_category') == 'nutrition_counseling'
    ]
    return render_template('nutrition_providers.html', providers=nutrition_providers, current_user=current_user)

@app.route('/providers/makeup-artist')
def makeup_providers():
    """View makeup artist providers"""
    current_user = get_current_user()
    all_providers = [user for user in user_manager.users if user.get('role') == 'provider']
    makeup_providers = [
        {k: v for k, v in provider.items() if k != 'password'}
        for provider in all_providers
        if provider.get('service_category') == 'makeup_artist'
    ]
    return render_template('makeup_providers.html', providers=makeup_providers, current_user=current_user)

@app.route('/providers/photography')
def photography_providers():
    """View photography providers"""
    current_user = get_current_user()
    all_providers = [user for user in user_manager.users if user.get('role') == 'provider']
    photography_providers = [
        {k: v for k, v in provider.items() if k != 'password'}
        for provider in all_providers
        if provider.get('service_category') == 'photography'
    ]
    return render_template('photography_providers.html', providers=photography_providers, current_user=current_user)

@app.route('/providers/life-coaching')
def lifecoaching_providers():
    """View life coaching providers"""
    current_user = get_current_user()
    all_providers = [user for user in user_manager.users if user.get('role') == 'provider']
    lifecoaching_providers = [
        {k: v for k, v in provider.items() if k != 'password'}
        for provider in all_providers
        if provider.get('service_category') == 'life_coaching'
    ]
    return render_template('lifecoaching_providers.html', providers=lifecoaching_providers, current_user=current_user)

@app.route('/provider/dashboard')
@login_required
def provider_dashboard():
    """Provider dashboard - manage business and bookings"""
    current_user = get_current_user()
    
    # Check if user is a provider
    if current_user.get('role') != 'provider':
        flash('Access denied. Provider account required.', 'error')
        return redirect(url_for('index'))
    
    # Get bookings for this provider
    all_appointments = scheduler.get_appointments()
    provider_bookings = [apt for apt in all_appointments if apt.get('provider_id') == current_user['id']]
    
    # Separate pending, confirmed, and completed bookings
    pending_bookings = [apt for apt in provider_bookings if apt.get('status') == 'pending']
    confirmed_bookings = [apt for apt in provider_bookings if apt.get('status') == 'confirmed']
    completed_bookings = [apt for apt in provider_bookings if apt.get('status') == 'completed']
    
    # Calculate statistics
    total_bookings = len(confirmed_bookings) + len(completed_bookings)
    upcoming_bookings = len([apt for apt in confirmed_bookings if apt['datetime'] > datetime.now()])
    pending_count = len(pending_bookings)
    completed_count = len(completed_bookings)
    
    # Get customer names for pending appointments
    pending_with_customers = []
    for apt in pending_bookings:
        customer = user_manager.get_user_by_id(apt.get('user_id'))
        pending_with_customers.append({
            'id': apt['id'],
            'type': apt['type'],
            'datetime': apt['datetime'],
            'duration': apt['duration'],
            'notes': apt.get('notes', ''),
            'customer_name': customer.get('name', 'Unknown') if customer else 'Unknown',
            'customer_phone': customer.get('phone', '') if customer else ''
        })
    
    # Get customer names for confirmed appointments
    confirmed_with_customers = []
    for apt in confirmed_bookings:
        customer = user_manager.get_user_by_id(apt.get('user_id'))
        confirmed_with_customers.append({
            'id': apt['id'],
            'type': apt['type'],
            'datetime': apt['datetime'],
            'duration': apt['duration'],
            'notes': apt.get('notes', ''),
            'customer_name': customer.get('name', 'Unknown') if customer else 'Unknown',
            'customer_phone': customer.get('phone', '') if customer else ''
        })
    
    # Get customer names for completed appointments
    completed_with_customers = []
    for apt in completed_bookings:
        customer = user_manager.get_user_by_id(apt.get('user_id'))
        completed_with_customers.append({
            'id': apt['id'],
            'type': apt['type'],
            'datetime': apt['datetime'],
            'duration': apt['duration'],
            'notes': apt.get('notes', ''),
            'completed_at': datetime.fromisoformat(apt.get('completed_at')) if apt.get('completed_at') else None,
            'customer_name': customer.get('name', 'Unknown') if customer else 'Unknown',
            'customer_phone': customer.get('phone', '') if customer else ''
        })
    
    # Recent confirmed bookings (last 5)
    recent_bookings = sorted(confirmed_bookings, key=lambda x: x['datetime'], reverse=True)[:5]
    
    # Prepare all bookings for calendar (convert datetime to ISO string for JSON)
    all_bookings_json = []
    for booking in confirmed_bookings:
        all_bookings_json.append({
            'id': booking['id'],
            'type': booking['type'],
            'datetime': booking['datetime'].isoformat(),
            'duration': booking['duration'],
            'notes': booking.get('notes', '')
        })
    
    return render_template('provider_dashboard.html',
                         current_user=current_user,
                         total_bookings=total_bookings,
                         upcoming_bookings=upcoming_bookings,
                         pending_count=pending_count,
                         completed_count=completed_count,
                         pending_bookings=pending_with_customers,
                         confirmed_bookings=confirmed_with_customers,
                         completed_bookings=completed_with_customers,
                         bookings=all_bookings_json)

@app.route('/appointment/<int:appointment_id>/accept', methods=['POST'])
@login_required
def accept_appointment(appointment_id):
    """Provider accepts an appointment"""
    current_user = get_current_user()
    
    if current_user.get('role') != 'provider':
        return jsonify({'success': False, 'error': 'Only providers can accept appointments'}), 403
    
    try:
        appointment = next((apt for apt in scheduler.appointments if apt['id'] == appointment_id), None)
        
        if not appointment:
            return jsonify({'success': False, 'error': 'Appointment not found'}), 404
        
        if appointment.get('provider_id') != current_user['id']:
            return jsonify({'success': False, 'error': 'Not your appointment'}), 403
        
        appointment['status'] = 'confirmed'
        scheduler.save_appointments()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/appointment/<int:appointment_id>/decline', methods=['POST'])
@login_required
def decline_appointment(appointment_id):
    """Provider declines an appointment"""
    current_user = get_current_user()
    
    if current_user.get('role') != 'provider':
        return jsonify({'success': False, 'error': 'Only providers can decline appointments'}), 403
    
    try:
        appointment = next((apt for apt in scheduler.appointments if apt['id'] == appointment_id), None)
        
        if not appointment:
            return jsonify({'success': False, 'error': 'Appointment not found'}), 404
        
        if appointment.get('provider_id') != current_user['id']:
            return jsonify({'success': False, 'error': 'Not your appointment'}), 403
        
        appointment['status'] = 'declined'
        scheduler.save_appointments()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/appointment/<int:appointment_id>/complete', methods=['POST'])
@login_required
def complete_appointment(appointment_id):
    """Mark an appointment as completed"""
    current_user = get_current_user()
    
    if current_user.get('role') != 'provider':
        return jsonify({'success': False, 'error': 'Only providers can complete appointments'}), 403
    
    try:
        appointment = next((apt for apt in scheduler.appointments if apt['id'] == appointment_id), None)
        
        if not appointment:
            return jsonify({'success': False, 'error': 'Appointment not found'}), 404
        
        if appointment.get('provider_id') != current_user['id']:
            return jsonify({'success': False, 'error': 'Not your appointment'}), 403
        
        if appointment.get('status') != 'confirmed':
            return jsonify({'success': False, 'error': 'Only confirmed appointments can be completed'}), 400
        
        # Check if appointment time has been reached
        appointment_datetime = appointment.get('datetime')
        if appointment_datetime:
            if isinstance(appointment_datetime, str):
                appointment_datetime = datetime.fromisoformat(appointment_datetime.replace('Z', '+00:00'))
            
            current_time = datetime.now()
            if current_time < appointment_datetime:
                return jsonify({'success': False, 'error': 'Cannot complete appointment before its scheduled time'}), 400
        
        appointment['status'] = 'completed'
        appointment['completed_at'] = datetime.now().isoformat()
        scheduler.save_appointments()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/profile/availability/update', methods=['POST'])
@login_required
def update_availability():
    """Update provider availability"""
    current_user = get_current_user()
    
    if current_user.get('role') != 'provider':
        return jsonify({'success': False, 'error': 'Only providers can set availability'}), 403
    
    try:
        availability_data = request.get_json()
        
        # Get user from database
        user = next((u for u in user_manager.users if u['id'] == current_user['id']), None)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Update availability
        user['availability'] = availability_data
        user_manager.save_users()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/provider/<int:provider_id>/reviews')
def provider_reviews(provider_id):
    """Get provider reviews as JSON"""
    reviews = review_manager.get_provider_reviews(provider_id)
    average_rating = review_manager.get_average_rating(provider_id)
    
    # Get customer names for reviews
    reviews_with_names = []
    for review in reviews:
        customer = user_manager.get_user_by_id(review['customer_id'])
        reviews_with_names.append({
            'id': review['id'],
            'customer_name': customer.get('name', 'Anonymous') if customer else 'Anonymous',
            'rating': review['rating'],
            'comment': review['comment'],
            'created_at': review['created_at'].strftime('%B %d, %Y')
        })
    
    return jsonify({
        'reviews': reviews_with_names,
        'average_rating': round(average_rating, 1), 
        'total_reviews': len(reviews)
    })

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

