document.addEventListener("DOMContentLoaded", function() {
    const steps = document.querySelectorAll(".form-step");
    let currentStep = 0;

    // Show the current step
    function showStep(step) {
        steps.forEach((el, index) => {
            el.style.display = index === step ? "block" : "none";
        });
    }

    // Validate passwords
    function validatePasswords() {
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirm_password").value;

        if (password !== confirmPassword) {
            alert("Passwords do not match.");
            return false;
        }
        return true;
    }

    // Move to the next step
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

    // Move to the previous step
    document.querySelectorAll(".prev-button").forEach(button => {
        button.addEventListener("click", function() {
            if (currentStep > 0) {
                currentStep--;
                showStep(currentStep);
            }
        });
    });

    // Handle form submission
    document.querySelector(".submit-button").addEventListener("click", function() {
        if (currentStep === steps.length - 1 && validatePasswords()) {
            alert("Form submitted successfully!");
            
        }
    });


    // Initially show the first step
    showStep(currentStep);

    // Retrieve session ID and client ID from the injected HTML
    const sessionDataElement = document.getElementById('sessionData');
    const sessionId = sessionDataElement.getAttribute('data-session-id');
    const clientId = sessionDataElement.getAttribute('data-client-id');

    document.getElementById('multiStepForm').addEventListener('submit', function(event) {
        event.preventDefault();

        // Generate a unique event name using session ID or client ID
        const eventName = `load_submission_${sessionId}_${clientId}_${Date.now()}`;

        // Collect form data
        const formData = new FormData(this);
        const payload = {};
        formData.forEach((value, key) => {
            payload[key] = value;
        });

        // Add the unique event name to the payload
        payload.event_name = eventName;

        // Send the JSON payload via Fetch API
        fetch('http://127.0.0.1:5000/Post_load', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
