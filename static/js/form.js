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
                if (currentStep === 4) {
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

    // Initially show the first step
    showStep(currentStep);

    // Retrieve session ID and client ID from the injected HTML
    const sessionDataElement = document.getElementById('sessionData');
    const sessionId = sessionDataElement.getAttribute('data-session-id');
    const clientId = sessionDataElement.getAttribute('data-client-id');



    document.getElementById('multiStepForm').addEventListener('submit', function(event) {
        event.preventDefault();
        // Generate a unique event name using session ID or client ID
        let urlParams = new URLSearchParams(window.location.search);
        const isSave = urlParams.get('action') === 'save';  
        console.log('Is save parameter present:', isSave)

        const eventName = `load_submission${isSave ? '_save' : ''}_${sessionId}_${clientId}_${Date.now()}`;

         // Debugging log for the event name
        console.log('Generated event name:', eventName);


        // Collect form data
        const formData = new FormData(this);
        const payload = {};
        formData.forEach((value, key) => {
            payload[key] = value;
        });

        // Add the unique event name to the payload
        payload.event_name = eventName;

        // Append transporter data from URL parameters (if available)
        urlParams = new URLSearchParams(window.location.search);
        urlParams.forEach((value, key) => {
            if (key.startsWith('transporter_')) {
                payload[key] = value;
            }
        });

        // Send the JSON payload via Fetch API
        fetch('/post_load', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })  
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            alert(' Form Submitted Successfully!');
        this.reset(); 
        currentStep = 0; 
        showStep(currentStep); 
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
