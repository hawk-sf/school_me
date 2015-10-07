from flask import redirect, flash, url_for
from . import main


@main.app_errorhandler(404)
def page_not_found(e):
    flash("Couldn't find what you were looking for...")
    return redirect(url_for('main.map')), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    flash("Whoops, looks like we just logged an error...")
    return redirect(url_for('main.map')), 500
