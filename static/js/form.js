document.addEventListener("DOMContentLoaded", function () {
    const steps = document.querySelectorAll(".form-step");
    let currentStep = 0;

    // Show the current step
    function showStep(step) {
        steps.forEach((el, index) => {
            el.style.display = index === step ? "block" : "none";
        });
    }

    // Helper: Fetch metadata
    async function fetchMetadata(companyName) {
        try {
            const response = await fetch(`/get_user_metadata?company_name=${encodeURIComponent(companyName)}`);
            if (!response.ok) {
                throw new Error(`Failed to fetch metadata: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error("Error fetching metadata:", error);
            return null;
        }
    }

    // Helper: Collect data from URL parameters
    function collectURLParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const params = {};
        urlParams.forEach((value, key) => {
            if (key.startsWith("transporter_")) {
                params[key] = value;
            }
        });
        return params;
    }

    // Move to the next step
    document.querySelectorAll(".next-button").forEach(button => {
        button.addEventListener("click", async function () {
            if (currentStep < steps.length - 1) {
                const currentStepElement = steps[currentStep];
                const inputs = currentStepElement.querySelectorAll("input, select, textarea");
                const payload = {};

                inputs.forEach(input => {
                    payload[input.name] = input.value;
                });

                // Retrieve session data
                const sessionDataElement = document.getElementById("sessionData");
                const sessionId = sessionDataElement.getAttribute("data-session-id");
                const clientId = sessionDataElement.getAttribute("data-client-id");

                // Generate unique event name
                payload.event_name = `load_submission_step_${currentStep + 1}_${sessionId}_${clientId}_${Date.now()}`;

                // Get company name
                let companyName = document.getElementById("company_name").value;
                if (companyName) {
                    companyName = companyName.replace(/ /g, "_");
                }

                // Fetch metadata
                const metadata = await fetchMetadata(companyName);
                if (metadata) {
                    payload.metadata = metadata;
                }

                // Send payload to `/post_load`
                fetch("/post_load", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        ...payload,
                        user_id: payload.metadata?.user_id || null,
                        ip_address: payload.metadata?.ip_address || null,
                        metadata: undefined,
                    }),
                })
                    .then(response => response.json())
                    .then(data => {
                        console.log("Step data sent successfully:", data);
                    })
                    .catch(error => {
                        console.error("Error sending step data:", error);
                    });

                // Move to the next step
                currentStep++;
                showStep(currentStep);
            }
        });
    });

    // Move to the previous step
    document.querySelectorAll(".prev-button").forEach(button => {
        button.addEventListener("click", function () {
            if (currentStep > 0) {
                currentStep--;
                showStep(currentStep);
            }
        });
    });

    // Handle form submission
    document.getElementById("multiStepForm").addEventListener("submit", async function (event) {
        event.preventDefault();

        const sessionDataElement = document.getElementById("sessionData");
        const sessionId = sessionDataElement.getAttribute("data-session-id");
        const clientId = sessionDataElement.getAttribute("data-client-id");

        const formData = new FormData(this);
        const payload = {};

        formData.forEach((value, key) => {
            payload[key] = value;
        });

        // Generate unique event name
        const urlParams = new URLSearchParams(window.location.search);
        const isSave = urlParams.get("action") === "save";
        payload.event_name = `load_submission${isSave ? "_save" : ""}_${sessionId}_${clientId}_${Date.now()}`;

        // Append URL params to payload
        Object.assign(payload, collectURLParams());

        // Get company name
        let companyName = document.getElementById("company_name").value;
        if (companyName) {
            companyName = companyName.replace(/ /g, "_");
        }

        // Fetch metadata
        const metadata = await fetchMetadata(companyName);
        if (metadata) {
            payload.metadata = metadata;
        }

        // Send payload
        fetch("/post_load", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                ...payload,
                user_id: payload.metadata?.user_id || null,
                ip_address: payload.metadata?.ip_address || null,
                metadata: undefined,
            }),
        })
            .then(response => response.json())
            .then(data => {
                console.log("Success:", data);
                alert("Form Submitted Successfully!");
                this.reset();
                currentStep = 0;
                showStep(currentStep);
            })
            .catch(error => {
                console.error("Error:", error);
            });
    });

    // Initially show the first step
    showStep(currentStep);
});
