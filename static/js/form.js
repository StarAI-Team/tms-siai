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
            // You can handle form submission here
        }
    });


    // Initially show the first step
    showStep(currentStep);
});
