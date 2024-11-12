$(document).ready(function() {
    // Login form validation
    $('#login-form').submit(function(e) {
        e.preventDefault();
        var username = $('#username').val();
        var password = $('#password').val();

        // Add your login validation logic here
        if (username === '' || password === '') {
            alert('Please enter both username and password');
        } else {
            // Submit the form
            $(this).unbind('submit').submit();
        }
    });

    // Domain form validation
    $('#domain-form').submit(function(e) {
        e.preventDefault();
        var domain = $('#domain').val();

        // Add your domain validation logic here
        if (domain === '') {
            alert('Please enter a domain');
        } else {
            // Submit the form
            $(this).unbind('submit').submit();
        }
    });
});