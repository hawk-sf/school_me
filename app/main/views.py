from flask import render_template, session, redirect, url_for
from . import main
from .. import db
from ..models import School


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
