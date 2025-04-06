// script.js
const users = {
    'admin': 'password123',
    'user1': 'pass123'
};

function switchMethod(method) {
    document.querySelectorAll('.login-option').forEach(option => {
        option.classList.remove('active');
    });
    event.currentTarget.classList.add('active');

    document.querySelectorAll('.login-form').forEach(form => {
        form.classList.remove('active');
    });
    if (method === 'password') {
        document.getElementById('passwordForm').classList.add('active');
    } else {
        document.getElementById('faceForm').classList.add('active');
    }
}

function showMessage(text, type) {
    const message = document.getElementById('message');
    message.textContent = text;
    message.className = `message ${type}`;
    message.style.display = 'block';
    setTimeout(() => {
        message.style.display = 'none';
    }, 3000);
}

document.getElementById('passwordForm').onsubmit = function(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (users[username] && users[username] === password) {
        showMessage('Login successful! Redirecting...', 'success');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1500);
    } else {
        showMessage('Invalid username or password', 'error');
    }
};

// Updated face recognition function
function startFaceRecognition() {
    // Create a hidden form
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = 'http://localhost:5000/face-login';
    document.body.appendChild(form);
    
    showMessage('Starting face recognition...', 'success');
    
    // Submit the form
    form.submit();
}

// Updated registration function
function registerNewUser() {
    // Create a hidden form
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = 'http://localhost:5000/register-face';
    document.body.appendChild(form);
    
    showMessage('Starting registration process...', 'success');
    
    // Submit the form
    form.submit();
}
