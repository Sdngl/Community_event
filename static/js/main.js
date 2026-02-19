/*
 * CrowdConnect - Main JavaScript
 */

// ===== DOM Ready =====
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initAlerts();
    initPasswordToggles();
    initFormValidation();
    initProgressBars();
    initTooltips();
    initMobileMenu();
});

/* ===== Alert Auto-Dismiss ===== */
function initAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            alert.classList.add('fade');
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
}

/* ===== Password Visibility Toggle ===== */
function initPasswordToggles() {
    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.closest('.input-group').querySelector('input[type="password"], input[type="text"]');
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
}

/* ===== Form Validation ===== */
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

/* ===== Progress Bars ===== */
function initProgressBars() {
    document.querySelectorAll('.progress-bar').forEach(bar => {
        const targetWidth = bar.getAttribute('data-width');
        if (targetWidth) {
            setTimeout(() => {
                bar.style.width = targetWidth;
            }, 100);
        }
    });
}

/* ===== Tooltips ===== */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/* ===== Mobile Menu ===== */
function initMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
                navbarCollapse.classList.remove('show');
            }
        });
    }
}

/* ===== Search Function ===== */
function performSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');
    
    if (searchInput && searchForm) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchForm.submit();
            }
        });
    }
}

/* ===== Event Registration ===== */
function confirmRegistration(eventId) {
    if (confirm('Are you sure you want to register for this event?')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/events/${eventId}/register`;
        document.body.appendChild(form);
        form.submit();
    }
    return false;
}

/* ===== Event Unregistration ===== */
function confirmUnregistration(eventId) {
    if (confirm('Are you sure you want to unregister from this event?')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/events/${eventId}/unregister`;
        document.body.appendChild(form);
        form.submit();
    }
    return false;
}

/* ===== Event Deletion ===== */
function confirmDelete(eventType, id) {
    const message = eventType === 'event' 
        ? 'Are you sure you want to delete this event? This action cannot be undone.'
        : 'Are you sure you want to delete this? This action cannot be undone.';
    
    if (confirm(message)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = eventType === 'event' 
            ? `/events/${id}/delete`
            : `/admin/${eventType}s/${id}/delete`;
        document.body.appendChild(form);
        form.submit();
    }
    return false;
}

/* ===== Copy to Clipboard ===== */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

/* ===== Date Formatting ===== */
function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

/* ===== Loading Spinner ===== */
function showLoading(element) {
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    spinner.id = 'loadingSpinner';
    element.appendChild(spinner);
}

function hideLoading() {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.remove();
    }
}

/* ===== AJAX Helper ===== */
async function fetchAPI(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/* ===== Flash Message Helper ===== */
function showFlashMessage(message, category = 'info') {
    const alertContainer = document.querySelector('.alert-container') || document.body;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${category} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

/* ===== Debounce Function ===== */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/* ===== Initialize Debounced Search ===== */
const debouncedSearch = debounce(function(searchTerm) {
    if (searchTerm.length >= 2) {
        // Perform search AJAX call here
        console.log('Searching for:', searchTerm);
    }
}, 300);
