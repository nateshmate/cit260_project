async function createAccount() {
    const first_name = document.getElementById("firstName").value;
    const last_name = document.getElementById("lastName").value;
    const role = document.getElementById("createRole").value;
    const username = document.getElementById("createEmail").value;
    const password = document.getElementById("createPassword").value;

    const response = await fetch("http://127.0.0.1:5000/create_account", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ first_name, last_name, role, username, password })
    });

    const data = await response.json();
    
    if (response.ok) {
        document.getElementById("createResponse").innerText = data.message;
        document.getElementById("createResponse").style.color = "green"; 
    } else {
        document.getElementById("createResponse").innerText = data.error;
        document.getElementById("createResponse").style.color = "red"; 
    }
}

async function login() {
    const role = document.getElementById("loginRole").value;
    const username = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;

    const response = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role, username, password })
    });

    const data = await response.json();
    
    if (response.ok) {
        document.getElementById("loginResponse").innerText = data.message;
        document.getElementById("loginResponse").style.color = "green"; 
    } else {
        document.getElementById("loginResponse").innerText = data.error;
        document.getElementById("loginResponse").style.color = "red"; 
    }
}

