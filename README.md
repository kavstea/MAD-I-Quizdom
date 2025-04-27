## Project Overview

<div>
  <img src="/Quizdom/images/Screenshot 2025-04-27 065356.png" width="33%" height='75px' alt="Admin Dashboard">
  <img src="/Quizdom/images/Screenshot 2025-04-27 070554.png" width="33%" height='75px' alt="User Quiz Interface">
  <img src="Quizdom/images/Screenshot 2025-04-27 070450.png" width="33%" height='75px' alt="User Scores Interface">
</div>

Quizdom acts as a web application designed to help users prepare for exams by taking quizzes on various subjects. Admins can manage users, subjects, chapters, and quizzes, while users can register, log in, attempt quizzes, and view their performance through visual summaries.

---

## Technologies Used

### Backend
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-000000?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Werkzeug](https://img.shields.io/badge/Werkzeug-000000?style=for-the-badge&logo=werkzeug&logoColor=white)

### Frontend
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)

### Data Visualization
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge)
![Seaborn](https://img.shields.io/badge/Seaborn-0C7BDC?style=for-the-badge)

---

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.7 or higher
- pip (Python package manager)

---

## Installation Steps

### 1. Install Dependencies
Install the required Python packages using `pip`:
```bash
pip install -r requirements.txt
```
If you don't have a `requirements.txt` file, you can install the dependencies manually:
```bash
pip install flask flask-sqlalchemy matplotlib seaborn werkzeug
```

### 2. Initialize the Database
Run the following command to initialize the SQLite database and create the necessary tables:
```bash
python main.py
```
This will create a `quizdomdata.db` file in your project directory, which contains the database schema and initial data.

### 3. Run the Application
Start the Flask development server:
```bash
python main.py
```
The application will be available at `http://127.0.0.1:5000`.

---

## Using the Application

### Admin Features
- **Admin Login**: Access the admin dashboard by logging in with the following credentials:
  - **Username**: `admin`
  - **Password**: `admin123`
- **Manage Users**: Block/unblock users, view user details.
- **Manage Subjects, Chapters, and Quizzes**: Add, edit, or delete subjects, chapters, and quizzes.
- **View Summary**: Visualize quiz performance using bar charts and pie charts.

### User Features
- **User Registration**: Register a new account by providing your details.
- **User Login**: Log in with your username/email and password.
- **Attempt Quizzes**: Take quizzes on various subjects and chapters.
- **View Performance**: Check your scores and visualize your performance using charts.

---

## Project Structure

```
Quizdom/                           # Root project directory
├── images/                        # Folder for app images 
├── root_folder/                   # Main folder containing app-specific files
│   ├── instance/                  # Folder for instance-specific files like the database
│   │   └── quizdomdata.db         # SQLite database file (stores user data, quiz results, etc.)
│   └── static/                    # Static files for frontend (CSS, JS, charts)
│       └── charts/                # Folder for saved/generated chart images
│           ├── attempts_chart.png  # Chart displaying attempts statistics
│           ├── bar_chart.png      # Bar chart showing quiz score distribution
│           ├── pie_chart.png      # Pie chart for subject wise quiz attempts breakdown
│           └── top_scores_chart.png # Chart for top scorers
├── templates/                     # Folder for HTML templates (views for user and admin pages)
├── README.md                      # Project documentation (setup instructions, features, etc.)
├── main.py                        # Flask application (handles routes, database, and app logic)
└── report.pdf                     # Project report (describes the project and its implementation)

```

---

## Troubleshooting
- **Database Issues**: If the database is not initialized properly, delete the `quizdomdata.db` file and restart the application.
- **Chart Generation Issues**: Ensure the `static/charts/` directory exists and has write permissions. If charts are not generated, check the Flask logs for errors.

---

<div align="center">
  <em>Thankyou!</em>
</div>  
