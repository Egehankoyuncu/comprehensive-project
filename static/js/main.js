// Main JavaScript file for the Student Tutoring System

// Function to handle message read status
function markMessageAsRead(messageId) {
    fetch(`/mark-message-read/${messageId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const messageElement = document.querySelector(`#message-${messageId}`);
            if (messageElement) {
                messageElement.classList.remove('unread');
            }
        }
    });
}

// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Function to handle session status updates
function updateSessionStatus(sessionId, newStatus) {
    fetch(`/update-session-status/${sessionId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            status: newStatus
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
}

// Function to handle review submission
function submitReview(sessionId) {
    const rating = document.querySelector('#rating').value;
    const comment = document.querySelector('#comment').value;

    fetch(`/submit-review/${sessionId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            rating: rating,
            comment: comment
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
}

// Add event listeners when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Handle message read status
    const unreadMessages = document.querySelectorAll('.unread');
    unreadMessages.forEach(message => {
        message.addEventListener('click', function() {
            const messageId = this.dataset.messageId;
            markMessageAsRead(messageId);
        });
    });

    // Handle session status updates
    const statusButtons = document.querySelectorAll('.status-update');
    statusButtons.forEach(button => {
        button.addEventListener('click', function() {
            const sessionId = this.dataset.sessionId;
            const newStatus = this.dataset.status;
            updateSessionStatus(sessionId, newStatus);
        });
    });

    // Handle review submission
    const reviewForm = document.querySelector('#review-form');
    if (reviewForm) {
        reviewForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const sessionId = this.dataset.sessionId;
            submitReview(sessionId);
        });
    }
}); 