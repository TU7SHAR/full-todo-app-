from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from models import db, User
import bcrypt
import random
import smtplib
from email.mime.text import MIMEText
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email
from sqlalchemy.exc import IntegrityError
import os

auth_bp = Blueprint('auth', __name__)

# --- Helper function to send email ---
def send_otp_email(user_email, otp_code):
    # For testing: Prints to your terminal so you don't get locked out while setting up email
    print(f"\n--- TESTING: The OTP for {user_email} is: {otp_code} ---\n")
    
    # To actually send emails, you'll need to use your email and an App Password
    # Put these in your .env file later: EMAIL_USER and EMAIL_PASS
    sender_email = os.getenv('EMAIL_USER', 'your_email@gmail.com')
    sender_password = os.getenv('EMAIL_PASS', 'your_app_password')
    
    if sender_email != 'your_email@gmail.com':
        try:
            msg = MIMEText(f"Your Task Diary verification code is: {otp_code}")
            msg['Subject'] = 'Task Diary - Verify Your Email'
            msg['From'] = sender_email
            msg['To'] = user_email
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")

class RegistrationForm(FlaskForm):
    name = StringField("", validators=[DataRequired()])
    email = StringField("", validators=[DataRequired(), Email()])
    password = PasswordField("", validators=[DataRequired()])

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            hashed_pwd = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Generate 6-digit OTP
            otp_code = str(random.randint(100000, 999999))
            
            new_user = User(name=form.name.data, email=form.email.data, password=hashed_pwd, otp=otp_code, is_verified=False)
            db.session.add(new_user)
            db.session.commit()
            
            # Send Email
            send_otp_email(new_user.email, otp_code)
            
            # Temporarily store email in session to know who is verifying
            session['pending_email'] = new_user.email
            flash("OTP sent to your email!", "success")
            return redirect(url_for('auth.verify_otp'))
            
        except IntegrityError:
            db.session.rollback()
            flash("Email already registered.", "error")
            return redirect(url_for('auth.register'))
            
    return render_template('register.html', form=form)

@auth_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'pending_email' not in session:
        return redirect(url_for('auth.register'))
        
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        user = User.query.filter_by(email=session['pending_email']).first()
        
        if user and user.otp == user_otp:
            # Mark as verified, clear the OTP from database
            user.is_verified = True
            user.otp = None
            db.session.commit()
            
            # Log the user in officially
            session['user_id'] = user.id
            session['user_name'] = user.name
            session.pop('pending_email', None) # Clear the pending status
            
            flash("Email verified! Welcome.", "success")
            return redirect(url_for('tasks.dashboard'))
        else:
            flash("Invalid OTP code. Try again.", "error")
            
    return render_template('verify_otp.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            # Optional: Check if they are verified before letting them log in
            if not user.is_verified:
                session['pending_email'] = user.email
                flash("Please verify your email first.", "error")
                return redirect(url_for('auth.verify_otp'))
                
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash("Login successful!", "success")
            return redirect(url_for('tasks.dashboard'))
        else:
            flash("Invalid email or password", "error")
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for('auth.login'))