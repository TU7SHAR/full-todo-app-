import os
import urllib.parse
from flask import Flask, render_template
from models import db
from auth import auth_bp
from tasks import tasks_bp 
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mysecret')

user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
host = os.getenv('MYSQL_HOST')
port = os.getenv('MYSQL_PORT', '4000')
database = os.getenv('MYSQL_DB', 'test')

safe_password = urllib.parse.quote_plus(password) if password else ""

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{user}:{safe_password}@{host}:{port}/{database}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "connect_args": {
        "ssl": {"min_version": "TLSv1.2"}
    }
}

db.init_app(app)

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        pass

app.register_blueprint(auth_bp)
app.register_blueprint(tasks_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))