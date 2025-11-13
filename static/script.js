// Modern JavaScript for Appointment Scheduler

document.addEventListener('DOMContentLoaded', function() {
    // Initialize modern features
    initializeAnimations();
    initializeFormValidation();
    initializeThemeToggle();
    initializeScrollEffects();
    
    // Set minimum date to today for date inputs
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    dateInputs.forEach(input => {
        input.min = today;
    });
    
    // Set default time to next hour
    const timeInput = document.getElementById('time');
    if (timeInput) {
        const now = new Date();
        const nextHour = new Date(now.getTime() + 60 * 60 * 1000);
        timeInput.value = nextHour.toTimeString().slice(0, 5);
    }
    
    // Enhanced auto-hide alerts with smooth animation
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-20px)';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 500);
            }
        }, 5000);
    });
    
    // Add parallax effect to hero section
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const parallax = heroSection.querySelector('.container');
            const speed = scrolled * 0.5;
            parallax.style.transform = `translateY(${speed}px)`;
        });
    }
});

// Animation initialization
function initializeAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe all cards and sections
    document.querySelectorAll('.card, .hero-section, .service-category').forEach(el => {
        observer.observe(el);
    });
    
    // Add staggered animation to cards
    document.querySelectorAll('.hover-card').forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
}

// Enhanced form validation with modern UI feedback
function initializeFormValidation() {
    const appointmentForm = document.getElementById('appointmentForm');
    if (appointmentForm) {
        appointmentForm.addEventListener('submit', function(e) {
            const date = document.getElementById('date').value;
            const time = document.getElementById('time').value;
            const selectedDate = new Date(date + 'T' + time);
            const now = new Date();
            
            if (selectedDate <= now) {
                e.preventDefault();
                showNotification('Please select a future date and time.', 'error');
                return false;
            }
        });
        
        // Real-time validation feedback
        const inputs = appointmentForm.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
    }
}

// Theme toggle functionality
function initializeThemeToggle() {
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('theme-icon');
    
    if (savedTheme === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
        if (themeIcon) themeIcon.className = 'fas fa-sun';
    } else {
        document.body.setAttribute('data-theme', 'light');
        if (themeIcon) themeIcon.className = 'fas fa-moon';
    }
}

// Scroll effects and parallax
function initializeScrollEffects() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            // Skip if href is just "#" (not a valid selector)
            if (href === '#' || !href || href.length <= 1) {
                return; // Let default behavior happen or let other handlers process it
            }
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.style.background = 'rgba(255, 255, 255, 0.95)';
                navbar.style.backdropFilter = 'blur(20px)';
                navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
            } else {
                navbar.style.background = 'rgba(255, 255, 255, 0.1)';
                navbar.style.backdropFilter = 'blur(20px)';
                navbar.style.boxShadow = 'none';
            }
        });
    }
}

