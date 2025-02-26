from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Step 1: Initialize Flask App & Database
db = SQLAlchemy()  

def initialize_quizdom_app():
    app_instance = Flask(__name__, template_folder="templates")
    app_instance.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizdomdata.db'  
    app_instance.config['CHART_FOLDER'] = os.path.join('static', 'charts')
    os.makedirs(app_instance.config['CHART_FOLDER'], exist_ok=True)
    app_instance.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app_instance.config['SECRET_KEY'] = 'quizdom123'

    db.init_app(app_instance)
    return app_instance

# Step 2: Create an Instance of Flask App
app = initialize_quizdom_app()

# Step 3: Define Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    scores = db.relationship('Score', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    chapters = db.relationship('Chapter', back_populates='subject', cascade="all, delete-orphan")

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

    subject = db.relationship('Subject', back_populates='chapters')
    quiz = db.relationship('Quiz', back_populates='chapter', cascade="all, delete")

class Quiz(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.DateTime, default=datetime.utcnow)
    time_duration = db.Column(db.Integer, nullable=False)
    remarks = db.Column(db.Text, nullable=False)

    questions = db.relationship('Question', back_populates='quiz', cascade="all, delete")
    chapter = db.relationship('Chapter', back_populates='quiz')
    scores = db.relationship('Score', back_populates='quiz', cascade="all, delete")

class Question(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(100), nullable=False)
    option2 = db.Column(db.String(100), nullable=False)
    option3 = db.Column(db.String(100), nullable=False)
    option4 = db.Column(db.String(100), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)  

    quiz = db.relationship('Quiz', back_populates='questions')

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date_taken = db.Column(db.DateTime, default=datetime.utcnow)
    time_taken = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='scores')
    quiz = db.relationship('Quiz', back_populates='scores')

# Step 4: Create an Admin User (Avoiding Duplicate Admin Creation)
def create_admin_user():
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                fullname='Admin User',
                qualification='Admin',
                dob=datetime.strptime('1990-01-01', '%Y-%m-%d').date()
            )
            admin.set_password('admin123')         
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created!")
        else:
            # Update the admin password if it already exists
            admin.set_password('admin123')
            db.session.commit()
            print("⚠️ Admin user already exists.")


# Step 5: Initialize the Database (Run Once)
app.app_context().push()
with app.app_context():
    db.create_all()
    create_admin_user()

# Step 6: Define Application Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/Admin-Login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')  
        password = request.form['password']
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if user and user.check_password(password):  
            if user.username == 'admin': 
                session['username'] = 'admin'
                return redirect(url_for('admin_dashboard'))  
            else:
                return render_template('admin_login.html', error='Invalid admin credentials')
        else:
            return render_template('admin_login.html', error='Invalid username/email or password')
    return render_template('admin_login.html')

