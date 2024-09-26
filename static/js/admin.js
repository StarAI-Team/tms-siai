document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('.sidebar ul li a'); // Select all sidebar links
    const sections = document.querySelectorAll('.content-section'); // Select all content sections

    // Function to hide all sections
    function hideAllSections() {
        sections.forEach(section => {
            section.style.display = 'none'; // Hide all sections
        });
    }

    // Initially hide all sections except the first one
    hideAllSections();
    if (sections.length > 0) {
        sections[0].style.display = 'block'; // Show the first section by default
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
