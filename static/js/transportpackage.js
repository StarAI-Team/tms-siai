document.addEventListener('DOMContentLoaded', () => {
    const packages = document.querySelectorAll('.package');
    const extraServicesInput = document.getElementById('extra-services');
    
    packages.forEach(packageElement => {
        // Add click event listener for each package
        packageElement.addEventListener('click', (e) => {
            // Get the clicked package button
            const clickedPackageBtn = e.target.closest('.select-package');
  
            if (clickedPackageBtn) {
                e.preventDefault();  // Prevent default link behavior
  
                // Get the selected package details
                const selectedPackage = clickedPackageBtn.getAttribute('data-package');
                const packageAmount = parseFloat(clickedPackageBtn.getAttribute('data-amount'));
  
                // Get extra service if selected
                const selectedService = extraServicesInput ? extraServicesInput.value : null;
                let serviceAmount = 0;
  
                // Check if extra service has a value
                if (selectedService) {
                    const serviceOption = document.querySelector(`#services option[value="${selectedService}"]`);
                    if (serviceOption) {
                        serviceAmount = parseFloat(serviceOption.getAttribute('data-value')); 
                    }
                }
  
                // Calculate total amount
                const totalAmount = packageAmount + serviceAmount;
  
                // Redirect to next page with package and total amount
                const url = `/transporter_package_selected?package=${encodeURIComponent(selectedPackage)}&amount=${totalAmount}`;
                window.location.href = url;
                
            }
  
            // Animate the clicked package with smooth and calming effect
            anime({
                targets: packageElement,
                scale: 1.05,  // Slight and subtle scaling
                duration: 500,  // Moderate speed
                easing: 'easeInOutSine',  // Smooth and gradual easing
                borderColor: '#ffffff',  // White border color
                boxShadow: '0px 10px 20px rgba(0, 0, 0, 0.2)',  // Soft shadow for depth
            });
  
            // Animate the other packages back to their original state
            packages.forEach(otherPackage => {
                if (otherPackage !== packageElement) {
                    anime({
                        targets: otherPackage,
                        scale: 1,  // Return to normal size
                        duration: 500,  // Same duration for smooth transition
                        easing: 'easeInOutSine',  // Smooth transition
                        borderColor: '#ffffff',  // White border
                        boxShadow: '0px 0px 0px rgba(0, 0, 0, 0)',  // Remove shadow
                    });
                }
            });
        });
    });
  });
  