// Enhanced notification system
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    `;
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.transition = 'all 0.5s ease-out';
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 500);
        }
    }, duration);
}

// Enhanced field validation
function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name || field.id;
    
    // Remove existing error styling
    clearFieldError(field);
    
    // Basic validation
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, `${fieldName} is required`);
        return false;
    }
    
    // Date validation
    if (field.type === 'date' && value) {
        const selectedDate = new Date(value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        if (selectedDate < today) {
            showFieldError(field, 'Please select a future date');
            return false;
        }
    }
    
    // Time validation
    if (field.type === 'time' && value) {
        const dateInput = document.getElementById('date');
        if (dateInput && dateInput.value) {
            const selectedDateTime = new Date(`${dateInput.value}T${value}`);
            const now = new Date();
            
            if (selectedDateTime <= now) {
                showFieldError(field, 'Please select a future time');
                return false;
            }
        }
    }
    
    return true;
}

function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    let errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        field.parentNode.appendChild(errorDiv);
    }
    errorDiv.textContent = message;
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Enhanced loading states
function addLoadingState(button) {
    const originalText = button.innerHTML;
    const originalClasses = button.className;
    
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Loading...';
    button.className = originalClasses + ' loading';
    button.disabled = true;
    
    return function removeLoadingState() {
        button.innerHTML = originalText;
        button.className = originalClasses;
        button.disabled = false;
    };
}

// Filter appointments by date with smooth animation
function filterByDate() {
    const dateFilter = document.getElementById('dateFilter');
    const selectedDate = dateFilter.value;
    
    // Add loading state
    const loadingButton = addLoadingState(event.target);
    
    setTimeout(() => {
        if (selectedDate) {
            window.location.href = `/appointments/${selectedDate}`;
        } else {
            window.location.href = '/appointments';
        }
        loadingButton();
    }, 500);
}

// Enhanced appointment cancellation with modern modal
function cancelAppointment(appointmentId) {
    // Create dynamic modal
    const modalHtml = `
        <div class="modal fade" id="cancelModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content glass-effect">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-exclamation-triangle me-2 text-warning"></i>
                            Cancel Appointment
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <i class="fas fa-calendar-times fa-4x text-danger mb-3"></i>
                        <h5>Are you sure you want to cancel this appointment?</h5>
                        <p class="text-muted">This action cannot be undone.</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Keep Appointment</button>
                        <button type="button" class="btn btn-danger" id="confirmCancel">
                            <i class="fas fa-trash me-1"></i>Cancel Appointment
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if present
    const existingModal = document.getElementById('cancelModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add new modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    const modal = new bootstrap.Modal(document.getElementById('cancelModal'));
    modal.show();
    
    document.getElementById('confirmCancel').onclick = function() {
        const loadingButton = addLoadingState(this);
        
        // Create a form to submit the cancellation
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/cancel_appointment/${appointmentId}`;
        form.style.display = 'none';
        
        document.body.appendChild(form);
        form.submit();
    };
}

// Enhanced utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatTime(timeString) {
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
}

// Enhanced filter by status with animations
function filterByStatus(status) {
    const rows = document.querySelectorAll('.appointment-row');
    const buttons = document.querySelectorAll('[onclick^="filterByStatus"]');
    
    // Update button states with smooth transition
    buttons.forEach(btn => {
        btn.style.transition = 'all 0.3s ease';
        btn.classList.remove('btn-light');
        btn.classList.add('btn-outline-light');
    });
    
    // Highlight active button
    event.target.classList.remove('btn-outline-light');
    event.target.classList.add('btn-light');
    
    // Filter rows with animation
    rows.forEach((row, index) => {
        const shouldShow = status === 'all' || row.dataset.status === status;
        
        if (shouldShow) {
            row.style.display = '';
            row.style.animation = `fadeInUp 0.5s ease ${index * 0.1}s both`;
        } else {
            row.style.animation = 'fadeOut 0.3s ease both';
            setTimeout(() => {
                row.style.display = 'none';
            }, 300);
        }
    });
}

// Enhanced profile functions
function editProfile() {
    const modal = new bootstrap.Modal(document.getElementById('editProfileModal'));
    modal.show();
}

function saveProfile() {
    const loadingButton = addLoadingState(event.target);
    
    setTimeout(() => {
        // In a real app, this would save to the backend
        const name = document.getElementById('editName').value;
        const email = document.getElementById('editEmail').value;
        const phone = document.getElementById('editPhone').value;
        const favoriteService = document.getElementById('editFavoriteService').value;
        
        showNotification('Profile updated successfully!', 'success');
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('editProfileModal'));
        modal.hide();
        
        loadingButton();
    }, 1000);
}

// Enhanced promo code copying
function copyPromoCode(code) {
    navigator.clipboard.writeText(code).then(function() {
        const button = event.target.closest('button');
        const originalText = button.innerHTML;
        
        button.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
        button.classList.remove('btn-outline-primary');
        button.classList.add('btn-success');
        
        showNotification('Promo code copied to clipboard!', 'success', 2000);
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-primary');
        }, 2000);
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
        showNotification('Could not copy promo code. Please copy manually: ' + code, 'error');
    });
}

// Enhanced services page functions
function bookService(serviceName, category) {
    document.getElementById('bookServiceName').textContent = serviceName;
    const modal = new bootstrap.Modal(document.getElementById('bookServiceModal'));
    modal.show();
}

function proceedToBooking() {
    const loadingButton = addLoadingState(event.target);
    
    setTimeout(() => {
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('bookServiceModal'));
        modal.hide();
        
        // Redirect to schedule page
        window.location.href = '/schedule';
        loadingButton();
    }, 500);
}

// Enhanced provider viewing - shows registered providers by service type
function viewProviders(serviceName, providers) {
    document.getElementById('modalServiceName').textContent = serviceName;
    const providersList = document.getElementById('providersList');
    
    // Clear previous content
    providersList.innerHTML = '';
    
    // Check if there are any providers
    if (!providers || providers.length === 0) {
        providersList.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="fas fa-users-slash fa-4x text-muted mb-3"></i>
                <h5 class="text-muted">No Providers Available</h5>
                <p class="text-muted">There are currently no service providers registered for ${serviceName}.</p>
                <p class="text-muted">Be the first to join as a provider!</p>
                <a href="/register" class="btn btn-primary mt-2">
                    <i class="fas fa-user-plus me-1"></i>Register as Provider
                </a>
            </div>
        `;
    } else {
        // Add provider cards with animation - handle both object and string providers
        providers.forEach((provider, index) => {
            const providerCard = document.createElement('div');
            providerCard.className = 'col-md-6';
            providerCard.style.animation = `fadeInUp 0.5s ease ${index * 0.1}s both`;
            
            // Check if provider is an object or just a string
            const isObject = typeof provider === 'object' && provider !== null;
            const providerName = isObject ? provider.name : provider;
            const providerDescription = isObject ? provider.description : '';
            const providerAddress = isObject ? provider.address : '';
            const providerUsername = isObject ? provider.username : '';
            const rating = isObject ? (provider.rating || 4.5) : 4.5;
            
            // Generate star rating
            const fullStars = Math.floor(rating);
            const halfStar = rating % 1 >= 0.5 ? 1 : 0;
            const emptyStars = 5 - fullStars - halfStar;
            
            let starsHTML = '';
            for (let i = 0; i < fullStars; i++) starsHTML += '<i class="fas fa-star"></i>';
            if (halfStar) starsHTML += '<i class="fas fa-star-half-alt"></i>';
            for (let i = 0; i < emptyStars; i++) starsHTML += '<i class="far fa-star"></i>';
            
            providerCard.innerHTML = `
                <div class="card h-100 hover-card">
                    <div class="card-body text-center">
                        <div class="service-icon mb-3">
                            <i class="fas fa-store fa-3x text-primary"></i>
                        </div>
                        <h6 class="card-title">${providerName}</h6>
                        <div class="text-warning mb-2" style="font-size: 0.9rem;">
                            ${starsHTML}
                            <small class="text-muted ms-1">(${rating.toFixed(1)})</small>
                        </div>
                        ${providerDescription ? `<p class="text-muted small mb-2">${providerDescription}</p>` : ''}
                        ${providerAddress ? `
                            <p class="text-muted small mb-2">
                                <i class="fas fa-map-marker-alt me-1"></i>${providerAddress}
                            </p>
                        ` : ''}
                        <button class="btn btn-primary btn-sm" onclick="bookWithProvider('${providerName}', '${serviceName}')">
                            <i class="fas fa-calendar-plus me-1"></i>Book with ${providerName}
                        </button>
                    </div>
                </div>
            `;
            providersList.appendChild(providerCard);
        });
    }
    
    const modal = new bootstrap.Modal(document.getElementById('providersModal'));
    modal.show();
}

