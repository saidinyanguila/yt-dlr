from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.models import User
from .. import db
import os

auth = Blueprint('auth', __name__)

@auth.route("/", methods=['GET', 'POST'])
@login_required
def account():
    if request.method == "GET":
        return render_template('user.html', user=current_user)
    elif request.method == "POST":
        return jsonify({
            "page_name" : "Account",
            "content" : f"<div class='section account-setion'><span class='section-header'>Account</span><div class='account-header'><div class='account-pfp img-box'><img src='/{ current_user.user_img_path }' alt=''></div><div class='account-info'><div class='account-user_name'><span>{ current_user.name }</span></div><div class='account-user_id'><span>{ current_user.email }</span></div></div></div><div class='account-section-content'><div class='account-tabs-container'><a href='{ url_for('auth.account_edit') }'><div class='account-tab'><span>Edit Profile</span></div></a><a href='{ url_for('auth.account_settings') }'><div class='account-tab'><span>Account Settings</span></div></a><div class='account-tab'><span>App Settings</span></div></div><a href='{ url_for('auth.logout') }' id='logout_user'>Log Out</a></div></div>"
        })

@auth.route("/edit", methods=['GET', 'POST'])
@login_required
def account_edit():
    if request.method == "GET":
        return render_template('user_edit.html', user=current_user)
    elif request.method == "POST":
        user = User.query.get(current_user.id)
        if not user:
            return "User not found", 404

        # Name
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')

        if len(f_name) > 3:
            user.f_name = f_name
            user.l_name = l_name

        # Profile Image
        file = request.files.get('image')
        if file:
            filename = f"{user.id}.png"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save('website/' + filepath)
            user.user_img_path = filepath

        # Commit Changes
        db.session.commit()

        return redirect(url_for('auth.account'))

@auth.route("/sign-in", methods=['GET','POST'])
def sign_in():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user :
            if check_password_hash(user.password, password):
                login_user(user=user, remember=True)
                return redirect(url_for('views.home'))
            else :
                flash("Incorrect email or password.", category="invalid_login")
                return render_template('sign in.html')
        else :
            flash("Incorrect email or password.", category="invalid_login")
            return render_template('sign in.html')

    return render_template('sign in.html')

@auth.route("/sign-up", methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user :
            return "Email already taken"
        else :
            new_user = User(f_name=f_name, l_name=l_name, email=email, password=generate_password_hash(password=password, method='scrypt'))
            db.session.add(new_user)
            db.session.commit()
            login_user(user=new_user, remember=True)
            print("User Created!")
            return redirect(url_for('views.home'))

    return render_template('sign up.html')

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.sign_in'))
