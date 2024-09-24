document.addEventListener('DOMContentLoaded', () => {
    const packages = document.querySelectorAll('.package');
    const extraServicesInput = document.getElementById('extra-services');
    
    packages.forEach(packageElement => {
        // Adding click event listener for each package
        packageElement.addEventListener('click', (e) => {
            // Get the clicked package button
            const clickedPackageBtn = e.target.closest('.select-package');
  
            if (clickedPackageBtn) {
                e.preventDefault();  // Prevent default link behavior
  
                // Getting the selected package details
                const selectedPackage = clickedPackageBtn.getAttribute('data-package');
                const packageAmount = parseFloat(clickedPackageBtn.getAttribute('data-amount'));
  
                // Getting extra service if selected
                const selectedService = extraServicesInput ? extraServicesInput.value : null;
                let serviceAmount = 0;
  
                // Checking if extra service has a value
                if (selectedService) {
                    const serviceOption = document.querySelector(`#services option[value="${selectedService}"]`);
                    if (serviceOption) {
                        serviceAmount = parseFloat(serviceOption.getAttribute('data-value')); 
                    }
                }
  
                // Calculating total amount
                const totalAmount = packageAmount + serviceAmount;
  
                // Redirecting to next page with package and total amount
                const url = `/client_package_selected?package=${encodeURIComponent(selectedPackage)}&amount=${totalAmount}`;
                window.location.href = url;
                
            }
  
            // Animating the clicked package with smooth and calming effect
            anime({
                targets: packageElement,
                scale: 1.28,  
                duration: 500, 
                easing: 'easeInOutSine', 
                borderColor: '#ffffff', 
                boxShadow: '0px 10px 20px rgba(0, 0, 0, 0.2)',  
            });
  
            // Animatimg the other packages back to their original state
            packages.forEach(otherPackage => {
                if (otherPackage !== packageElement) {
                    anime({
                        targets: otherPackage,
                        scale: 1,  
                        duration: 500, 
                        easing: 'easeInOutSine',  
                        borderColor: '#ffffff',  
                        boxShadow: '0px 0px 0px rgba(0, 0, 0, 0)',  
                    });
                }
            });
        });
    });
  });
  