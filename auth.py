from flask import Blueprint, render_template, redirect, url_for, request, session
from models import db, User
import bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

auth_bp = Blueprint('auth', __name__)

class RegistrationForm(FlaskForm):
    name = StringField("", validators=[DataRequired()])
    email = StringField("", validators=[DataRequired(), Email()])
    password = PasswordField("", validators=[DataRequired()])
    submit = SubmitField("Register")

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(name=form.name.data, email=form.email.data, password=hashed_pwd)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))
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
            return redirect(url_for('tasks.dashboard'))
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))