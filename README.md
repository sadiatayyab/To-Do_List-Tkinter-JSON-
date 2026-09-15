# 🚀 TaskFlow Pro – Daily Task Manager

A modern desktop-based **Task Management Application** built using **Python and Tkinter** during my internship at **Skillify**.

TaskFlow Pro helps users organize daily tasks, set priorities, track progress, manage deadlines, and monitor productivity through a clean and user-friendly interface.

---

## 📌 Internship Project

**Organization:** Skillify  
**Project:** TaskFlow Pro – Daily Task Manager  
**Technology:** Python + Tkinter  
**Data Storage:** JSON  
**Project Type:** Desktop Application  

This project was developed as part of my internship at **Skillify**, with a focus on Python programming, GUI development, file handling, data management, input validation, and building a practical desktop application.

---

## ✨ Features

### 📊 Dashboard

The dashboard provides an overview of your tasks and productivity.

- Total Tasks
- Active Tasks
- In Progress Tasks
- Completed Tasks
- Completion Percentage
- Recent Tasks
- Quick Actions
- Current Date
- Productivity overview

---

### ➕ Add Tasks

Users can easily create new tasks with:

- Task Title
- Description
- Category
- Priority
- Status
- Due Date
- Due Time

#### 📅 Date Selection

The application includes a calendar-based date picker instead of requiring users to manually enter dates.

#### 🕐 Time Selection

Users can select:

- Hour
- Minute
- AM/PM

instead of manually entering the time.

---

### ✏️ Edit Tasks

Existing tasks can be edited and updated.

Users can modify:

- Title
- Description
- Category
- Priority
- Status
- Due Date
- Due Time

---

### 🗑️ Delete Tasks

The application provides task deletion functionality.

Users can:

- Delete an individual task
- Delete completed tasks
- Confirm before deleting important data

---

### ✅ Task Completion

Tasks can be marked as completed directly from the task management interface.

The dashboard automatically updates the statistics after task changes.

---

## 🏷️ Task Categories

TaskFlow Pro supports multiple categories:

- General
- Study
- Work
- Personal
- Shopping
- Health
- Finance
- Travel
- Fitness
- Family
- Projects
- Meetings
- Learning
- Home
- Errands

---

## 🚦 Priority Levels

Each task can have one of the following priorities:

- 🟢 Low
- 🟡 Medium
- 🔴 High
- 🚨 Urgent

---

## 📌 Task Status

Tasks can have three different statuses:

- Pending
- In Progress
- Completed

---

## 🔍 Search & Filtering

The task management page allows users to quickly find tasks.

### Search

Search tasks using:

- Task title
- Description

### Filters

Tasks can also be filtered by:

- Category
- Status

This makes it easier to manage a large number of tasks.

---

## 💾 Automatic JSON Data Storage

TaskFlow Pro uses a JSON file for local data storage.

When tasks are saved, they are automatically stored in:

```text
tasks.json

The application loads the saved tasks when it starts again.

Example:

[
    {
        "id": 1,
        "title": "Complete Assignment",
        "description": "Finish the web technology assignment",
        "category": "Study",
        "priority": "High",
        "status": "Pending",
        "due_date": "2026-09-16",
        "due_time": "18:00",
        "created_at": "2026-09-15T10:00:00",
        "updated_at": "2026-09-15T10:00:00"
    }
]

This allows the application to work without requiring an external database.
```

## 📈 Reports

TaskFlow Pro provides task reports and summary information.

Users can view:

Total tasks
Completed tasks
Pending tasks
In-progress tasks
Completion percentage
Task statistics

Reports can also be exported for further use.

Supported Export Formats
TXT
CSV
JSON

## 💬 Feedback System

The application includes a feedback section where users can submit:

Name
Email
Feedback/message

Feedback is stored locally in:

feedback.json

## 🌓 Light & Dark Theme

TaskFlow Pro includes both:

☀️ Light Mode
🌙 Dark Mode

Users can switch between themes according to their preference.

## 🛡️ Input Validation

The application validates user input before saving tasks.

Examples include:

Required task title
Valid date format
Valid time format
Valid task category
Valid priority
Valid status

This helps prevent incorrect or incomplete task data.

## 🖥️ User Interface

The application was designed with a modern desktop interface using Tkinter.

The interface includes:

Sidebar navigation
Dashboard cards
Modern buttons
Form layouts
Task tables
Search controls
Filters
Date picker
Time picker
Light/Dark themes
Responsive window layout


## 🛠️ Technologies Used
Programming Language

Python

GUI Framework

Tkinter

Data Storage

JSON

File Handling

Python's built-in file handling and JSON modules.

Export
CSV
JSON
TXT


## 📂 Project Structure

TaskFlow-Pro/
│
├── taskflow_pro_fixed.py
├── tasks.json
├── feedback.json
└── README.md

tasks.json is automatically created when tasks are saved.

feedback.json is created when feedback is submitted.

## ⚙️ Requirements

Python 3.x is required.

Tkinter is included with most standard Python installations.

No external libraries are required for the basic application.

## ▶️ How to Run
1. Clone the Repository
git clone https://github.com/sadiatayyab/To-Do_List-Tkinter-JSON-
2. Open the Project Folder
cd TaskFlow-Pro
3. Run the Application
python taskflow_pro_fixed.py

The TaskFlow Pro desktop application will open.

##  📋 Example Tasks

The application can be used for different types of tasks, such as:

Complete university assignments
Prepare presentations
Study for exams
Attend meetings
Manage personal tasks
Track health-related reminders
Plan trips
Manage projects
Complete household errands
Track financial reminders

## 🎯 Learning Objectives

This project helped me practice and improve my understanding of:

Python programming
Object-Oriented Programming
Tkinter GUI development
Event-driven programming
JSON file handling
CRUD operations
Form validation
Search and filtering
Data organization
File export
User interface design
Application state management
Desktop application development

## 🚀 Future Improvements

Possible future improvements include:

User authentication
SQLite database integration
Task notifications
Desktop reminders
Recurring tasks
Drag-and-drop task management
Calendar view
Productivity charts
Task sorting
Automatic overdue detection
Cloud synchronization
Mobile/web version

##  Internship Project

This project was developed as part of my internship at Skillify.

The project gave me practical experience in transforming Python concepts into a functional desktop application with a focus on usability, data management, and interface design.

## 📄 License

This project was developed for educational and internship purposes.