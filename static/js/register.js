document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registrationForm');
    const submitBtn = document.getElementById('submitBtn');
    const messageBox = document.getElementById('messageBox');
    
    // Input fields
    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const phoneInput = document.getElementById('phone');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    
    // Error message elements
    const nameError = document.getElementById('name-error');
    const emailError = document.getElementById('email-error');
    const phoneError = document.getElementById('phone-error');
    const passwordError = document.getElementById('password-error');
    const confirmPasswordError = document.getElementById('confirm-password-error');
    
    // Real-time validation
    nameInput.addEventListener('input', function() {
        if (this.value.length > 0 && this.value.length < 2) {
            nameError.textContent = 'Name must be at least 2 characters';
        } else {
            nameError.textContent = '';
        }
    });
    
    emailInput.addEventListener('input', function() {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (this.value && !emailPattern.test(this.value)) {
            emailError.textContent = 'Please enter a valid email address';
        } else {
            emailError.textContent = '';
        }
    });
    
    phoneInput.addEventListener('input', function() {
        // Remove non-numeric characters
        this.value = this.value.replace(/[^0-9]/g, '');
        
        if (this.value.length > 0 && this.value.length !== 10) {
            phoneError.textContent = 'Phone number must be exactly 10 digits';
        } else {
            phoneError.textContent = '';
        }
    });
    
    passwordInput.addEventListener('input', function() {
        if (this.value.length > 0 && this.value.length < 6) {
            passwordError.textContent = 'Password must be at least 6 characters';
        } else {
            passwordError.textContent = '';
        }
        
        // Check confirm password match if it has value
        if (confirmPasswordInput.value) {
            checkPasswordMatch();
        }
    });
    
    confirmPasswordInput.addEventListener('input', checkPasswordMatch);
    
    function checkPasswordMatch() {
        if (confirmPasswordInput.value !== passwordInput.value) {
            confirmPasswordError.textContent = 'Passwords do not match';
        } else {
            confirmPasswordError.textContent = '';
        }
    }
    
    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Clear previous messages
        messageBox.style.display = 'none';
        messageBox.textContent = '';
        
        // Validate all fields
        if (!validateForm()) {
            return;
        }
        
        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.querySelector('.btn-text').style.display = 'none';
        submitBtn.querySelector('.btn-loader').style.display = 'inline-block';
        
        // Prepare data
        const formData = {
            name: nameInput.value.trim(),
            email: emailInput.value.trim(),
            phone: phoneInput.value.trim(),
            password: passwordInput.value
        };
        
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                showMessage(result.message, 'success');
                form.reset();
                
                // Redirect to login after 2 seconds
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                showMessage(result.message, 'error');
            }
        } catch (error) {
            showMessage('An error occurred. Please try again later.', 'error');
            console.error('Error:', error);
        } finally {
            // Re-enable submit button
            submitBtn.disabled = false;
            submitBtn.querySelector('.btn-text').style.display = 'inline-block';
            submitBtn.querySelector('.btn-loader').style.display = 'none';
        }
    });
    
    function validateForm() {
        let isValid = true;
        
        // Name validation
        if (nameInput.value.trim().length < 2) {
            nameError.textContent = 'Name must be at least 2 characters';
            isValid = false;
        }
        
        // Email validation
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(emailInput.value)) {
            emailError.textContent = 'Please enter a valid email address';
            isValid = false;
        }
        
        // Phone validation
        if (phoneInput.value.length !== 10) {
            phoneError.textContent = 'Phone number must be exactly 10 digits';
            isValid = false;
        }
        
        // Password validation
        if (passwordInput.value.length < 6) {
            passwordError.textContent = 'Password must be at least 6 characters';
            isValid = false;
        }
        
        // Confirm password validation
        if (confirmPasswordInput.value !== passwordInput.value) {
            confirmPasswordError.textContent = 'Passwords do not match';
            isValid = false;
        }
        
        return isValid;
    }
    
    function showMessage(message, type) {
        messageBox.textContent = message;
        messageBox.className = 'message-box ' + type;
        messageBox.style.display = 'block';
    }
});
