from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from models import db, Todo
from datetime import datetime, timezone

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))    
    search_query = request.args.get('search', '')
    query = Todo.query.filter_by(user_id=session['user_id'])
    if search_query:
        query = query.filter(Todo.content.contains(search_query))
        
    tasks = query.order_by(Todo.completed.asc(), Todo.date_created.desc()).all()
    return render_template('dashboard.html', name=session['user_name'], tasks=tasks, search_query=search_query)

@tasks_bp.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    task_content = request.form.get('content')
    if task_content:
        new_task = Todo(content=task_content, user_id=session['user_id'])
        db.session.add(new_task)
        db.session.commit()
        flash("Task created successfully", "success")
    
    return redirect(url_for('tasks.dashboard'))

@tasks_bp.route('/delete/<int:id>')
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    task = Todo.query.get(id)
    if task and task.user_id == session['user_id']:
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted", "success")
    
    return redirect(url_for('tasks.dashboard'))

@tasks_bp.route('/toggle/<int:id>')
def toggle(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    task = Todo.query.get(id)
    if task and task.user_id == session['user_id']:
        task.completed = 1 if task.completed == 0 else 0
        db.session.commit()
    
    return redirect(url_for('tasks.dashboard'))

@tasks_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    task = Todo.query.get(id)
    if not task or task.user_id != session['user_id']:
        return redirect(url_for('tasks.dashboard'))
    
    if request.method == 'POST':
        task.content = request.form.get('content')
        db.session.commit()
        flash("Task updated successfully", "success")
        return redirect(url_for('tasks.dashboard'))
    
    return render_template('update.html', task=task)