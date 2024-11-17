const FrmLogin = document.getElementById('frm-login');
const FrmRegister = document.getElementById('frm-reg');
const LogOutUser = document.getElementById('logout');

/* -------------------Register User----------------------- */
async function registerUser(username, password){
    console.log(`Register user ${username} ${password}`);
    const regData = {
        username: username,
        password: password
    };

    const response = await fetch('/register', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify(regData) // Convert the data to JSON format
    });

    const data = await response.json();
    if (data.message != "") {
        console.error(`Message: ${data.message}`);
    }
}

FrmRegister.addEventListener("submit", function(event){
    console.log('RegisterForm submitted.');
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    registerUser(username, password);
});
/* -------------------Register User------------------------ */

/* ---------------------Login User------------------------- */
async function loginUser(loginUserName, LoginPassword){
    console.log(`Login user ${loginUserName} ${LoginPassword}`);
    const loginData = {
        username: loginUserName,
        password: LoginPassword
    };

    const response = await fetch('/login', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify(loginData) // Convert the data to JSON format
    });

    const loginResponse = await response.json();
    if (loginResponse.message != "") {
        console.error(`Message: ${loginResponse.message}`);
    }
    //get response from /login
    window.location.href = "domain.html";
    //iframe
}


FrmLogin.addEventListener("submit", function(event){
    console.log('LoginForm submitted.');
    event.preventDefault();
    const loginUserName = document.getElementById('login-username').value;
    const loginPassword = document.getElementById('login-password').value;

    loginUser(loginUserName, loginPassword);
});
/* ---------------------Login User------------------------- */


// Function to toggle between Register and Login forms
function toggleForms() {
    var regForm = document.getElementById("frm-reg");
    var loginForm = document.getElementById("frm-login");
    var switchFormBtn = document.getElementById("switchFormBtn");
    var switchBackBtn = document.getElementById("switchBackBtn");

    // Toggle form visibility
    if (regForm.style.display !== "none") {
        regForm.style.display = "none"; // Hide register form
        loginForm.style.display = "block"; // Show login form
        switchFormBtn.style.display = "none"; // Hide "Already Registered" button
        switchBackBtn.style.display = "inline-block"; // Show "New User" button
    } else {
        regForm.style.display = "block"; // Show register form
        loginForm.style.display = "none"; // Hide login form
        switchFormBtn.style.display = "inline-block"; // Show "Already Registered" button
        switchBackBtn.style.display = "none"; // Hide "New User" button
    }
}


function displayFileName() {
    var fileInput = document.getElementById('file-upload');
    var fileName = fileInput.files.length > 0 ? fileInput.files[0].name : 'No file selected';
    document.getElementById('file-name').textContent = 'Selected file: ' + fileName;
}
