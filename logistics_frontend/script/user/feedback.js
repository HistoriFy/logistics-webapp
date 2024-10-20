function createFeedbackForm(bookingId) {
    const formContainer = document.createElement('div');
    formContainer.className = 'feedback-form';
    formContainer.innerHTML = `
        <h4>Please rate your experience</h4>
        <div class="rating-slider">
            <input type="range" id="rating-slider-${bookingId}" name="rating-${bookingId}" min="1" max="5" step="1" value="3" 
                oninput="document.getElementById('rating-output-${bookingId}').value = this.value" />
            <output id="rating-output-${bookingId}">3</output>
        </div>
        <textarea id="feedback-${bookingId}" placeholder="Your feedback"></textarea>
        <button id="submitFeedback-${bookingId}">Submit Feedback</button>
    `;

    // Corrected: using getElementById to attach event listener
    const submitButton = formContainer.querySelector(`#submitFeedback-${bookingId}`);
    submitButton.addEventListener('click', function() {
        submitFeedback(bookingId);
    });

    return formContainer;
}

async function submitFeedback(bookingId) {
    const ratingElement = document.getElementById(`rating-slider-${bookingId}`);
    const feedbackElement = document.getElementById(`feedback-${bookingId}`);

    const rating = parseInt(ratingElement.value);
    const feedback = feedbackElement.value.trim();
    
    if (!feedback) {
        showToast('Please provide some feedback', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/regular_user/bookings/feedback/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                booking_id: bookingId,
                rating: rating,
                feedback: feedback
            })
        });
        
        const data = await response.json();
        if (response.ok) {
            showToast('Feedback submitted successfully', 'success');
            // Disable the feedback form after submission
            const formContainer = document.querySelector(`#order-${bookingId} .feedback-form`);
            formContainer.innerHTML = '<p>Thank you for your feedback!</p>';
        } else {
            showToast(data.error || 'Failed to submit feedback', 'error');
        }
    } catch (error) {
        showToast('Failed to submit feedback', 'error');
        console.error('Error submitting feedback:', error);
    }
}