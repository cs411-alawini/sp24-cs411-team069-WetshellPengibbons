import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length
from google.cloud.sql.connector import Connector
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from app.config import *
from app.ml_arch import *
from gensim.models import Word2Vec
from scipy.spatial import distance
import fasttext

#Global Variables
course_title = ""
course_code = ""
professor = ""
course_description = ""
image_link = 'https://alawini.web.illinois.edu/wp-content/uploads/2021/11/Home-Alawini-scaled.jpg'


# Load Model to interpret Course
model = fasttext.load_model("app/fasttext_model.bin")



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

with pool.connect() as db_conn:
    # get random course
    init_query = sqlalchemy.text("SELECT * FROM CourseInfo ORDER BY RAND() LIMIT 1")
    result_proxy = db_conn.execute(init_query)
    result_set = result_proxy.fetchall()
    course_data = {column: value for column, value in zip(result_proxy.keys(), result_set[0])}

    # Store values
    course_title = course_data['CourseTitle']
    course_code = course_data['CourseCode']
    professor = course_data['ProfessorName']
    course_description = course_data['CourseDescription']

# Used to train word embedding_model
#get_word_embeddings(pool)

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
            check_user_stmt = sqlalchemy.text("SELECT 1 FROM Users WHERE NetID = :netid")
            existing_user = db_conn.execute(check_user_stmt, {"netid": netid}).fetchone()
            if not existing_user:
                insert_stmt = sqlalchemy.text("INSERT INTO Users (NetID, Major, GraduatingYear) VALUES (:netid, :major, :grad_year)")
                db_conn.execute(insert_stmt, {"netid": netid, "major": major, "grad_year": grad_year})
                db_conn.commit()
                flash(f'User created: {netid}, Major: {major}, Graduating: {grad_year}')
            else:
                update_stmt = sqlalchemy.text("UPDATE Users SET Major = :major, GraduatingYear = :grad_year WHERE NetID = :netid")
                db_conn.execute(update_stmt, {"netid": netid, "major": major, "grad_year": grad_year})
                db_conn.commit()
                

        session['netid'] = netid  # Store netid in session after successful insertion or failed attempt due to duplication
        session['user_vec'] = [0]*100
        session['selected_courses'] = 0
        return redirect(url_for('index'))
    
    # This will display the NetID or 'Not Signed in'
    return render_template('index.html', form=form, netid=session.get('netid', 'Not Signed in'), course_title=course_title, course_code=course_code, professor=professor, image_link=image_link)

@app.route('/submit_response', methods=['POST'])
def submit_response():
    global course_code
    global course_title
    global professor
    global course_description

    user_response = request.form['response']
    if 'netid' in session:
        netid = session['netid']
        with pool.connect() as db_conn:
            existing_entry_query = sqlalchemy.text("SELECT 1 FROM MatchResult WHERE NetID = :netid AND CourseCode = :coursecode")
            existing_entry = db_conn.execute(existing_entry_query, {"netid": netid, "coursecode": course_code}).fetchone()
            if not existing_entry:
                insert_stmt = sqlalchemy.text(
                    "INSERT INTO MatchResult (NetID, CourseCode, Response) VALUES (:netid, :coursecode, :response)"
                )
                db_conn.execute(insert_stmt, {"netid": netid, "coursecode": course_code, "response": user_response})
                db_conn.commit()
                flash(f'Response "{user_response}" saved for NetID {netid}.')
            else:
                update_stmt = sqlalchemy.text("UPDATE MatchResult SET Response = :response WHERE CourseCode = :coursecode AND NetID = :netid")
                db_conn.execute(update_stmt, {"response": user_response, "coursecode": course_code, "netid": netid })
                db_conn.commit()
        
        # If the user selects 'Yes', update preference vector
        if user_response:
            if session['selected_courses'] == 0:
                weight = np.zeros(100)
            else:
                weight = (np.array((session['user_vec'])) * session['selected_courses'])
            session['user_vec'] = ((weight + model.get_word_vector(course_title)) / (session['selected_courses']+1)).tolist()
        session['selected_courses']+=1

        # Get new course
        with pool.connect() as db_conn:
            similarity_score = 0
            course_data = {}
            while similarity_score < 0.5:
                init_query = sqlalchemy.text("SELECT * FROM CourseInfo ORDER BY RAND() LIMIT 1")
                result_proxy = db_conn.execute(init_query)
                result_set = result_proxy.fetchall()
                course_data = {column: value for column, value in zip(result_proxy.keys(), result_set[0])}
                similarity_score = 1 - distance.cosine(session['user_vec'], model.get_word_vector(course_title))
                print(session['user_vec'],model.get_word_vector(course_title))
            
            course_title = course_data['CourseTitle']
            course_code = course_data['CourseCode']
            professor = course_data['ProfessorName']
            course_description = course_data['CourseDescription']
                
    else:
        flash('You must be signed in to submit a response.')
    return redirect(url_for('index'))

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'netid' in session:
        netid = session['netid']
        with pool.connect() as db_conn:
            delete_stmt = sqlalchemy.text("DELETE FROM Users WHERE NetID = :netid")
            db_conn.execute(delete_stmt, {"netid": netid})
            db_conn.commit()
        session.pop('netid', None)  # Remove netid from session
        flash('Your account has been successfully deleted.')
    else:
        flash('You are not signed in.')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
