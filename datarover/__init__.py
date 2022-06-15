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

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
import json

db = SQLAlchemy()
security = Security()

def create_app():
    app = Flask(__name__)

    load_config(app, "../config.json")
    # app.config.from_file("config.json", load=json.load)

    db.init_app(app)

    # print(app.config["server_url"])

    from .models import Users, Roles, user_datastore
    security.init_app(app, user_datastore)

    @security.login_context_processor
    def security_login_processor():
        return dict(app_name = app.config["APP_NAME"])
    
    with app.app_context():
        db.create_all()

    from .webApp import webApp as webApp_blueprint
    app.register_blueprint(webApp_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app

def load_config(app, configfile):
    app.config.from_file(configfile, load=json.load)

