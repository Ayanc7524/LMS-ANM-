from flask import Flask, render_template, request, redirect, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/lms'
app.secret_key = 'your_secret_key'  # Ensure this is secure and unique for your app

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the Register model
class Register(db.Model):
    __tablename__ = 'register'  # Add table name if needed
    sno = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(80), nullable=False)
    lname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)  # Store hashed passwords
    contact = db.Column(db.String(15), nullable=False)

    def __init__(self, fname, lname, email, password, contact):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.contact = contact

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

# Home route
@app.route("/")
def home():
    return render_template("index.html")

# Login route
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print("Email:", email)  # Debugging: check if email is received
        print("Password:", password)  # Debugging: check if password is received

        # Query the database to find the user
        user = Register.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.sno
            session['email'] = user.email
            session['fname'] = user.fname
            session['lname'] = user.lname

            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "danger")
    return render_template("login.html")


# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        # Retrieve the user's name from the session
        user_first_name = session.get('fname')
        user_last_name = session.get('lname')
        
        # Use the full name if you want to display it as a single string
        full_name = f"{user_first_name} {user_last_name}"
        return render_template("dashboard.html", full_name=full_name)
    
    flash("Please log in to access the dashboard", "danger")
    return redirect(url_for('login'))
@app.route('/test_dashboard')
def test_dashboard():
    return render_template("dashboard.html", full_name="Test User")


# Register route
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('repassword')
        contact = request.form.get('mobile')

        # Check if the passwords match
        if password != cpassword:
            flash("Passwords do not match", "danger")
            return render_template('register.html')

        # Create a new user entry in the database
        new_user = Register(fname=fname, lname=lname, email=email, password=password, contact=contact)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# Logout route
@app.route("/logout")
def logout():
    session.clear()  # Clears the entire session
    flash("You have been logged out", "success")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
