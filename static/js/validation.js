/*
 * Form Validation JavaScript
 * Client-side validation for forms
 */

// ===== Password Strength Checker =====
class PasswordStrength {
    constructor(passwordInput, strengthMeter) {
        this.passwordInput = passwordInput;
        this.strengthMeter = strengthMeter;
        this.init();
    }

    init() {
        this.passwordInput.addEventListener('input', () => this.checkStrength());
    }

    checkStrength() {
        const password = this.passwordInput.value;
        const strength = this.calculateStrength(password);
        this.updateUI(strength);
    }

    calculateStrength(password) {
        let strength = 0;
        
        // Length check
        if (password.length >= 6) strength++;
        if (password.length >= 10) strength++;
        
        // Character checks
        if (/[A-Z]/.test(password)) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^A-Za-z0-9]/.test(password)) strength++;
        
        return Math.min(strength, 5);
    }

    updateUI(strength) {
        const labels = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'];
        const colors = ['#dc3545', '#ffc107', '#fd7e14', '#28a745', '#20c997'];
        
        this.strengthMeter.style.width = `${strength * 20}%`;
        this.strengthMeter.style.backgroundColor = colors[strength - 1] || colors[0];
        
        if (this.strengthMeter.nextElementSibling) {
            this.strengthMeter.nextElementSibling.textContent = labels[strength - 1] || 'Very Weak';
        }
    }
}

// ===== Form Validators =====
const Validators = {
    required: (value) => {
        return value.trim() !== '';
    },
    
    minLength: (value, length) => {
        return value.length >= length;
    },
    
    maxLength: (value, length) => {
        return value.length <= length;
    },
    
    email: (value) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(value);
    },
    
    username: (value) => {
        const usernameRegex = /^[a-zA-Z0-9_]+$/;
        return usernameRegex.test(value) && value.length >= 3;
    },
    
    password: (value) => {
        return value.length >= 6;
    },
    
    matching: (value1, value2) => {
        return value1 === value2;
    },
    
    phone: (value) => {
        const phoneRegex = /^[0-9+\-\s()]+$/;
        return phoneRegex.test(value) && value.length >= 10;
    },
    
    date: (value) => {
        const date = new Date(value);
        return date instanceof Date && !isNaN(date);
    },
    
    futureDate: (value) => {
        const date = new Date(value);
        return date instanceof Date && !isNaN(date) && date > new Date();
    }
};

// ===== Initialize Password Strength =====
document.addEventListener('DOMContentLoaded', function() {
    const passwordInputs = document.querySelectorAll('input[type="password"][name="password"]');
    passwordInputs.forEach(input => {
        const strengthMeter = input.parentElement.querySelector('.password-strength');
        if (strengthMeter) {
            new PasswordStrength(input, strengthMeter);
        }
    });
});

// ===== Custom Validation Rules =====
const CustomValidators = {
    // Username validation
    username: {
        validate: (value) => {
            if (!value) return 'Username is required';
            if (value.length < 3) return 'Username must be at least 3 characters';
            if (value.length > 80) return 'Username must be less than 80 characters';
            if (!/^[a-zA-Z0-9_]+$/.test(value)) return 'Username can only contain letters, numbers, and underscores';
            return null;
        }
    },
    
    // Email validation
    email: {
        validate: (value) => {
            if (!value) return 'Email is required';
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return 'Please enter a valid email address';
            if (value.length > 120) return 'Email must be less than 120 characters';
            return null;
        }
    },
    
    // Password validation
    password: {
        validate: (value) => {
            if (!value) return 'Password is required';
            if (value.length < 6) return 'Password must be at least 6 characters';
            return null;
        }
    },
    
    // Event title validation
    eventTitle: {
        validate: (value) => {
            if (!value) return 'Event title is required';
            if (value.length < 5) return 'Title must be at least 5 characters';
            if (value.length > 200) return 'Title must be less than 200 characters';
            return null;
        }
    },
    
    // Event description validation
    eventDescription: {
        validate: (value) => {
            if (!value) return 'Description is required';
            if (value.length < 20) return 'Description must be at least 20 characters';
            return null;
        }
    },
    
    // Capacity validation
    capacity: {
        validate: (value) => {
            if (!value) return 'Capacity is required';
            const num = parseInt(value);
            if (isNaN(num) || num < 1) return 'Capacity must be at least 1';
            if (num > 10000) return 'Capacity cannot exceed 10,000';
            return null;
        }
    }
};

// ===== Real-time Validation =====
class FormValidator {
    constructor(formElement) {
        this.form = formElement;
        this.fields = {};
        this.init();
    }

    init() {
        // Find all form fields with validation rules
        const inputs = this.form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            if (input.name && CustomValidators[input.name]) {
                this.fields[input.name] = {
                    element: input,
                    validator: CustomValidators[input.name],
                    errorElement: null
                };
                
                // Create error element
                this.createErrorElement(input);
                
                // Add input event listener
                input.addEventListener('input', () => this.validateField(input.name));
                input.addEventListener('blur', () => this.validateField(input.name));
            }
        });
    }

    createErrorElement(input) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.style.display = 'none';
        input.parentNode.appendChild(errorDiv);
        input.classList.add('is-invalid');
    }

    validateField(fieldName) {
        const field = this.fields[fieldName];
        const value = field.element.value;
        const error = field.validator.validate(value);
        
        if (error) {
            this.showError(fieldName, error);
            return false;
        } else {
            this.clearError(fieldName);
            return true;
        }
    }

    showError(fieldName, message) {
        const field = this.fields[fieldName];
        field.element.classList.add('is-invalid');
        field.element.classList.remove('is-valid');
        
        const errorDiv = field.element.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
    }

    clearError(fieldName) {
        const field = this.fields[fieldName];
        field.element.classList.remove('is-invalid');
        field.element.classList.add('is-valid');
        
        const errorDiv = field.element.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }

    validateAll() {
        let isValid = true;
        Object.keys(this.fields).forEach(fieldName => {
            if (!this.validateField(fieldName)) {
                isValid = false;
            }
        });
        return isValid;
    }
}

// ===== Initialize Form Validators =====
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[data-validate="true"]');
    forms.forEach(form => {
        new FormValidator(form);
    });
});

// ===== Confirm Dialog Helper =====
function confirmAction(message = 'Are you sure?') {
    return confirm(message);
}

// ===== Auto-hide flash messages =====
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 300);
        });
    }, 5000);
});
