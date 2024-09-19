document.addEventListener("DOMContentLoaded", function() {
    const steps = document.querySelectorAll(".form-step");
    let currentStep = 0;

    // Show the current step
    function showStep(step) {
        steps.forEach((el, index) => {
            el.style.display = index === step ? "block" : "none";
        });
    }

    // Move to the next step
    document.querySelectorAll(".next-button").forEach(button => {
        button.addEventListener("click", function() {
            if (currentStep < steps.length - 1) {
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

    // Initially show the first step
    showStep(currentStep);

    // Retrieve session ID and client ID from the injected HTML
    const sessionDataElement = document.getElementById('sessionData');
    const sessionId = sessionDataElement.getAttribute('data-session-id');
    const clientId = sessionDataElement.getAttribute('data-client-id');

    document.getElementById('multiStepForm').addEventListener('submit', function(event) {
        event.preventDefault();

        // Generate a unique event name using session ID or client ID
        const eventName = `load_submission`;
        const clientId = `${sessionId}`;

        // Collect form data
        const formData = new FormData(this);
        const payload = {};
        formData.forEach((value, key) => {
            payload[key] = value;
        });

        // Add the unique event name and client ID to the payload
        payload.event_name = eventName;
        payload.client_id = clientId;

        // Add user agent to the payload
        payload.user_agent = navigator.userAgent;

        // Optional: Fetch user IP from an external service and append it to the payload
        fetch('https://api.ipify.org?format=json')
            .then(response => response.json())
            .then(data => {
                payload.user_ip = data.ip;  // Add user IP to the payload

                // Now that we have both the user agent and IP, send the payload
                sendFormData(payload);
            })
            .catch(error => {
                console.error('Error fetching IP address:', error);
                
                // If fetching the IP fails, still send the form data without it
                sendFormData(payload);
            });
    });

    // Function to send form data to the backend
    function sendFormData(payload) {
        fetch('http://127.0.0.1:5000/Post_load', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload),
            mode: 'cors'
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});
