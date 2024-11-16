/* ---------------------Logout User------------------------- */
document.getElementById('logoutBtn').addEventListener('click', function() {
    // Send a POST request to the /logout route
    fetch('/logout', {
        method: 'POST',
        credentials: 'same-origin' // Ensure cookies (like the session) are sent
    })
    .then(response => {
        if (response.ok) {
            // Redirect to home page or login page after logout
            window.location.href = '/';
        }
    })
    .catch(error => {
        console.error('Error logging out:', error);
    });
});
/* ---------------------Logout User------------------------- */