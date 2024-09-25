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

            setTimeout(() => {
                console.log("Redirecting to:", url);
                window.location.href = url;
            }, 100); 

  
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

  
// Function to send event data to Flask
function sendEventData(section, selectedPackage, totalAmount) {
    const data = {
        package: selectedPackage,
        totalAmount: totalAmount
    };

    console.log("Sending event data for section:", section);
    console.log("Event Data:", data);

    // Fetching user_id and ip_address metadata from the backend
    fetch('/get_user_metadata')
    .then(response => {
        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.statusText}`);
        }
        return response.json();
    })
    .then(metadata => {
        console.log("Metadata received:", metadata);
        const eventDetails = {
            event_name: `clientRegistration(${section})`, 
            user_id: metadata.user_id,
            ip_address: metadata.ip_address,
            timestamp: new Date().toISOString(),
            user_agent: navigator.userAgent,
            current_section: section,
            form_data: data  
        };

        console.log("Payload to be sent:", eventDetails);

        // Sending the section data to the Flask backend
        fetch('/client_register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(eventDetails),  
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
        })
        .catch(error => {
            console.error('Error sending data to Flask:', error);
        });
    })
    .catch(error => {
        console.error('Error fetching user metadata:', error);
    });
}