function bookWithProvider(providerName, serviceName) {
    const loadingButton = addLoadingState(event.target);
    
    setTimeout(() => {
        // Close providers modal
        const providersModal = bootstrap.Modal.getInstance(document.getElementById('providersModal'));
        providersModal.hide();
        
        showNotification(`Booking ${serviceName} with ${providerName}...`, 'info');
        
        // Redirect to schedule page
        window.location.href = '/schedule';
        loadingButton();
    }, 500);
}

// Enhanced search and filter with debouncing
let searchTimeout;
function filterServices() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(performFilter, 300);
}

function performFilter() {
    const searchInput = document.getElementById('serviceSearch');
    const categoryFilter = document.getElementById('categoryFilter');
    const serviceCards = document.querySelectorAll('.service-card');
    const noResults = document.getElementById('noResults');
    
    if (!searchInput || !categoryFilter || !serviceCards.length) {
        return;
    }
    
    const searchTerm = searchInput.value.toLowerCase().trim();
    const selectedCategory = categoryFilter.value;
    
    let visibleCount = 0;
    const categoryMap = new Map();
    
    serviceCards.forEach((card) => {
        const serviceName = card.dataset.name || '';
        const category = card.dataset.category || '';
        
        // Track category containers
        if (!categoryMap.has(category)) {
            categoryMap.set(category, { visible: false, element: card.closest('.service-category') });
        }
        
        let showCard = true;
        
        // Search filter
        if (searchTerm && !serviceName.includes(searchTerm)) {
            showCard = false;
        }
        
        // Category filter
        if (selectedCategory && category !== selectedCategory) {
            showCard = false;
        }
        
        if (showCard) {
            card.style.display = '';
            card.style.animation = 'fadeInUp 0.5s ease both';
            visibleCount++;
            categoryMap.get(category).visible = true;
        } else {
            card.style.animation = 'fadeOut 0.3s ease both';
            setTimeout(() => {
                card.style.display = 'none';
            }, 300);
        }
    });
    
    // Hide/show category sections based on visibility
    categoryMap.forEach(({ visible, element }) => {
        if (element) {
            element.style.display = visible ? '' : 'none';
        }
    });
    
    // Show/hide no results message
    if (noResults) {
        if (visibleCount === 0) {
            noResults.style.display = 'block';
            noResults.style.animation = 'fadeInUp 0.5s ease both';
        } else {
            noResults.style.animation = 'fadeOut 0.3s ease both';
            setTimeout(() => {
                noResults.style.display = 'none';
            }, 300);
        }
    }
}

