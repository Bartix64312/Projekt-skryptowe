from flask import Blueprint, render_template

ui_bp = Blueprint('ui', __name__)

@ui_bp.route('/')
def index():
    return render_template('index.html')

@ui_bp.route('/warsztat')
def practice():
    return render_template('practice.html')