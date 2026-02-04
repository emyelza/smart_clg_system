import json
import time
import random
import numpy as np
from datetime import datetime
import os

# --- Configuration ---
subjects = ["CSE-2A", "DBMS"]
rooms = {"CSE-2A": "Block A - 101", "DBMS": "Block B - 204"}
teachers = {"CSE-2A": "Prof. Smith", "DBMS": "Dr. Rao"}
time_slots = ["09:00-10:00", "10:00-11:00", "11:00-12:00"]

class CollegeEnv:
    def __init__(self):
        self.current_slot_idx = 0
        self.current_subject = subjects[0]
    
    def step(self):
        # Move to next slot
        self.current_slot_idx = (self.current_slot_idx + 1) % len(time_slots)
        self.current_subject = subjects[self.current_slot_idx % len(subjects)]
        return {
            "time": time_slots[self.current_slot_idx],
            "subject": self.current_subject
        }

class TeacherAgent:
    def __init__(self, name, subject):
        self.name = name
        self.subject = subject
        
    def act(self, env_state):
        # Simple Logic: 90% chance to attend
        if random.random() < 0.9:
            return "TEACH"
        else:
            return "CANCEL"

class StudentAgent:
    def __init__(self, student_id):
        self.id = student_id
        self.attendance_record = {s: {"attended": 0, "total": 0} for s in subjects}
        self.current_attendance_pct = 100.0
    
    def act(self, class_status, subject):
        if class_status == "CANCELLED":
            return "SKIP"
        
        prob_attend = 0.95
        if self.current_attendance_pct > 80:
            prob_attend = 0.85
        elif self.current_attendance_pct < 75:
            prob_attend = 0.99
            
        return "ATTEND" if random.random() < prob_attend else "SKIP"

    def update_attendance(self, subject, action, class_status):
        if class_status == "ONGOING":
            self.attendance_record[subject]["total"] += 1
            if action == "ATTEND":
                self.attendance_record[subject]["attended"] += 1
        
        # Recalc %
        total_classes = sum(s["total"] for s in self.attendance_record.values())
        total_attended = sum(s["attended"] for s in self.attendance_record.values())
        if total_classes > 0:
            self.current_attendance_pct = (total_attended / total_classes) * 100
        else:
            self.current_attendance_pct = 100.0

class CollegeSimulation:
    def __init__(self):
        self.teacher_agents = {s: TeacherAgent(teachers[s], s) for s in subjects}
        self.students = [StudentAgent(f"S{i:02d}") for i in range(1, 31)]
        self.env = CollegeEnv()
        
        # Initial State
        self.current_state = {
            "time": "09:00-10:00",
            "class": "CSE-2A",
            "room": "Block A - 101",
            "teacher": "Prof. Smith",
            "class_status": "ONGOING",
            "students_present": 0,
            "total_students": 30
        }
        self.attendance_data = {}
        self.step() # Run one step to init data

    def step(self):
        # 1. Update Env
        env_state = self.env.step()
        curr_time = env_state["time"]
        curr_subject = env_state["subject"]
        curr_room = rooms[curr_subject]
        curr_teacher = self.teacher_agents[curr_subject]
        
        # 2. Teacher Action
        teacher_action = curr_teacher.act(env_state)
        class_status = "ONGOING" if teacher_action == "TEACH" else "CANCELLED"
        
        # 3. Student Actions
        students_present = 0
        for s in self.students:
            action = s.act(class_status, curr_subject)
            s.update_attendance(curr_subject, action, class_status)
            if action == "ATTEND" and class_status == "ONGOING":
                students_present += 1
        
        # 4. Update Memory State
        self.current_state = {
            "time": curr_time,
            "class": curr_subject,
            "room": curr_room,
            "teacher": curr_teacher.name,
            "class_status": class_status,
            "students_present": students_present,
            "total_students": len(self.students)
        }
        
        # 5. Update Attendance Data
        att_data = {}
        for s in self.students:
            att_data[s.id] = {
                "attended": sum(sub["attended"] for sub in s.attendance_record.values()),
                "total": sum(sub["total"] for sub in s.attendance_record.values()),
                "pct": round(s.current_attendance_pct, 1)
            }
        self.attendance_data = att_data
        
        print(f"[Sim] {curr_time} | {curr_subject} | {class_status} | Present: {students_present}")
