from flask import Blueprint, request, render_template, redirect, session, flash, url_for
from auth.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_id, error = auth_service.authenticate_user(email, password)
        
        if user_id:
            session['user_id'] = user_id
            return redirect(url_for('main.dashboard'))
        flash(error)
    
    return render_template("auth.html", is_login=True)

@auth_bp.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template("auth.html", is_login=False)
        
        user_id, error = auth_service.create_user(name, email, password)
        
        if user_id:
            session['user_id'] = user_id
            return redirect(url_for('main.dashboard'))
        flash(error)
    
    return render_template("auth.html", is_login=False)

@auth_bp.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))
