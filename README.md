# Smart College Simulator (RL-Based)

## Description
The Smart College Simulator models realistic student and teacher behaviors in a campus environment using Reinforcement Learning (RL) concepts. The system mimics a real-time college schedule where autonomous agents decide to attend classes, cancel lectures, or skip sessions based on internal states and rewards. This simulation powers a live dashboard for tracking class locations, attendance, and faculty status without requiring real-world sensors or manual data entry.

## Tech Stack
*   **Simulator**: Python (NumPy, Custom RL Agents)
*   **Backend**: Flask (Python)
*   **Frontend**: HTML5, CSS3, Vanilla JavaScript
*   **Data Storage**: JSON (Real-time Simulation State)

## Key Features
*   **Autonomous Campus**: Students and teachers are independent agents that make decisions dynamically, rather than following rigid hard-coded schedules.
*   **Real-Time Dashboard**: A live interface for administrators to monitor ongoing classes and attendance percentages.
*   **AI Admin Chatbot**: Natural language interface for administrators to query specific student statuses or overall campus health.
*   **Faculty Tracking**: Real-time location tracking for teachers based on their current teaching status.

## Reinforcement Learning System
The simulation uses probabilistic models and reward-based logic to drive agent behavior:

### Teacher Agents
*   **Action Space**: Teach, Cancel.
*   **Logic**: Decisions are influenced by assigned time slots and a history of previous cancellations.
*   **Reward**: +10 for teaching, -5 for cancelling.

### Student Agents
*   **Action Space**: Attend, Skip.
*   **Logic**: Decisions are based on their current attendance percentage and the status of the class (Ongoing vs Cancelled).
*   **Reward**: +5 for attending. A significant penalty (-20) is applied if attendance falls below 75%, simulating the motivation to avoid detention.

## Running Instructions
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
## Running Instructions
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Start Application**:
    ```bash
    python backend/main.py
    ```
    *Note: The Simulator runs automatically in the background.*

3.  **Access Dashboard**:
    Open your browser and navigate to:
    ```
    http://localhost:8000
    ```
