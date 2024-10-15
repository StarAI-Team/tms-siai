 <!-- Reviews Section -->
 <div id="reviews-section"style="display: none;">
    <h4>
        <span id="leave-review" style="cursor: pointer; color: blue; text-decoration: underline;">Leave a Review:</span>
    </h4>
    
    <textarea id="reviews-text"  placeholder="Write your review here"></textarea><br>

    <!-- Star Rating Section -->
    <div id="rating-section">
        <label for="rating-5" class="star">
            <input type="radio" id="rating-5" name="rating" value="5" onclick="setRating(5)">
            ★
        </label>
        <label for="rating-4" class="star">
            <input type="radio" id="rating-4" name="rating" value="4" onclick="setRating(4)">
            ★
        </label>
        <label for="rating-3" class="star">
            <input type="radio" id="rating-3" name="rating" value="3" onclick="setRating(3)">
            ★
        </label>
        <label for="rating-2" class="star">
<input type="radio" id="rating-2" name="rating" value="2" onclick="setRating(2)">
★
</label>
<label for="rating-1" class="star">
<input type="radio" id="rating-1" name="rating" value="1" onclick="setRating(1)">
★
</label>
</div> 

<button onclick="submitReview()">Submit Review</button>

</div>


// Function to show the Add Reviews section
function showAddReviewSection() {
    const reviewsSection = document.getElementById('reviews-section');
    reviewsSection.style.display = 'block'; // Change display to block to show the section
}

// Attach click event to the "Leave a Review" text
document.getElementById('leave-review').addEventListener('click', showAddReviewSection);

    // Function to submit the review
function submitReview() {
// Get the review text and rating from the form inputs
const transporterId = document.getElementById('transporter_id').value;  
const reviewText = document.getElementById('reviews-text').value;       
let selectedRating = null;

// Get the selected rating (if using radio buttons for star ratings)
const ratingInputs = document.querySelectorAll('input[name="rating"]');
for (let input of ratingInputs) {
    if (input.checked) {
        selectedRating = input.value; // Get the selected rating
        break; // Exit loop if a rating is found
    }
}

// Ensure the user filled in all required fields
if (!reviewText || !selectedRating) {
    alert("Please fill in all fields.");
    return;
}

// Build the payload to send to Flask
const reviewData = {
    transporter_id: transporterId, // Ensure the key matches what Flask expects
    rating: selectedRating,
    review: reviewText,
    timestamp: new Date().toLocaleString() // Optional: adding timestamp
};

// Send review data to the Flask backend via POST request
fetch('/submit_review', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(reviewData), // Send the review data as JSON
})
.then(response => {
    if (!response.ok) throw new Error('Network response was not ok');
    return response.json();
})
.then(data => {
    if (data.success) {
        alert("Review submitted successfully!");
        // Clear the form and reset the ratings
        document.getElementById('reviews_text').value = ''; // Clear the review text
        setRating(0); // Reset rating display (you can define setRating() to clear stars)
    } else {
        alert("Failed to submit review.");
    }
})
.catch(error => {
    console.error("Error submitting review:", error);
});
}
}

// Function to set the rating
function setRating(rating) {
    selectedRating = rating; // Store the selected rating
    const stars = document.querySelectorAll('.star');
    stars.forEach((star, index) => {
        star.classList.toggle('filled', index < selectedRating);
  });

    // Reset rating input fields
  const ratingInputs = document.querySelectorAll('input[name="rating"]');
  ratingInputs.forEach(input => {
    input.checked = input.value == rating;
    });
}
})


