import os
import urllib.parse
from flask import Flask, render_template
from models import db
from auth import auth_bp
from tasks import tasks_bp # Assuming you put Todo routes in tasks.py
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

user = os.getenv('MYSQL_USER')
password = urllib.parse.quote_plus(os.getenv('MYSQL_PASSWORD'))
host = os.getenv('MYSQL_HOST')
database = os.getenv('MYSQL_DB')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'mysql://{user}:{password}@{host}/{database}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(tasks_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)