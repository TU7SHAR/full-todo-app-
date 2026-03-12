import os
import urllib.parse
from flask import Flask, render_template
from models import db
from auth import auth_bp
from tasks import tasks_bp 
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mysecret')

user = os.getenv('MYSQL_USER')
password = urllib.parse.quote_plus(os.getenv('MYSQL_PASSWORD'))
host = os.getenv('MYSQL_HOST')
port = os.getenv('MYSQL_PORT', '17449')
database = os.getenv('MYSQL_DB')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?ssl_disabled=False"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}

db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(tasks_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))