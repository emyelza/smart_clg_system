from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import threading
import time
import sys
import os

# Put project root in path so we can import simulator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.simulation import CollegeSimulation

# Configure Flask to serve frontend files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
CORS(app)

# --- Integrated Simulation ---
simulation = CollegeSimulation()

def run_simulation_loop():
    while True:
        time.sleep(5)  # 5 seconds per step
        simulation.step()

# Start Simulation Thread
sim_thread = threading.Thread(target=run_simulation_loop, daemon=True)
sim_thread.start()

# --- Routes ---
@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/api")
def read_root():
    return jsonify({"message": "Smart College Simulator (Integrated Memory)"})

@app.route("/student/status", methods=["GET"])
def get_student_status():
    return jsonify(simulation.current_state)

@app.route("/student/attendance/<student_id>", methods=["GET"])
def get_attendance(student_id):
    data = simulation.attendance_data
    if student_id not in data:
         return jsonify({"error": "Student not found"}), 404
    return jsonify({"id": student_id, **data[student_id]})

@app.route("/admin/dashboard", methods=["GET"])
def get_admin_dashboard():
    state = simulation.current_state
    attendance = simulation.attendance_data
    
    total_attended = 0
    total_classes = 0
    if attendance:
        for s in attendance.values():
            total_attended += s["attended"]
            total_classes += s["total"]
    
    overall_pct = 0
    if total_classes > 0:
        overall_pct = round((total_attended / total_classes) * 100, 1)

    return jsonify({
        "current_class": state.get("class", "N/A"),
        "status": state.get("class_status", "N/A"),
        "students_present": state.get("students_present", 0),
        "overall_attendance_pct": overall_pct
    })

@app.route("/admin/chat", methods=["POST"])
def admin_chat():
    if not request.json or 'message' not in request.json:
        abort(400)
        
    msg = request.json['message'].lower()
    state = simulation.current_state
    attendance = simulation.attendance_data
    
    response_text = "I didn't understand that. Try asking about 'low attendance', 'simulation status', or 'students present'."
    
    if "low attendance" in msg or "below 75" in msg:
        low_att_students = [sid for sid, data in attendance.items() if data["pct"] < 75]
        if low_att_students:
            response_text = f"Students with low attendance (<75%): {', '.join(low_att_students)}"
        else:
            response_text = "Good news! No students are below 75% attendance currently."
            
    elif "present" in msg or "how many" in msg:
        count = state.get("students_present", 0)
        total = state.get("total_students", 0)
        response_text = f"Currently, {count} out of {total} students are present."
        
    elif "cancelled" in msg or "class status" in msg:
        status = state.get("class_status", "UNKNOWN")
        subject = state.get("class", "Unknown Subject")
        if status == "CANCELLED":
             response_text = f"Yes, the current class ({subject}) is CANCELLED."
        else:
             response_text = f"The current class ({subject}) is ONGOING."
             
    elif "teacher" in msg or "where" in msg:
        teacher = state.get("teacher", "Unknown")
        room = state.get("room", "Unknown")
        status = state.get("class_status", "UNKNOWN")
        if status == "ONGOING":
            response_text = f"{teacher} is currently in {room}."
        else:
             response_text = f"{teacher} is currently not in class (Class Triggered Cancel)."

    return jsonify({"response": response_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
