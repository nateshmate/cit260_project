
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

    // Store user info
    localStorage.setItem("first_name", data.first_name);
    localStorage.setItem("last_name", data.last_name);
    localStorage.setItem("email", username);
    localStorage.setItem("role", role);

    // Redirect based on role
    if (role === "student") {
      window.location.href = "studentdashboard.html";
    } else if (role === "faculty") {
      window.location.href = "facultydashboard.html";
    }
  } else {
    document.getElementById("loginResponse").innerText = data.error;
    document.getElementById("loginResponse").style.color = "red";
  }
}



async function createExam() {
  const examname = document.getElementById("exam").value;
  const examdate = document.getElementById("date").value;
  const examtime = document.getElementById("time").value;
  const campusname = document.querySelector('input[name="location"]:checked')?.value;
  const buildingname = document.getElementById("building").value;
  const roomnumber = document.getElementById("room").value;
  //const facultyID = document.getElementById("facultyID").value;
  //const capacity = document.getElementById("capacity").value;

  // Validate input fields
  if (!examname || !examdate || !examtime || !campusname || !buildingname || !roomnumber) {
    alert("Please fill all the required fields.");
    return;
  }

  try {
    const response = await fetch("http://127.0.0.1:5000/create_exam", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        examname,
        examdate,
        examtime,
        campusname,
        buildingname,
        roomnumber
      })
    });

    const data = await response.json();

    if (response.ok) {
      document.getElementById("responseMessage").innerText = data.message;
      document.getElementById("responseMessage").style.color = "green";
    } else {
      document.getElementById("responseMessage").innerText = data.error;
      document.getElementById("responseMessage").style.color = "red";
    }
  } catch (error) {
    console.error("Error:", error);
    document.getElementById("responseMessage").innerText = "An error occurred. Please try again.";
    document.getElementById("responseMessage").style.color = "red";
  }
}


function handleCreateExam(e) {
  e.preventDefault();
  createExam();
}
