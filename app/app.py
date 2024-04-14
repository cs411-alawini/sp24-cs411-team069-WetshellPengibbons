from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
app.config['SECRET_KEY'] = 'balls'

class UserCreationForm(FlaskForm):
    netid = StringField('NetID', validators=[DataRequired(), Length(max=8)])
    major = StringField('Major', validators=[DataRequired()])
    grad_year = IntegerField('Graduation Year', validators=[DataRequired()])
    submit = SubmitField('Create User')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = UserCreationForm()
    if form.validate_on_submit():
        # Here you would usually persist this information to a database
        netid = form.netid.data
        major = form.major.data
        grad_year = form.grad_year.data
        # For demonstration, we'll just flash a message to the user
        flash(f'User created: {netid}, Major: {major}, Graduating: {grad_year}')
        return redirect(url_for('index'))
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
