document.addEventListener("DOMContentLoaded", function() {
    const requiredFields = {
        section1: ['first_name', 'last_name', 'phone_number', 'id_number','id_number', 'company_name', 'company_location', 'company_email'],
        section2: ['company_contact', 'bank_name', 'account_name', 'account_number', 'directorship_text','directorship', 'proof_of_current_address_text', 'proof_of_current_address' ],
        section3: ['tax_clearance_text', 'tax_clearance', 'tax_expiry', 'certificate_of_incorporation_text', 'certificate_of_incorporation'],
        section4: ['user_name', 'profile_picture', 'password', 'confirm_password']
    }
    
    const form = document.getElementById('multiStepForm');
    const nextButtons = document.querySelectorAll('.next-button');
    const prevButtons = document.querySelectorAll('.prev-button');
    const formSteps = document.querySelectorAll('.form-step');
    const showPasswordCheckbox = document.getElementById('show_password');
  
    
    document.getElementById('visibility_button1').addEventListener('click', function() {
        toggleVisibility('password', 'icon1');
    });
    
    document.getElementById('visibility_button2').addEventListener('click', function() {
        toggleVisibility('confirm_password', 'icon2');
    });
    
    function toggleVisibility(inputId, iconId) {
        const passwordInput = document.getElementById(inputId);
        const icon = document.getElementById(iconId);
    
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            icon.textContent = 'visibility_off';
        } else {
            passwordInput.type = 'password';
            icon.textContent = 'visibility';
        }
    }
    
    
    
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
    
        // Selecting only input elements in the current section
        const inputs = currentSection.querySelectorAll('input');

        inputs.forEach(input => {
            // Checking if the input is in the required list for the current step
            if (required.includes(input.name)) {
                console.log("Validating input: ", input.name);
                if (!input.checkValidity()) { 
                    isValid = false; 
                    input.classList.add('error'); 
                    showErrorMessage(`Please fill out the required field: ${input.placeholder}`); 
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
    
    async function sendEventData(section, shouldRedirect) {
        const data = {};
        const inputs = formSteps[currentStep].querySelectorAll('input, textarea');
    
        // Collecting form data from inputs in the current section
        inputs.forEach(input => {
            if (input.name && input.value) {
                data[input.name] = input.value; 
            }
        });
    
        console.log("Form data for section:", section, data);
    
        // Fetching user_id and ip_address metadata from the backend
        try {
            const metadataResponse = await fetch('/get_user_metadata');
            const metadata = await metadataResponse.json();
    
            const eventDetails = {
                event_name: `shipperRegistration_${section}`,  
                user_id: metadata.user_id,
                ip_address: metadata.ip_address,
                timestamp: new Date().toISOString(),
                user_agent: navigator.userAgent,
                current_section: section,
                form_data: data  
            };
    
            console.log("Payload to be sent:", eventDetails);

             // Sending the section data to the Flask backend
             const response = await fetch('/shipper_register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(eventDetails),  
            });
    
            const responseData = await response.json();
            console.log('Response data:', responseData);
            
            if (responseData.error) {
                alert(`Error: ${responseData.error}`);
                return false;  // Return false if there's an error
            } else {
                return true;  // Return true for a successful submission
            }
        } catch (error) {
            console.error('Error sending data:', error);
            alert('There was a problem submitting your data. Please try again.');
            return false;  // Return false on catch
        }
    }
    
 // Attaching event listener
 nextButtons.forEach(button => {
    button.addEventListener("click", async function() {
        if (validateFormStep()) {  // Performing validation for the current step
            const section = formSteps[currentStep].querySelector("h1").textContent.trim();  // Get section name
            const success = await sendEventData(section, false);  // Submitting section data
            
            if (success) {
                // Moving to the next step if submission is successful
                if (currentStep < formSteps.length - 1) {
                    currentStep++;
                    showStep(currentStep);
                } else {
                    // All sections completed successfully, validate password
                    const password = document.getElementById("password").value;
                    const confirmPasswordElement = document.getElementById("confirm_password");
                    
                    if (!confirmPasswordElement) {
                        console.error("Confirm password field is missing!");
                        return; 
                    }

                    const confirmPassword = confirmPasswordElement.value;

                    // Validate password
                    if (password !== confirmPassword) {
                        confirmPasswordElement.classList.add('error');
                        showErrorMessage("Passwords do not match.");
                        alert("Passwords do not match! Try Again");
                    } else {
                        confirmPasswordElement.classList.remove('error');
                        console.log("Passwords match.");
                        // Redirect to the desired URL upon successful validation
                        window.location.href = '/shipper-package';
                    }
                }
            }
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
    handleFileNameUpdate('profile_picture', 'user_name');
});