function clearFilters() {
    const searchInput = document.getElementById('serviceSearch');
    const categoryFilter = document.getElementById('categoryFilter');
    
    if (searchInput) searchInput.value = '';
    if (categoryFilter) categoryFilter.value = '';
    
    // Show all cards with animation
    document.querySelectorAll('.service-card').forEach((card, index) => {
        card.style.display = '';
        card.style.animation = `fadeInUp 0.5s ease ${index * 0.05}s both`;
    });
    
    // Show all category sections
    document.querySelectorAll('.service-category').forEach((category) => {
        category.style.display = '';
    });
    
    // Hide no results message
    const noResults = document.getElementById('noResults');
    if (noResults) {
        noResults.style.display = 'none';
    }
}

// Enhanced help page functions
function startChat(topicId, topicTitle) {
    const modal = new bootstrap.Modal(document.getElementById('chatModal'));
    modal.show();
    
    // Add initial message based on topic
    const chatMessages = document.getElementById('chatMessages');
    const topicMessages = {
        'refund': 'I can help you with refund requests. Please provide your appointment ID and reason for the refund.',
        'reschedule': 'I can help you reschedule your appointment. What date and time would work better for you?',
        'technical': 'I can help you with technical issues. Please describe what problem you\'re experiencing.',
        'billing': 'I can help you with billing questions. What specific billing issue can I assist you with?',
        'general': 'I\'m here to help with any general questions you might have. What can I assist you with?'
    };
    
    // Clear previous messages except the initial bot message
    const initialMessage = chatMessages.querySelector('.bot-message');
    chatMessages.innerHTML = '';
    chatMessages.appendChild(initialMessage);
    
    // Add topic-specific message
    setTimeout(() => {
        addBotMessage(topicMessages[topicId] || 'How can I help you today?');
    }, 500);
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (message) {
        addUserMessage(message);
        input.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        // Simulate bot response
        setTimeout(() => {
            hideTypingIndicator();
            const responses = [
                'I understand your concern. Let me help you with that.',
                'Thank you for providing that information. I\'m looking into this for you.',
                'I can definitely help you with that. Let me check our system.',
                'That\'s a great question. Here\'s what I can tell you...',
                'I\'m sorry to hear about this issue. Let me assist you right away.',
                'I\'ve noted your request. A support representative will follow up with you shortly.'
            ];
            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            addBotMessage(randomResponse);
        }, 1000 + Math.random() * 2000);
    }
}

function addUserMessage(message) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.style.animation = 'slideInRight 0.3s ease both';
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-user"></i>
        </div>
        <div class="message-content">
            <div class="message-header">
                <strong>You</strong>
                <small class="text-muted">now</small>
            </div>
            <div class="message-text">${message}</div>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addBotMessage(message) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.style.animation = 'slideInLeft 0.3s ease both';
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="message-header">
                <strong>Support Bot</strong>
                <small class="text-muted">now</small>
            </div>
            <div class="message-text">${message}</div>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message typing-indicator';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="message-header">
                <strong>Support Bot</strong>
                <small class="text-muted">typing...</small>
            </div>
            <div class="message-text">
                <span class="typing-dots">
                    <span>.</span><span>.</span><span>.</span>
                </span>
            </div>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Add CSS animations dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes fadeOut {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-20px);
        }
    }
    
    .typing-dots span {
        animation: typing 1.4s infinite ease-in-out;
        display: inline-block;
    }
    
    .typing-dots span:nth-child(1) { animation-delay: 0s; }
    .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.5;
        }
        30% {
            transform: translateY(-10px);
            opacity: 1;
        }
    }
    
    .animate-in {
        animation: fadeInUp 0.6s ease both;
    }
`;
document.head.appendChild(style);