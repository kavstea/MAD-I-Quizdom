# Project Overview

Quizdom acts as a web application designed to help users prepare for exams by taking quizzes on various subjects. Admins can manage users, subjects, chapters, and quizzes, while users can register, log in, attempt quizzes, and view their performance through visual summaries.

## Technologies Used
- **Backend**: Flask, Flask-SQLAlchemy, Werkzeug Security
- **Frontend**: HTML, CSS, Bootstrap, Jinja2
- **Database**: SQLite
- **Data Visualization**: Matplotlib, Seaborn

## Prerequisites
Before running the application, ensure you have the following installed:
- **Python 3.7 or higher**
- **pip** (Python package manager)

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
- **`main.py`**: The main Flask application file containing routes, database models, and logic.
- **`templates/`**: Contains HTML templates for rendering the frontend.
- **`static/`**: Stores static files like CSS, JavaScript, and generated charts.
- **`quizdomdata.db`**: SQLite database file (created after running the application).
- **`README.md`**: This file, providing instructions for setting up and running the application.

---

## Troubleshooting
- **Database Issues**: If the database is not initialized properly, delete the `quizdomdata.db` file and restart the application.
- **Chart Generation Issues**: Ensure the `static/charts/` directory exists and has write permissions. If charts are not generated, check the Flask logs for errors.
