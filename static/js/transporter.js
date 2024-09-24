document.addEventListener("DOMContentLoaded", function() {
    const requiredFields = {
        section1: ['first_name', 'last_name', 'phone_number', 'id_number','id_number', 'company_name', 'company_location', 'company_email'],
        section2: ['company_contact', 'bank_name', 'account_name', 'account_number', 'directorship_text','directorship', 'proof_of_current_address_text', 'proof_of_current_address' ],
        section3: ['tax_clearance_text', 'tax_clearance', 'tax_expiry', 'certificate_of_incorporation_text', 'certificate_of_incorporation','operators_licence_text', 'operators_licence', 'operators_expiry', 'permits_text', 'permits', 'permit_expiry', 'tracking_licence_text','tracking_licence', ],
        section4: ['number_of_trucks', 'num_of_trucks_text', 'num_of_trucks', 'reg_books_text','reg_books', 'certificate_of_fitness_text', 'certificate_of_fitness'],
        section5: ['user_name', 'profile_picture', 'password', 'confirm_password']
    };
    const form = document.getElementById('multiStepForm');
    const nextButtons = document.querySelectorAll('.next-button');
    const prevButtons = document.querySelectorAll('.prev-button');
    const formSteps = document.querySelectorAll('.form-step');
    const finalNextButton = document.querySelector('#final-next-button');
    let currentStep = 0;

    function showStep(step) {
        formSteps.forEach((el, index) => {
            el.style.display = index === step ? "block" : "none";
        });
        clearErrorMessage();
    }

    // Show only the first form step initially
    showStep(currentStep);

    function validateFormStep() {
        const currentSection = formSteps[currentStep]; 
        const required = requiredFields[`section${currentStep + 1}`] || [];
        let isValid = true; // Initialize validity to true
    
        // Select only input elements in the current section
        const inputs = currentSection.querySelectorAll('input');

        inputs.forEach(input => {
            // Check if the input is in the required list for the current step
            if (required.includes(input.name)) {
                console.log("Validating input: ", input.name);
                if (!input.checkValidity()) { 
                    isValid = false; 
                    input.classList.add('error'); 
                    showErrorMessage(`Please fill out the required field: ${input.placeholder}`); // Show error message
                    console.log("Input " + input.name + " is invalid.");
                    console.log("Validation message: ", input.validationMessage);
                } else {
                    input.classList.remove('error'); 
                    console.log("Input " + input.name + " is valid.");
                }
            }
        });
        
        return isValid; 
    }
    
    
    finalNextButton.addEventListener('click', async function(event) {
        
        if (!validateFormStep()) {
            event.preventDefault(); // Prevent moving to the next step if validation fails
            return; 
        }
    
        // If on step 4, validate passwords before proceeding
    if (currentStep === 4 && !validatePasswords()) {
        alert('Passwords do not match!');
        return; 
    }

    // Gather form data to send to Flask
    const formData = new FormData(document.getElementById("multiStepForm"));
    const payload = {};
    
    // Convert FormData to a plain object
    formData.forEach((value, key) => {
        payload[key] = value;
    });

    try {
        // Send data to Flask processing endpoint using fetch
        const response = await fetch('http:/127.0.0.1:8000/register_transporter', {  
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (response.ok) {
            console.log('Data sent to Flask successfully.');
            // Optionally, you can proceed to the next step or route
            window.location.href = 'http://127.0.0.1:8000/transporter-package'
        } else {
            console.error('Error sending data to Flask:', response.statusText);
        }
    } catch (error) {
        console.error('Error sending data to Flask:', error);
    }
});


    function validatePasswords() {
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirm_password").value;
        if (password !== confirmPassword) {
            confirmPassword.classList.add('error');
            showErrorMessage("Passwords do not match.");
            console.log("Passwords do not match.");
            alert("Passwords do not match! Try Again")
            return false;
        } else {
            confirmPassword.classList.remove('error');
            console.log("Passwords match.");
            return true;
        }
    }


    function showErrorMessage(message) {
        const errorMessageDiv = document.querySelector('#step-error-message');
        errorMessageDiv.innerText = message;
        errorMessageDiv.style.display = 'block';
    }

    function clearErrorMessage() {
        const errorMessageDiv = document.querySelector('#step-error-message');
        errorMessageDiv.innerText = '';
        errorMessageDiv.style.display = 'none';
    }

    function sendEventData(section) {
        const data = {};
        const inputs = formSteps[currentStep].querySelectorAll('input');
        inputs.forEach(input => {
            data[input.name] = input.value;
        });
        console.log("Form data being sent:", data);
    
        // Capture user_id and ip_address from the backend
        fetch('/get_user_metadata')
        .then(response => response.json())
        .then(metadata => {
            const eventDetails = {
            event_name: `transporterRegistration(${section})`,  
            user_id: metadata.user_id,
            ip_address: metadata.ip_address,
            timestamp: new Date().toISOString(),
            user_agent: navigator.userAgent,
            form_data: data  
        };
    
           
        // Log the final payload before sending
        console.log("Final payload to be sent:", eventDetails)
    
    
            // Send the captured data to Flask for processing
            fetch('/register_transporter', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(eventDetails),
            })
            .then(response => response.json())
            .then(data => {
                console.log('Event data sent:', data);
            })
            .catch(error => console.error('Error sending event data:', error));
        })
        .catch(error => console.error('Error fetching metadata:', error));
    }
    
   // Assuming you have already defined formSteps and currentStep

nextButtons.forEach(button => {
    button.addEventListener("click", async function() {
        console.log("Next button clicked");

        // Validate the current form step before proceeding
        if (validateFormStep()) {
            // Create an object to hold form data
            const payload = {};
            const inputs = formSteps[currentStep]?.querySelectorAll("input, textarea") || [];

            // Append data to the payload object
            inputs.forEach(input => {
                if (input.name && input.value) {
                    payload[input.name] = input.value; // Use the name attribute as the key
                }
            });

            // Capture user metadata (user_id and ip_address)
            try {
                const metadataResponse = await fetch('/get_user_metadata');
                const metadata = await metadataResponse.json();

                // Add user_id and ip_address to the payload
                payload.user_id = metadata.user_id; 
                payload.ip_address = metadata.ip_address; // Optional, if needed
            } catch (error) {
                console.error('Error fetching user metadata:', error);
                return; // Exit if metadata cannot be fetched
            }

            // Log the final payload before sending
            console.log("Final Payload being sent:", payload);

            try {
                const response = await fetch('http://127.0.0.1:8000/register_transporter', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                });

                const data = await response.json();

                // Handle response
                if (data.error) {
                    alert(`Error: ${data.error}`);
                } else {
                    // Proceed to the next step
                    console.log("Data submitted successfully:", data);
                    // Move to the next step logic...
                    if (currentStep < formSteps.length - 1) {
                        currentStep++;
                        showStep(currentStep); // Display the next step
                    } else {
                        alert('Final step completed successfully!');
                        form.reset(); // Reset the form if needed
                    }
                }
            } catch (error) {
                console.error('Error submitting step:', error);
            }
        } else {
            console.log("Current step is invalid.");
            showErrorMessage('Please fix the errors before proceeding.');
        }
    });
});

    


 prevButtons.forEach(button => {
    button.addEventListener("click", function() {
        if (currentStep > 0) {
            currentStep--;
            showStep(currentStep);
        }
    });
});


    // Function to handle file name update for file inputs
    function handleFileNameUpdate(fileInputId, textInputId) {
        const fileInput = document.getElementById(fileInputId);
        const textInput = document.getElementById(textInputId);

        fileInput.addEventListener('change', function () {
            const fileName = fileInput.files.length > 0 ? fileInput.files[0].name : '';
            textInput.value = fileName;
        });
    }

    // Bind the file input elements to handle file name display
    handleFileNameUpdate('directorship', 'directorship_text');
    handleFileNameUpdate('proof_of_current_address', 'proof_of_current_address_text');
    handleFileNameUpdate('tax_clearance', 'tax_clearance_text');
    handleFileNameUpdate('certificate_of_incorporation', 'certificate_of_incorporation_text');
    handleFileNameUpdate('operators_licence', 'operators_licence_text');
    handleFileNameUpdate('permits', 'permits_text');
    handleFileNameUpdate('tracking_licence', 'tracking_licence_text');
    handleFileNameUpdate('num_of_trucks', 'num_of_trucks_text');
    handleFileNameUpdate('reg_books', 'reg_books_text');
    handleFileNameUpdate('certificate_of_fitness', 'certificate_of_fitness_text');
    handleFileNameUpdate('profile_picture', 'user_name');
});
