
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
  const email = localStorage.getItem("email");
  if (!email) {
    alert("User not logged in.");
    return;
  }

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
        roomnumber,
        email
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

let examsMap = {};

async function loadExams() {
  try {
    const response = await fetch("http://127.0.0.1:5000/faculty/exams");
    const exams = await response.json();
    const examSelect = document.getElementById("Exam_Name");
    if (!examSelect) return;

    examSelect.innerHTML = '<option value="">Select an exam</option>';
    exams.forEach(exam => {
      examsMap[exam.examid] = exam;
      const option = document.createElement("option");
      option.value = exam.examid;
      option.textContent = exam.examname;
      examSelect.appendChild(option);
    });
  } catch (err) {
    console.error("Failed to load exams:", err);
  }
}

function populateStudentInfo() {
  const firstName = localStorage.getItem("first_name") || "";
  const lastName = localStorage.getItem("last_name") || "";
  const email = localStorage.getItem("email") || "";

  const fullNameField = document.getElementById("Full_Name");
  const emailField = document.getElementById("Email");

  if (fullNameField) fullNameField.value = `${firstName} ${lastName}`;
  if (emailField) emailField.value = email;

  const regDate = document.getElementById("Reg_Date");
  if (regDate) regDate.value = new Date().toISOString().split("T")[0];
}

function handleExamChange() {
  const examSelect = document.getElementById("Exam_Name");
  if (!examSelect) return;

  examSelect.addEventListener("change", function () {
    const selectedExam = examsMap[this.value];
    const detailsBox = document.getElementById("examDetails");

    if (selectedExam) {
      document.getElementById("Exam_ID").value = selectedExam.examid;
      document.getElementById("examCampus").textContent = selectedExam.campusname;
      document.getElementById("examBuilding").textContent = selectedExam.buildingname;
      document.getElementById("examRoom").textContent = selectedExam.roomnumber;
      document.getElementById("examDate").textContent = selectedExam.examdate;
      document.getElementById("examTime").textContent = selectedExam.examtime;
      detailsBox.style.display = "block";
    } else {
      detailsBox.style.display = "none";
    }
  });
}

function setupExamFormSubmission() {
  const form = document.getElementById("examForm");
  if (!form) return;

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const payload = {
      email: document.getElementById("Email").value,
      Exam_ID: document.getElementById("Exam_ID").value,
      Reg_Date: document.getElementById("Reg_Date").value
    };
    

    try {
      const response = await fetch("http://127.0.0.1:5000/register_exam", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      if (response.ok) {
        alert("Registration successful!");
        window.location.href = "studentdashboard.html";
      } else {
        alert("Registration failed: " + result.error);
      }
    } catch (err) {
      console.error("Error during registration:", err);
      alert("An error occurred while registering.");
    }
  });
}

document.addEventListener("DOMContentLoaded", function () {
  if (document.getElementById("examForm")) {
    populateStudentInfo();
    loadExams();
    handleExamChange();
    setupExamFormSubmission();
  }
});
