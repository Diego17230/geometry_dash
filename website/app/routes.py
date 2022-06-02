from flask import render_template
from app import app


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/download')
def download():
    return render_template('download.html', title='Download')


@app.route('/watch')
def watch():
    return render_template('watch.html', title='Watch')
