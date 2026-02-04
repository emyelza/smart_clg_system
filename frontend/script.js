const API_BASE = "";

// --- Tab Switching ---
function showSection(sectionId) {
    document.querySelectorAll('section').forEach(s => {
        s.classList.remove('active-section');
        s.classList.add('hidden-section');
    });
    document.getElementById(`${sectionId}-section`).classList.remove('hidden-section');
    document.getElementById(`${sectionId}-section`).classList.add('active-section');

    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
}

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
    populateStudentDropdown();
    populateTeacherDropdown();
    startAdminPolling();
});

function populateStudentDropdown() {
    const select = document.getElementById('student-id-select');
    for (let i = 1; i <= 30; i++) {
        const id = `S${String(i).padStart(2, '0')}`;
        const option = document.createElement('option');
        option.value = id;
        option.innerText = `Student ${id}`;
        select.appendChild(option);
    }
}

function populateTeacherDropdown() {
    const select = document.getElementById('teacher-select');
    // Hardcoded from simulator config
    const teachers = ["Prof. Smith", "Dr. Rao"];
    teachers.forEach(t => {
        const option = document.createElement('option');
        option.value = t;
        option.innerText = t;
        select.appendChild(option);
    });
}

// --- Student Functions ---
async function checkClassLocation() {
    // For MVP, location is same for all students (based on current subject)
    const resultBox = document.getElementById('class-info');
    resultBox.innerHTML = '<span class="placeholder">Loading...</span>';

    try {
        const res = await fetch(`${API_BASE}/student/status`);
        if (!res.ok) throw new Error("API Error");
        const data = await res.json();

        if (data.class_status === "ONGOING") {
            resultBox.innerHTML = `
                <div>
                    <div style="font-size: 1.2rem; color: var(--text-main)">${data.class}</div>
                    <div style="color: var(--primary)">${data.room}</div>
                    <div style="font-size: 0.9rem; color: var(--text-muted)">Teacher: ${data.teacher}</div>
                </div>
            `;
        } else {
            resultBox.innerHTML = `<span style="color: #ef4444">Class Cancelled</span>`;
        }
    } catch (e) {
        resultBox.innerHTML = "Error fetching data.";
    }
}

async function checkAttendance() {
    const studentId = document.getElementById('student-id-select').value;
    const resultBox = document.getElementById('attendance-info');
    resultBox.innerHTML = '<span class="placeholder">Loading...</span>';

    try {
        const res = await fetch(`${API_BASE}/student/attendance/${studentId}`);
        if (!res.ok) throw new Error("API Error");
        const data = await res.json();

        // Color code based on percentage
        let color = '#22c55e'; // Green
        if (data.pct < 75) color = '#ef4444'; // Red
        else if (data.pct < 85) color = '#eab308'; // Yellow

        resultBox.innerHTML = `
            <div style="font-size: 1.5rem; color: ${color}; font-weight: bold">
                ${data.pct}%
            </div>
            <div style="font-size: 0.8rem; margin-top: 5px">
                Attended: ${data.attended}/${data.total}
            </div>
        `;
    } catch (e) {
        resultBox.innerHTML = "Error fetching data.";
    }
}

async function locateTeacher() {
    const teacherName = document.getElementById('teacher-select').value;
    const resultBox = document.getElementById('teacher-location-box');
    resultBox.innerHTML = '<span class="placeholder">Locating...</span>';

    try {
        // Reuse status endpoint since it has the live teacher info
        const res = await fetch(`${API_BASE}/student/status`);
        if (!res.ok) throw new Error("API Error");
        const data = await res.json();

        // Check if the selected teacher is the one currently in class
        if (data.teacher === teacherName && data.class_status === "ONGOING") {
            resultBox.innerHTML = `
                <div>
                    <div style="font-size: 1.2rem; color: var(--text-main)">${data.room}</div>
                    <div style="font-size: 0.9rem; color: var(--primary)">Teaching: ${data.class}</div>
                </div>
            `;
        } else {
            // In a real app we'd need a specific endpoint, but for MVP:
            resultBox.innerHTML = `<span style="color: var(--text-muted)">Not in a class currently (Free Period)</span>`;
        }

    } catch (e) {
        resultBox.innerHTML = "Error fetching data.";
    }
}

// --- Admin Functions ---
let pollingInterval;

function startAdminPolling() {
    // Poll every 2 seconds
    updateDashboard();
    pollingInterval = setInterval(updateDashboard, 2000);
}

async function updateDashboard() {
    // Only fetch if Admin section is active (optimization)
    const adminSection = document.getElementById('admin-section');
    if (adminSection.classList.contains('hidden-section')) return;

    try {
        const res = await fetch(`${API_BASE}/admin/dashboard`);
        const data = await res.json();

        document.getElementById('live-class').innerText = data.current_class;
        document.getElementById('live-status').innerText = data.status;
        document.getElementById('live-count').innerText = data.students_present;
        document.getElementById('live-pct').innerText = `${data.overall_attendance_pct}%`;

        // Dynamic status color
        const statusEl = document.getElementById('live-status');
        if (data.status === "ONGOING") statusEl.style.color = "#22c55e";
        else statusEl.style.color = "#ef4444";

    } catch (e) {
        console.error("Polling error", e);
    }
}

// --- Chatbot ---
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const msgText = input.value.trim();
    if (!msgText) return;

    // Add User Message
    addMessage(msgText, 'user');
    input.value = '';

    try {
        const res = await fetch(`${API_BASE}/admin/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msgText })
        });
        const data = await res.json();

        // Add AI Message
        addMessage(data.response, 'ai');

    } catch (e) {
        addMessage("Sorry, I couldn't reach the server.", 'ai');
    }
}

function addMessage(text, sender) {
    const history = document.getElementById('chat-history');
    const div = document.createElement('div');
    div.classList.add('chat-msg', sender);
    div.innerText = text;
    history.appendChild(div);
    history.scrollTop = history.scrollHeight;
}

// Enter key for chat
document.getElementById('chat-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
