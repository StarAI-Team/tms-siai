document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('multiStepForm');
    const nextButtons = document.querySelectorAll('.next-button');
    const prevButtons = document.querySelectorAll('.prev-button');
    const formSteps = document.querySelectorAll('.form-step');
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
        let valid = true;
        const inputs = formSteps[currentStep].querySelectorAll('input');
        inputs.forEach(input => {
            console.log("Validating input: ", input.name);
            if (!input.checkValidity()) {
                valid = false;
                input.classList.add('error');
                showErrorMessage(`Please fill out the required field: ${input.placeholder}`);
                console.log("Input " + input.name + " is invalid.");
                console.log("Validation message: ", input.validationMessage);
            } else {
                input.classList.remove('error');
                console.log("Input " + input.name + " is valid.");
            }
        });
        return valid;
    }
    
    

    function validatePasswords() {
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirm_password").value;
        if (password.value !== confirmPassword.value) {
            confirmPassword.classList.add('error');
            showErrorMessage("Passwords do not match.");
            console.log("Passwords do not match.");
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
    
    nextButtons.forEach(button => {
        button.addEventListener("click", function() {
            console.log("Next button clicked");
            if (validateFormStep()) {
                if (currentStep === 4 && !validatePasswords()) {
                    return;
                }
                if (currentStep < formSteps.length - 1) {
                    currentStep++;
                    console.log("Moving to step:", currentStep);
                    showStep(currentStep);
                } else {
                    console.log("No more steps to move to.");
                }
            } else {
                console.log("Current step is invalid.");
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

    // Handle form submission
    form.addEventListener('submit', function (e) {
        e.preventDefault(); // Prevent the default form submission
        if (validateFormStep()) {
            const formData = new FormData(form);

            // Creating a custom event with a single event name
            const formSubmissionEvent = new CustomEvent('clientRegistration', {
                detail: {
                    formData: formData,
                    formId: form.id // Optional: Pass the form ID
                }
            });
            // Dispatch the custom event
            document.dispatchEvent(formSubmissionEvent);

            // Send form data to the server
            fetch('http://127.0.0.1:8000/client_register', {
                method: 'POST',
                body: formData,
            })            
            .then(response => response.json())
            .then(data => {
                if (data.error === "Missing fields") {
                    alert(`Error: Missing fields: ${data.fields.join(', ')}`);
                } else {
                    alert('Form submitted successfully!');
                    form.reset();
                    currentStep = 0;  // Reset to the first step after successful submission
                    showStep(currentStep);  // Show the first step
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        } else {
            showErrorMessage('Please fix the errors before submitting.');
        }
    });

     // Listen for the custom event globally 
     document.addEventListener('clientRegistration', function (e) {
        console.log('Form submission event detected: ', e.detail);
        const formData = e.detail.formData;
        for (var pair of formData.entries()) {
            console.log(pair[0] + ': ' + pair[1]);
        }
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
