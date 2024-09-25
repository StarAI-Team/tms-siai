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
        const inputs = formSteps[currentStep].querySelectorAll('input, textarea');
    
        // Collect form data from inputs in the current section
        inputs.forEach(input => {
            if (input.name && input.value) {
                data[input.name] = input.value;
            }
        });
    
        console.log("Form data for section:", section, data);
    
        // Fetch user_id and ip_address metadata from the backend
        fetch('/get_user_metadata')
        .then(response => response.json())
        .then(metadata => {
            const eventDetails = {
                event_name: `transporterRegistration(${section})`,  // Use the section name
                user_id: metadata.user_id,
                ip_address: metadata.ip_address,
                timestamp: new Date().toISOString(),
                user_agent: navigator.userAgent,
                current_section: section,
                form_data: data  // Include form data for the current section
            };
    
            console.log("Payload to be sent:", eventDetails);
    
            // Send the section data to the Flask backend
            fetch('/register_transporter', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(eventDetails),  // Send JSON payload
            })
            .then(response => response.json())
            .then(data => {
                console.log('Response data:', data);
                if (data.error) {
                    alert(`Error: ${data.error}`);
                } else {
                    // Move to the next step if submission is successful
                    if (currentStep < formSteps.length - 1) {
                        currentStep++;
                        showStep(currentStep);
                    } else {
                        alert('All sections completed successfully!');
                        form.reset();  // Reset the form when all sections are completed
                    }
                }
            })
            .catch(error => {
                console.error('Error sending data:', error);
                alert('There was a problem submitting your data. Please try again.');
            });
        })
        .catch(error => {
            console.error('Error fetching metadata:', error);
            alert('Error fetching user metadata.');
        });
    }
    
    // Attach event listener for the "Next" button
    nextButtons.forEach(button => {
        button.addEventListener("click", function() {
            if (validateFormStep()) {  // Perform validation for the current step
                const section = formSteps[currentStep].querySelector("h1").textContent.trim();  // Get section name
                sendEventData(section);  // Submit section data
            } else {
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
