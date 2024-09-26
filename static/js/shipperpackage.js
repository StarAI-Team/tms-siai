document.addEventListener('DOMContentLoaded', () => {
    const packages = document.querySelectorAll('.package');
    const extraServicesInput = document.getElementById('extra-services');
    
    packages.forEach(packageElement => {
        // Adding click event listener for each package
        packageElement.addEventListener('click', async (e) => {
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

                // Animating the clicked package with smooth and calming effect
                anime({
                    targets: packageElement,
                    scale: 1.28,  
                    duration: 500, 
                    easing: 'easeInOutSine', 
                    borderColor: '#ffffff', 
                    boxShadow: '0px 10px 20px rgba(0, 0, 0, 0.2)',  
                    complete: async () => {  // Callback to run after animation completes
                        // Send event data to the backend
                        const section = 'Packages'; 
                        const sentData = await sendEventData(section, selectedPackage, totalAmount); // Wait for the data to be sent
                        
                        // Check if data was sent successfully
                        if (sentData) {
                            // Redirect only after the event data is successfully sent
                            const url = `/shipper_package_selected?package=${encodeURIComponent(selectedPackage)}&amount=${totalAmount}`;
                            console.log("Redirecting to:", url);
                            window.location.href = url;
                        } else {
                            console.error("Failed to send event data. Not redirecting.");
                        }
                    }
                });

                // Animating the other packages back to their original state
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
            }
        });
    });
});

// Function to send event data to Flask
async function sendEventData(section, selectedPackage, totalAmount) {
    const data = {
        package: selectedPackage,
        totalAmount: totalAmount
    };

    console.log("Sending event data for section:", section);
    console.log("Event Data:", data);

    try {
        // Disable form buttons or show a loader (optional, based on UI requirements)
        disableButtons(true); // You can implement this to disable buttons temporarily

        // Fetching user_id and ip_address metadata from the backend
        const metadataResponse = await fetch('/get_user_metadata');
        const metadata = await metadataResponse.json();

        // Prepare event details to be sent
        const eventDetails = {
            event_name: `shipper(${section})`,
            user_id: metadata.user_id,
            ip_address: metadata.ip_address,
            timestamp: new Date().toISOString(),
            user_agent: navigator.userAgent,
            current_section: section,
            totalAmount: totalAmount,
            form_data: data
        };

        console.log("Payload to be sent:", eventDetails);

        // Sending event data to the backend for processing
        const registerResponse = await fetch('/shipper_register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(eventDetails),
        });

        // Handle the backend response
        if (!registerResponse.ok) {
            throw new Error(`Error during submission: ${registerResponse.statusText}`);
        }

        const responseData = await registerResponse.json();
        console.log('Response data:', responseData);

        // Check if there's an error in the response and handle it
        if (responseData.error) {
            console.error(`Error: ${responseData.error}`);
            alert(`Error: ${responseData.error}`);
            return false; 
        }

        return true;  // Indicate success

    } catch (error) {
        console.error('Error sending event data to Flask:', error);
        alert('There was a problem submitting your data. Please try again.');
        return false;  

        
    } finally {
        disableButtons(false);  // Re-enable buttons after processing
    }
}

// Optional function to disable/enable buttons (for better user experience during processing)
function disableButtons(disable) {
    const buttons = document.querySelectorAll('button, input[type="submit"]');
    buttons.forEach(button => {
        button.disabled = disable;
    });
}
