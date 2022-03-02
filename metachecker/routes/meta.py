from flask import Blueprint, render_template
from flask import redirect, url_for
from flask_login import logout_user


bp = Blueprint('meta', 'meta')


@bp.route('/about')
def about():
    return render_template('about.html')


@bp.route('/disconnect')
def disconnect():
    logout_user()
    return redirect(url_for('collection.index'))
