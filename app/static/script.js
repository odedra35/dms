

const username = document.getElementById('username');
const password = document.getElementById('password');
const confirmPassword = document.getElementById('confirm-password');
const submitButton = document.getElementById('submit-button');


submitButton.addEventListener('click', function(event){
    event.preventDefault();
    if (password.value != submitPassword.value) {
        alert('Passwords do not match!')
    } else {
        submitRegistration(username, password);
    }

});


async function submitRegistration(username, password) {
    data = {
        "username": username,
        "password": password
    };
    console.log(data)
    await fetch(`/register`,  {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify(data) // Convert the data to JSON format
    });
}

// Upload json file
function handleFileUpload() {
    // Get the file input element and selected file
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0]; // Get the first file selected
    
    if (!file) {
        alert("Please select a file.");
        return;
    }

    // Check if the file is a JSON file
    if (file.type !== 'application/json') {
        alert("Please upload a valid JSON file.");
        return;
    }

    // Create a new FileReader object to read the file
    const reader = new FileReader();

    // Define what happens when the file is read
    reader.onload = function(event) {
        try {
            // Parse the file content as JSON
            const jsonData = JSON.parse(event.target.result);

            // Display the JSON data on the page
            document.getElementById('output').textContent = JSON.stringify(jsonData, null, 2); // Format with indentation
        } catch (error) {
            alert("Error parsing JSON: " + error.message);
        }
    };

    // Read the content of the file as text
    reader.readAsText(file);
}