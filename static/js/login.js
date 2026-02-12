document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('loginForm');
    const submitBtn = document.getElementById('submitBtn');
    const messageBox = document.getElementById('messageBox');

    // Input fields
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    // Error message elements
    const emailError = document.getElementById('email-error');
    const passwordError = document.getElementById('password-error');

    // Real-time validation
    emailInput.addEventListener('input', function () {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (this.value && !emailPattern.test(this.value)) {
            emailError.textContent = 'Please enter a valid email address';
        } else {
            emailError.textContent = '';
        }
    });

    passwordInput.addEventListener('input', function () {
        if (this.value.length > 0) {
            passwordError.textContent = '';
        }
    });

    // Form submission
    form.addEventListener('submit', async function (e) {
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
            email: emailInput.value.trim(),
            password: passwordInput.value
        };

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                showMessage(result.message, 'success');

                // Redirect to dashboard after 1 second
                setTimeout(() => {
                    window.location.href = result.redirect || '/dashboard';
                }, 1000);
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

        // Email validation
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(emailInput.value)) {
            emailError.textContent = 'Please enter a valid email address';
            isValid = false;
        }

        // Password validation
        if (!passwordInput.value) {
            passwordError.textContent = 'Password is required';
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