@app.route('/User-Registration', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        fullname = request.form['fullname']
        qualification = request.form['qualification']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
        password = request.form['password']
        # Check if user already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            if not existing_user.is_active:  # Check if the user is blocked
                return render_template('user_registration.html', error="This account is blocked. Please contact the admin.")
            return render_template('user_registration.html', error="Username or Email already exists!")
        # Create new user
        user = User(username=username, email=email, fullname=fullname, qualification=qualification, dob=dob, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        # Redirect to the login page after successful registration
        return redirect(url_for('user_login')) 
    return render_template('user_registration.html')

@app.route('/User-Login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')  
        password = request.form['password']
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if user and user.check_password(password): 
            if not user.is_active:  # Check if the user is blocked
                return render_template('user_login.html', error='Your account is blocked. Please contact the admin.')
            session['username'] = user.username 
            session['user_id'] = user.id
            return redirect(url_for('user_dashboard'))  
        else:
            return render_template('user_login.html', error='Invalid username/email or password')
    return render_template('user_login.html')

@app.route('/Admin-Dashboard')
def admin_dashboard():
    if session.get('username') != 'admin': 
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/Admin-Summary', methods=['GET', 'POST'])
def admin_summary():
    if session.get('username') != 'admin':
        return redirect(url_for('admin_login'))

    subject_attempts = db.session.query(Subject.name, db.func.count(Score.user_id)).join(Quiz, Score.quiz_id == Quiz.id).join(Chapter, Quiz.chapter_id == Chapter.id).join(Subject, Chapter.subject_id == Subject.id).group_by(Subject.name).all()
    sub_dict = dict(subject_attempts)

    topscorers = db.session.query(Subject.name, db.func.max(Score.score)).join(Quiz, Score.quiz_id == Quiz.id).join(Chapter, Quiz.chapter_id == Chapter.id).join(Subject, Chapter.subject_id == Subject.id).group_by(Subject.name).all()
    top_dict = dict(topscorers)

    # Convert scores to percentages
    bar_labels = list(top_dict.keys())
    bar_values = [min(100, (score / len(Quiz.query.filter_by(id=Score.quiz_id).first().questions) * 100)) if Quiz.query.filter_by(id=Score.quiz_id).first() else 0 for score in top_dict.values()]

    pie_labels = []
    pie_values = []
    for key, value in sub_dict.items():
        if value > 0:
            pie_labels.append(key)
            pie_values.append(value)

    # Top scores bar chart
    plt.figure(figsize=(8, 6), facecolor='#E0FFFF')
    sns.barplot(x=bar_labels, y=bar_values)
    plt.xlabel('Subjects')
    plt.ylabel('Top Scores (%)')  # Update y-axis label to indicate percentages
    plt.title('Top Scores by Subject')
    bar_chart_path = os.path.join(app.config['CHART_FOLDER'], 'bar_chart.png')
    plt.savefig(bar_chart_path)
    plt.close()

    bar_chart_url = url_for('static', filename='charts/bar_chart.png')

    # Pie chart for subject-wise attempts
    plt.figure(figsize=(8, 6), facecolor='#E0FFFF')
    plt.pie(pie_values, labels=pie_labels, autopct='%1.1f%%')
    plt.axis('equal')
    plt.title('Subject-wise User Attempts')
    pie_chart_path = os.path.join(app.config['CHART_FOLDER'], 'pie_chart.png')
    plt.savefig(pie_chart_path)
    plt.close()

    pie_chart_url = url_for('static', filename='charts/pie_chart.png')

    return render_template('admin_summary.html', bar_chart_url=bar_chart_url, pie_chart_url=pie_chart_url)
    return render_template('admin_summary.html', bar_chart_url=bar_chart_url, pie_chart_url=pie_chart_url)

@app.route('/Manage-Subjects')
def manage_subjects():
    search_query = request.args.get('search', '').lower()
    subjects = Subject.query.filter(
        (Subject.name.ilike(f'%{search_query}%')) |
        (Subject.description.ilike(f'%{search_query}%'))
    ).all()
    return render_template('subject_management.html', subjects=subjects)

@app.route('/New-Subject', methods=['GET', 'POST'])
def new_subject():
    if request.method == 'POST':
        sub_name = request.form['name']
        sub_description = request.form['description']
        subject = Subject(name=sub_name, description=sub_description)
        db.session.add(subject)
        db.session.commit()
        return redirect(url_for('manage_subjects'))
    return render_template('subject_management.html')

@app.route('/Edit-Subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if request.method == 'POST':
        subject.name = request.form['name']
        subject.description = request.form['description']
        db.session.commit()
        return redirect(url_for('manage_subjects'))
    return render_template('subject_management.html')  

@app.route('/Delete-Subject/<int:subject_id>')
def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('manage_subjects')) 

@app.route('/New-Chapter/<int:subject_id>', methods=['GET', 'POST'])
def new_chapter(subject_id):
    subject = Subject.query.get(subject_id)
    if request.method == 'POST':
        chap_name = request.form['name']
        chap_description = request.form['description']
        chapter = Chapter(title=chap_name, description=chap_description, subject=subject)
        db.session.add(chapter)
        db.session.commit()
        return redirect(url_for('manage_subjects'))
    return render_template('subject_management.html')     

@app.route('/Edit-Chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if request.method == 'POST':
        chapter.title = request.form['name']
        chapter.description = request.form['description']
        db.session.commit()
        return redirect(url_for('manage_subjects'))
    return render_template('subject_management.html')  

@app.route('/Delete-Chapter/<int:chapter_id>')
def delete_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('manage_subjects'))  

@app.route('/Manage-Quizzes')
def manage_quizzes():
    search_query = request.args.get('search', '').lower()
    quizzes = Quiz.query.join(Chapter).join(Subject).filter(
        (Quiz.title.ilike(f'%{search_query}%')) |
        (Chapter.title.ilike(f'%{search_query}%')) |
        (Subject.name.ilike(f'%{search_query}%'))
    ).all()
    chapters = Chapter.query.all()
    return render_template('quiz_management.html', quizzes=quizzes, chapters=chapters)

@app.route('/New-Quiz', methods=['GET', 'POST'])
def new_quiz():
    if request.method == 'POST':
        quiz_title = request.form['title']
        chapter_id = request.form['chapter_id']
        date_of_quiz = datetime.strptime(request.form['date_of_quiz'], '%Y-%m-%d')  # Convert string to datetime
        # Get hours and minutes from the form
        try:
            time_hours = int(request.form['time_hours'])
            time_minutes = int(request.form['time_minutes'])
            time_duration = time_hours * 60 + time_minutes  # Convert to total minutes
        except (ValueError, KeyError):
            return render_template('quiz_management.html', error="Invalid time duration. Please enter valid hours and minutes.")

        remarks = request.form['remarks']
        quiz = Quiz(title=quiz_title, chapter_id=chapter_id, date_of_quiz=date_of_quiz, time_duration=time_duration, remarks=remarks)
        db.session.add(quiz)
        db.session.commit()
        return redirect(url_for('manage_quizzes'))
    return render_template('quiz_management.html')

@app.route('/Edit-Quiz/<int:quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if request.method == 'POST':
        quiz.title = request.form['title']
        quiz.chapter_id = request.form['chapter_id']
        quiz.date_of_quiz = datetime.strptime(request.form['date_of_quiz'], '%Y-%m-%d')
        
        # Convert hours and minutes to total minutes for time_duration
        time_hours = int(request.form['time_hours'])
        time_minutes = int(request.form['time_minutes'])
        quiz.time_duration = time_hours * 60 + time_minutes
        
        quiz.remarks = request.form['remarks']
        db.session.commit()
        return redirect(url_for('manage_quizzes'))
    return render_template('quiz_management.html')

@app.route('/Delete-Quiz/<int:quiz_id>')
def delete_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for('manage_quizzes'))

@app.route('/New-Question/<int:quiz_id>', methods=['GET', 'POST'])
def new_question(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if request.method == 'POST':
        question_text = request.form['question_text']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_option = request.form['correct_option']
        question = Question(quiz_id=quiz_id, question_text=question_text, option1=option1, option2=option2, option3=option3, option4=option4, correct_option=correct_option)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('manage_quizzes'))
    return render_template('quiz_management.html')

@app.route('/Edit-Question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get(question_id)
    if request.method == 'POST':
        question.question_text = request.form['question_text']
        question.option1 = request.form['option1']
        question.option2 = request.form['option2']
        question.option3 = request.form['option3']
        question.option4 = request.form['option4']
        question.correct_option = request.form['correct_option']
        db.session.commit()
        return redirect(url_for('manage_quizzes'))
    return render_template('edit_question.html', question=question)

@app.route('/Delete-Question/<int:question_id>')
def delete_question(question_id):
    question = Question.query.get(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('manage_quizzes'))    

@app.route('/Manage-Users')
def manage_users():
    search_query = request.args.get('search', '').lower()
    users = User.query.filter(
        (User.username.ilike(f'%{search_query}%')) |
        (User.email.ilike(f'%{search_query}%')) |
        (User.fullname.ilike(f'%{search_query}%'))
    ).all()
    return render_template('user_management.html', users=users)

@app.route('/Block-User/<int:user_id>', methods=['POST'])
def block_user(user_id):
    if session.get('username') != 'admin':
        return redirect(url_for('admin_login'))
    
    user = User.query.get(user_id)
    if user:
        user.is_active = not user.is_active  # Toggle the active status
        db.session.commit()
        flash(f'User {"unblocked" if user.is_active else "blocked"} successfully', 'success')
    else:
        flash('User not found', 'error')
    
    return redirect(url_for('manage_users'))

@app.route('/User-Dashboard')
def user_dashboard():
    if session.get('username') is None:  
        return redirect(url_for('user_login')) 
    return render_template('user_dashboard.html')

@app.route('/User-Summary')
def user_summary():
    if session.get('username') is None:
        return redirect(url_for('user_login'))

    user_id = session['user_id']

    # Subject-wise top scores for the user
    subject_top_scores = db.session.query(
        Subject.name,
        db.func.max(Score.score).label('top_score')
    ).join(Quiz, Score.quiz_id == Quiz.id)\
     .join(Chapter, Quiz.chapter_id == Chapter.id)\
     .join(Subject, Chapter.subject_id == Subject.id)\
     .filter(Score.user_id == user_id)\
     .group_by(Subject.name)\
     .all()

    # Convert scores to percentages
    top_score_labels = [subject.name for subject in subject_top_scores]
    top_score_values = [min(100, (subject.top_score / len(Quiz.query.filter_by(id=Score.quiz_id).first().questions)) * 100) if Quiz.query.filter_by(id=Score.quiz_id).first() else 0 for subject in subject_top_scores]

    # Subject-wise quizzes attempted by the user
    subject_attempts = db.session.query(
        Subject.name,
        db.func.count(Score.quiz_id).label('attempts')
    ).join(Quiz, Score.quiz_id == Quiz.id)\
     .join(Chapter, Quiz.chapter_id == Chapter.id)\
     .join(Subject, Chapter.subject_id == Subject.id)\
     .filter(Score.user_id == user_id)\
     .group_by(Subject.name)\
     .all()

    attempts_labels = [subject.name for subject in subject_attempts]
    attempts_values = [subject.attempts for subject in subject_attempts]

    # Top scores bar chart
    plt.figure(figsize=(8, 6), facecolor='#E5F0F8')
    sns.barplot(x=top_score_labels, y=top_score_values)
    plt.xlabel('Subjects')
    plt.ylabel('Top Scores (%)')  # Update y-axis label to indicate percentages
    plt.title('Subject-wise Top Scores')
    top_scores_chart_path = os.path.join(app.config['CHART_FOLDER'], 'top_scores_chart.png')
    plt.savefig(top_scores_chart_path)
    plt.close()

    # Attempts shown in pie chart
    plt.figure(figsize=(8, 6), facecolor='#E5F0F8')
    plt.pie(attempts_values, labels=attempts_labels, autopct='%1.1f%%')
    plt.axis('equal')
    plt.title('Subject-wise Quizzes Attempted')
    attempts_chart_path = os.path.join(app.config['CHART_FOLDER'], 'attempts_chart.png')
    plt.savefig(attempts_chart_path)
    plt.close()

    # URLs for the charts
    top_scores_chart_url = url_for('static', filename='charts/top_scores_chart.png')
    attempts_chart_url = url_for('static', filename='charts/attempts_chart.png')

    return render_template('user_summary.html', top_scores_chart_url=top_scores_chart_url, attempts_chart_url=attempts_chart_url)  

@app.route('/Upcomming-Quizzes')
def upcomming_quizzes():
    if session.get('username') is None:
        return redirect(url_for('user_login'))

    # Get the search query from the URL parameters
    search_query = request.args.get('search', '').lower()
    
    # Fetch quizzes based on the search query
    quizzes = Quiz.query.join(Chapter).join(Subject).filter(
        (Quiz.title.ilike(f'%{search_query}%')) |  # Search by quiz title
        (Chapter.title.ilike(f'%{search_query}%')) |  # Search by chapter title
        (Subject.name.ilike(f'%{search_query}%'))  # Search by subject name
    ).all()
    
    return render_template('upcomming_quizzes.html', quizzes=quizzes)

@app.route('/Attempt-Quiz/<int:quiz_id>', methods=['GET', 'POST'])
def attempt_quiz(quiz_id):
    if session.get('username') is None:
        return redirect(url_for('user_login'))

    quiz = Quiz.query.get(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    # Check if the user has already attempted this quiz
    user_id = session['user_id']
    existing_score = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if existing_score:
        flash('You have already attempted this quiz.', 'info')
        return redirect(url_for('upcomming_quizzes'))

    if 'start_time' not in session:
        session['start_time'] = datetime.now().isoformat()

    if request.method == 'POST':
        score = 0
        for question in questions:
            answer_marked = request.form.get(f'question-{question.id}')
            print(f"Question ID: {question.id}, Correct Option: {question.correct_option}, User Answer: {answer_marked}")  # Debugging
            if answer_marked and answer_marked.strip() == str(question.correct_option).strip():
                score += 1

        # Track time taken
        start_time = datetime.fromisoformat(session.get('start_time'))
        end_time = datetime.now()
        time_taken_seconds = int((end_time - start_time).total_seconds())

        # Save Score
        final_score = Score(
            quiz_id=quiz_id,
            user_id=user_id,
            score=score,
            date_taken=datetime.utcnow(),
            time_taken=time_taken_seconds,
            completed=True
        )
        
        db.session.add(final_score)
        db.session.commit()
        session.pop('start_time', None)

        print(f"Final Score: Quiz ID={quiz_id}, User ID={user_id}, Score={score}, Time Taken={time_taken_seconds}")  # Debugging

        return redirect(url_for('upcomming_quizzes'))

    return render_template('attempt_quiz.html', quiz=quiz, questions=questions, time=quiz.time_duration)

@app.route('/Scorecard')
def scorecard():
    if session.get('username') is None:
        return redirect(url_for('user_login'))

    search_query = request.args.get('search', '').lower()
    user_id = session['user_id']

    # Fetch scores along with total questions in each quiz
    scores = db.session.query(Score, Quiz).join(Quiz).join(Chapter).join(Subject).filter(
        (Score.user_id == user_id)
    ).all()

    # Prepare the modified data including percentage
    score_data = []
    for score, quiz in scores:
        total_questions = len(quiz.questions)
        if total_questions > 0:
            percentage_score = int((score.score / total_questions) * 100)
        else:
            percentage_score = 0  # Avoid division by zero

        score_data.append({
            'subject': quiz.chapter.subject.name,
            'chapter': quiz.chapter.title,
            'score': score.score,
            'total_questions': total_questions,
            'percentage': percentage_score,
            'date_taken': score.date_taken.strftime('%d/%m/%Y'),
            'time_taken': score.time_taken
        })

    # Filter scores based on search query (subject, chapter, quiz title, or percentage)
    if search_query:
        filtered_scores = []
        for score in score_data:
            # Check if the search query matches subject, chapter, or quiz title
            if (search_query in score['subject'].lower() or
                search_query in score['chapter'].lower() or
                search_query in str(score['score']).lower() or
                search_query in str(score['total_questions']).lower()):
                filtered_scores.append(score)
            # Check if the search query is a percentage and matches the score's percentage
            elif search_query.endswith('%'):
                try:
                    # Remove the '%' and convert to integer
                    percentage_query = int(search_query[:-1])
                    if score['percentage'] == percentage_query:
                        filtered_scores.append(score)
                except ValueError:
                    # If the search query is not a valid percentage, ignore it
                    pass
        score_data = filtered_scores

    return render_template('scorecard.html', scores=score_data)

# Step 7: Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)