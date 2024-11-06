console.log("admin.js loaded");

function generateSubmissionId() {
    return 'submission_' + Date.now();
}

document.addEventListener('DOMContentLoaded', function() {
    console.log("Page loaded. Current localStorage:", localStorage);
    const links = document.querySelectorAll('.sidebar ul li a'); // Select all sidebar links
    const sections = document.querySelectorAll('.content-section'); // Select all content sections
    const submissionLinks = document.querySelectorAll('a[data-role="submission-link"]');

    submissionLinks.forEach((link, index) => {
        link.addEventListener('click', function(event) {
            storeSubmissionId(index);
        });
    });

    window.storeSubmissionId = function(submissionIndex) {
        const uniqueSubmissionId = generateSubmissionId(); // Generate a unique ID if needed for tracking
        localStorage.setItem('uniqueSubmissionId', uniqueSubmissionId); // Store the unique ID
        localStorage.setItem('lastSubmissionIndex', submissionIndex); // Store only the index
        console.log("Stored unique ID:", uniqueSubmissionId);
        console.log("Stored submission index:", submissionIndex);
        console.log("Expected element ID for removal: submission-" + submissionIndex);
    };
    
    
    
 

    // Function to hide all sections
    function hideAllSections() {
        sections.forEach(section => {
            section.style.display = 'none'; // Hide all sections
        });
    }

    // Initially hide all sections except the first one
    hideAllSections();
    if (sections.length > 0) {
        sections[0].style.display = 'block'; 
    }


    // Attach click event to each link
    links.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent the default link behavior

            // Remove 'active' class from all links and hide all sections
            links.forEach(l => l.classList.remove('active'));
            hideAllSections();

            // Get the target section ID from the link's data-target attribute
            const targetId = this.getAttribute('data-target');
            const targetSection = document.getElementById(targetId);

            // If the target section exists, show it and mark the link as active
            if (targetSection) {
                targetSection.style.display = 'block';
                this.classList.add('active');
            } else {
                console.error(`No section found with ID: ${targetId}`);
            }
        });
    });
});

// Clear entry function to be used in both admin.html and submit.html
function clearEntry() {
    const rejectionReasonContainer = document.getElementById("rejection-reason-container");
    if (rejectionReasonContainer && rejectionReasonContainer.style.display === "block") {
        rejectionReasonContainer.style.display = "none";
    }

    const rejectionReasonField = document.getElementById('rejection-reason');
    if (rejectionReasonField) {
        rejectionReasonField.value = ''; // Clear rejection reason
    }

    // Retrieve the position/index to locate and remove the correct HTML element
    const lastSubmissionIndex = localStorage.getItem('lastSubmissionIndex');
    console.log("Retrieved lastSubmissionIndex from localStorage:", lastSubmissionIndex);

    if (lastSubmissionIndex) {
        // Form the element ID based on the expected format in admin.html
        const elementId = `submission-${lastSubmissionIndex}`;
        const submissionElement = document.getElementById(elementId);
        console.log("Attempting to remove element with ID:", elementId);

        if (submissionElement) {
            submissionElement.remove(); // Remove the element by ID
            console.log("Removed submission link with ID:", elementId);
        } else {
            console.warn("Could not find element with ID:", elementId);
        }
        localStorage.removeItem('lastSubmissionIndex'); // Clean up storage after use
    }

    // Clean up uniqueSubmissionId if needed
    const uniqueSubmissionId = localStorage.getItem('uniqueSubmissionId');
    if (uniqueSubmissionId) {
        console.log("Clearing unique submission ID:", uniqueSubmissionId);
        localStorage.removeItem('uniqueSubmissionId');
    }

    alert("All entries have been cleared.");
    console.log("Entries cleared and navigating back to the previous page");

    // Redirect back to admin.html with a unique parameter to refresh the page
    window.location.href = `${window.location.origin}/?refresh=${Date.now()}`;
}