# Data Rover
# Copyright (C) 2022  Vitalant
# Developed by Vincent Chiang

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from flask import Flask, render_template, make_response, url_for, request, send_file, session, Blueprint, redirect, current_app
import os
from . import db
from .models import Users, user_datastore
from flask_security.utils import hash_password, verify_password
from flask_security import roles_accepted, current_user, login_required, Security

auth = Blueprint('auth', __name__)

ROLES = ["Admin", "SuperUser", "User"]


@auth.route('/register', methods = ['POST', 'GET'])
@roles_accepted('Admin', "SuperUser")
def register():
    if request.method == 'POST':
        if user_datastore.find_user(email = request.form.get('email')) == None:

            user_datastore.find_or_create_role(name = request.form.get('role'))
            user_datastore.create_user(
                email=request.form.get('email'),
                password=hash_password(request.form.get('password')),
                roles = [request.form.get('role')]
            )
            db.session.commit()
            return render_template('register.html', success = True, app_name = current_app.config["APP_NAME"], admin = current_user.has_role("Admin") or current_user.has_role("SuperUser"))
        else:
            return render_template('register.html', success = False, app_name = current_app.config["APP_NAME"], admin = current_user.has_role("Admin") or current_user.has_role("SuperUser"))
    return render_template('register.html', app_name = current_app.config["APP_NAME"], admin = current_user.has_role("Admin") or current_user.has_role("SuperUser"))

@auth.route('/change', methods = ['POST', 'GET'])
@login_required
def change():
    # print('+++++++')
    # print(current_app.config["APP_NAME"])
    if request.method == 'POST':
        if verify_password(request.form.get('password'), current_user.password):

            current_user.password = hash_password(request.form.get('new_password'))
            current_user.password_changed = True
            db.session.commit()
            return redirect(url_for('webApp.main'))
        else:
            return render_template('change.html', success = False, app_name = current_app.config["APP_NAME"], admin = current_user.has_role("Admin") or current_user.has_role("SuperUser"))
    return render_template('change.html', app_name = current_app.config["APP_NAME"], admin = current_user.has_role("Admin") or current_user.has_role("SuperUser"))

@auth.route('/manage', methods = ['POST', 'GET'])
@roles_accepted('Admin', "SuperUser")
def manage():
    # Admin can delete everyone while SuperUser can only delete normal Users
    if request.method == 'POST':

        u = user_datastore.find_user(email = request.form["user"])
        admin_role = u.has_role("Admin")
        super_role = u.has_role("SuperUser")

        msg = None
        if admin_role:
            msg = "Cannot Modify Admin Account"
        elif request.form["type"] == "delete":
            if super_role:
                if current_user.has_role("Admin"):
                    user_datastore.delete_user(u)
                    msg = "Super User Account deleted"
                else:
                    msg = "Fail, only Admin can delete super user account"
            else:
                user_datastore.delete_user(u)
                success = True
        elif request.form["type"] == "deactivate":
            if super_role:
                if current_user.has_role("Admin"):
                    success = user_datastore.delete_user(u)
                    if success:
                        msg = "Super user account deactivated"
                    else:
                        msg = "Fail, account already deactivated or its your acount"
                else:
                    msg = "Only admin can delete super user account"
            else:
                success = user_datastore.deactivate_user(u)
                if success:
                    msg = "User account deactivated"
                else:
                    msg = "Fail, account already deactivated or its your acount"
        else:
            if super_role:
                if current_user.has_role("Admin"):
                    success = user_datastore.activate_user(u)
                    if success:
                        msg = "Super user account activated"
                    else:
                        msg = "Fail, Account already activated"
                else:
                    msg = "Fail, Only admin can activate super user account"
            else:
                success = user_datastore.activate_user(u)
                if success:
                    msg = "User account activated"
                else:
                    msg = "Fail, account already activated"

        db.session.commit()
        all_users = Users.query.all()
        all_users = [user.email for user in all_users]
        return render_template('manage.html', app_name = current_app.config["APP_NAME"], users = all_users, message = msg, admin = current_user.has_role("Admin") or current_user.has_role("SuperUser"))

            

    else:
        all_users = Users.query.all()
        all_users = [u.email for u in all_users]

        return render_template('manage.html', app_name = current_app.config["APP_NAME"], users = all_users, admin = current_user.has_role("Admin") or current_user.has_role("SuperUser"))

@auth.route('/admin_change', methods = ['POST', 'GET'])
@roles_accepted('Admin', "SuperUser")
def admin_change():
    # Admin ->SuperUser -> User
    all_users = Users.query.all()
    all_users = [u.email for u in all_users]
    if request.method == 'POST':

        u = user_datastore.find_user(email = request.form["user"])
        admin_role = u.has_role("Admin")
        super_role = u.has_role("SuperUser")

        msg = None
        
        if admin_role:
            msg = "Cannot change admin password, if you are the admin go to change password on main page"
        elif super_role:
            if current_user.has_role("Admin"):
                u.password = hash_password(request.form.get('new_password'))
                u.password_changed = False
                db.session.commit()
                msg = "Super User Account Password changed"
            else:
                msg = "Fail, only Admin can modify super user account"
        else:
            u.password = hash_password(request.form.get('new_password'))
            u.password_changed = False
            db.session.commit()
            msg = "User Account Password changed"

        return render_template('admin_change.html', app_name = current_app.config["APP_NAME"], users = all_users, message = msg, admin = current_user.has_role("Admin") or current_user.has_role("SuperUser")) 

    else:

        return render_template('admin_change.html', app_name = current_app.config["APP_NAME"], users = all_users, admin = current_user.has_role("Admin") or current_user.has_role("SuperUser"))
