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
port = os.getenv('MYSQL_PORT', '17449')
database = os.getenv('MYSQL_DB')

safe_password = urllib.parse.quote_plus(password) if password else ""

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{user}:{safe_password}@{host}:{port}/{database}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "connect_args": {
        "ssl": {"fake_flag_to_enable_tls": True} 
    }
}

db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(tasks_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            # Test connection
            db.session.execute(text('SELECT 1'))
            print("\n" + "="*30)
            print("DATABASE CONNECTED SUCCESSFULLY!")
            print("="*30 + "\n")
        except Exception as e:
            print("\n" + "!"*30)
            print(f"DATABASE CONNECTION FAILED: {e}")
            print("!"*30 + "\n")
            
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))