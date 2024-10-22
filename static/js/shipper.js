document.addEventListener("DOMContentLoaded", function() {
    const requiredFields = {
        section1: ['first_name', 'last_name', 'phone_number', 'id_number','id_number_text', 'company_name', 'company_location', 'company_email'],
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
        const formData = new FormData();
        const inputs = formSteps[currentStep].querySelectorAll('input, textarea');
    
        // Collecting form data from inputs in the current section
        inputs.forEach(input => {
            if (input.name) {
                if (input.type === 'file') {
                    // Append files to FormData
                    const files = input.files;
                    for (let i = 0; i < files.length; i++) {
                        formData.append(input.name, files[i]);
                    }
                } else {
                    // Append other input values
                    formData.append(input.name, input.value);
                }
            }
        });
    
        // Fetching user_id and ip_address metadata from the backend
        try {
            const metadataResponse = await fetch('/get_user_metadata');
            const metadata = await metadataResponse.json();
    
            // Adding user metadata to FormData
            formData.append('event_name', `shipperRegistration_${section}`);
            formData.append('user_id', metadata.user_id);
            formData.append('ip_address', metadata.ip_address);
            formData.append('timestamp', new Date().toISOString());
            formData.append('user_agent', navigator.userAgent);
            formData.append('current_section', section);

             // Sending the section data to the Flask backend
             const response = await fetch('/shipper_register', {
                method: 'POST',
                body: formData,  // Use FormData for the body
            });

            const responseData = await response.json();
            
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
                    const confirmPassword = document.getElementById("confirm_password").value;

                    // Validate password
                    if (password !== confirmPassword) {
                        document.getElementById("confirm_password").classList.add('error');
                        showErrorMessage("Passwords do not match.");
                        alert("Passwords do not match! Try Again");
                    } else {
                        document.getElementById("confirm_password").classList.remove('error');
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
    handleFileNameUpdate('id_number', 'id_number_text');
    handleFileNameUpdate('directorship', 'directorship_text');
    handleFileNameUpdate('proof_of_current_address', 'proof_of_current_address_text');
    handleFileNameUpdate('tax_clearance', 'tax_clearance_text');
    handleFileNameUpdate('certificate_of_incorporation', 'certificate_of_incorporation_text');
    handleFileNameUpdate('profile_picture', 'user_name');
});

document.getElementById('password').addEventListener('input', function() {
    const password = this.value;

    // Check for number
    const numberCheck = /\d/.test(password);
    document.getElementById('number').style.color = numberCheck ? 'green' : 'red';
    
    // Check for lowercase letter
    const lowercaseCheck = /[a-z]/.test(password);
    document.getElementById('lowercase').style.color = lowercaseCheck ? 'green' : 'red';
    
    // Check for uppercase letter
    const uppercaseCheck = /[A-Z]/.test(password);
    document.getElementById('uppercase').style.color = uppercaseCheck ? 'green' : 'red';
});

// Form submission validation
document.querySelector('form').addEventListener('submit', function(e) {
    const password = document.getElementById('password').value;

    const numberCheck = /\d/.test(password);
    const lowercaseCheck = /[a-z]/.test(password);
    const uppercaseCheck = /[A-Z]/.test(password);
    const lengthCheck = password.length >= 8;

    // If any condition is not met, prevent submission and alert the user
    if (!numberCheck || !lowercaseCheck || !uppercaseCheck || !lengthCheck) {
        e.preventDefault(); // Prevent form submission

        // Show an alert with the unmet conditions
        let errorMessage = "Password must meet the following requirements:\n";
        if (!lengthCheck) errorMessage += "- At least 8 characters long\n";
        if (!numberCheck) errorMessage += "- At least one number\n";
        if (!lowercaseCheck) errorMessage += "- At least one lowercase letter\n";
        if (!uppercaseCheck) errorMessage += "- At least one uppercase letter\n";

        alert(errorMessage); // Alert the user
    }
});

