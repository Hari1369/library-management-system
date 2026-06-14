function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

function getOtp() {
    const email = document.getElementById('email').value;
    if (!email) { alert('Please enter your email'); return; }

    fetch("{% url 'send_otp' %}", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ email: email })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            document.getElementById('step1').style.display = 'none';
            document.getElementById('step2').style.display = 'block';
        } else {
            alert(data.message || 'Failed to send OTP');
        }
    })
    .catch(() => alert('Something went wrong'));
}

function verifyOtp() {
    const email = document.getElementById('email').value;
    const otp = document.getElementById('otp').value;
    if (!otp) { alert('Please enter the OTP'); return; }

    fetch("{% url 'verify_otp' %}", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ email: email, otp: otp })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            document.getElementById('step2').style.display = 'none';
            document.getElementById('step3').style.display = 'block';
        } else {
            alert(data.message || 'Invalid OTP');
        }
    })
    .catch(() => alert('Something went wrong'));
}

function submitPassword() {
    const email = document.getElementById('email').value;
    const otp = document.getElementById('otp').value;
    const new_password = document.getElementById('new_password').value;
    const confirm_password = document.getElementById('confirm_password').value;

    if (!new_password || !confirm_password) { alert('Please fill both password fields'); return; }
    if (new_password !== confirm_password) { alert('Passwords do not match'); return; }

    fetch("{% url 'reset_password' %}", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ email: email, otp: otp, new_password: new_password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert('Password reset successful! Please login.');
            window.location.href = "{% url 'login' %}";
        } else {
            alert(data.message || 'Failed to reset password');
        }
    })
    .catch(() => alert('Something went wrong'));
}