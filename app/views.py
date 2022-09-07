from flask import render_template, request
from app import app

@app.route('/')
@app.route('/submit')
@app.route('/index')
@app.route('/submissions')
def submit():
    return render_template('submissions.html')

@app.route('/viewFlags')
def viewFlags():
    return render_template('viewFlags.html')