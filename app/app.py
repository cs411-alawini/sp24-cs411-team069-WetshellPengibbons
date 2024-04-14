import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length
from google.cloud.sql.connector import Connector
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from app.config import *

# Load configuration from environment variables for security and flexibility
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'app/cryptic-heaven-390921-29a111989a8c.json'
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  # Fallback to 'default_secret_key'

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Google Cloud SQL connector setup
connector = Connector()

def getconn() -> sqlalchemy.engine.base.Connection:
    conn = connector.connect(
        CONNECTION_NAME,
        "pymysql",
        user=GOOGLE_CLOUD_USERNAME,
        password=GOOGLE_CLOUD_PASSWORD,
        db=DB_NAME
    )
    return conn

# Configure SQLAlchemy to use connection factory
pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
    echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=pool)

class UserCreationForm(FlaskForm):
    netid = StringField('NetID', validators=[DataRequired(), Length(max=8)])
    major = StringField('Major', validators=[DataRequired()])
    grad_year = IntegerField('Graduation Year', validators=[DataRequired()])
    submit = SubmitField('Create User')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = UserCreationForm()
    if form.validate_on_submit():
        netid = form.netid.data
        major = form.major.data
        grad_year = form.grad_year.data
        with pool.connect() as db_conn:
            insert_stmt = sqlalchemy.text("INSERT INTO Users (NetID, Major, GraduatingYear) VALUES (:netid, :major, :grad_year)")
            db_conn.execute(insert_stmt, {"netid": netid, "major": major, "grad_year": grad_year})
            db_conn.commit()

        flash(f'User created: {netid}, Major: {major}, Graduating: {grad_year}')
        return redirect(url_for('index'))
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
