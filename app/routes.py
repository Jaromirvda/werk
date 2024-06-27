from flask import render_template

from app import app

@app.route('/')
@app.route('/index')
def index():
    render_template('home.html')

@app.route('/search')
def search():

    render_template('search.html')

@app.route('/edit')
def edit():
    render_template('edit.html')

@app.route('/delete')
def delete():
    render_template('delete.html')

@app.route('/add')
def add():
    render_template('add.html')