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

from flask_security import RoleMixin, UserMixin, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
from . import db

roles_users_table = db.Table('roles_users',
  db.Column('users_id', db.Integer(), 
  db.ForeignKey('users.id')),
  db.Column('roles_id', db.Integer(), 
  db.ForeignKey('roles.id')))

users_queries_table = db.Table('users_queries',
  db.Column('users_id', db.Integer(), 
  db.ForeignKey('users.id')),
  db.Column('queries_id', db.Integer(), 
  db.ForeignKey('queries.id')))

class Users(db.Model, UserMixin):
  id = db.Column(db.Integer(), primary_key=True)
  email = db.Column(db.String(255), unique=True)
  password = db.Column(db.String(80))
  active = db.Column(db.Boolean())
  last_login_at = db.Column(db.DateTime)
  current_login_at = db.Column(db.DateTime)
  last_login_ip = db.Column(db.String(100))
  current_login_ip = db.Column(db.String(100))
  login_count = db.Column(db.Integer)
  fs_uniquifier = db.Column(db.String(255), unique = True, nullable = True)
  password_changed = db.Column(db.Boolean(), default = False, nullable = False)
  roles = db.relationship('Roles', secondary=roles_users_table,
    backref='user', lazy=True)
  queries = db.relationship('Queries', secondary=users_queries_table,
    backref='user', lazy='dynamic')

class Roles(db.Model, RoleMixin):
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(80), unique=True)
  description = db.Column(db.String(255))

class Queries(db.Model):
  id = db.Column(db.Integer(), primary_key = True)
  name = db.Column(db.String(), unique = True)
  tables = db.Column(db.String())
  tName = db.Column(db.String())
  sql = db.Column(db.String())
  ordering = db.Column(db.String())
  order_descending = db.Column(db.Boolean())

user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)