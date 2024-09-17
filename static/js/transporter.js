document.addEventListener("DOMContentLoaded", function() {
    const steps = document.querySelectorAll(".form-step");
    let currentStep = 0;

    function showStep(step) {
        steps.forEach((el, index) => {
            el.style.display = index === step ? "block" : "none";
        });
    }

    function validatePasswords() {
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirm_password").value;
        if (password !== confirmPassword) {
            alert("Passwords do not match.");
            return false;
        }
        return true;
    }

    document.querySelectorAll(".next-button").forEach(button => {
        button.addEventListener("click", function() {
            if (currentStep < steps.length - 1) {
                if (currentStep === 4 && !validatePasswords()) {
                    return;
                }
                currentStep++;
                showStep(currentStep);
            }
        });
    });

    document.querySelectorAll(".prev-button").forEach(button => {
        button.addEventListener("click", function() {
            if (currentStep > 0) {
                currentStep--;
                showStep(currentStep);
            }
        });
    });

    // Handle form submission
    document.getElementById('multiStepForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const sessionDataElement = document.getElementById('sessionData');
        const sessionId = sessionDataElement.getAttribute('data-session-id');
        const clientId = sessionDataElement.getAttribute('data-client-id');

        const formData = new FormData(this);

        const eventName = `load_submission_${sessionId}_${clientId}_${Date.now()}`;
        formData.append('event_name', eventName);

        fetch('http://127.0.0.1:8000/transport_register', {
            method: 'POST',
            body: formData  // Send the form data, which includes file uploads
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    showStep(currentStep);
});
