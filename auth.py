from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from models import db, User
import bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__)

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
            new_user = User(name=form.name.data, email=form.email.data, password=hashed_pwd)
            db.session.add(new_user)
            db.session.commit()
            
            session['user_id'] = new_user.id
            session['user_name'] = new_user.name
            
            flash("Account created successfully!", "success")
            return redirect(url_for('tasks.dashboard'))
            
        except IntegrityError:
            db.session.rollback()
            flash("Email already registered.", "error")
            return redirect(url_for('auth.register'))
            
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
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