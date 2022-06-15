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

from flask import Flask, render_template, make_response, url_for, request, send_file, session, Blueprint, redirect, flash, current_app, g
import pandas as pd
from pandas import DataFrame
import numpy as np
from flask_security import login_required, current_user
from flask_security.utils import hash_password
import pyodbc
from . import db
from .models import Queries, user_datastore, Users
from . import helper

webApp = Blueprint('webApp', __name__)

# Setting up before Request from the config file:
@webApp.before_request
def load_config():
  server_url = current_app.config["SERVER_URL"]
  database = current_app.config["DATABASE_NAME"]
  odbc_driver = current_app.config["ODBC_DRIVER"]
  # if platform.system() == "Windows":
  #   odbc_driver = "{SQL Server}"
  # elif platform.system() in ("Darwin", "Linux"):
  #   odbc_driver = "{ODBC Driver 17 for SQL Server}"
  #   odbc_driver = "{freetds}"

  pre = 'DRIVER='+odbc_driver+';SERVER='+server_url+';DATABASE='+database+';Port=1433'
  if current_app.config['WINDOWS_AUTHENTICATION']:
    g.cnxn = pyodbc.connect(pre + ';Trusted_Connection=yes')
  else:
    g.cnxn = pyodbc.connect(pre + ';UID=' + current_app.config["DB_USERNAME"] + 
                                    ';PWD=' + current_app.config["DB_PASSWORD"])
  
  df = pd.read_sql("SELECT COLUMN_NAME, TABLE_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COlUMNS", g.cnxn)
  colN = np.char.add(list(df["TABLE_NAME"]), np.char.add(".", list(df["COLUMN_NAME"])))
  dt = list(df["DATA_TYPE"])
  g.DATA_TYPES = dict(zip(colN, dt))
  g.schema = current_app.config["DBO_SCHEMA"]
  g.ordering = current_app.config['ORDERING']
  g.partial_variables = current_app.config["PARTIAL_VARIABLES"]
  g.search_list_cols = current_app.config["SEARCH_LIST_COLUMNS"]
  g.both = current_app.config["BOTH_SEARCH"]
  g.PREVIEW_NUM = current_app.config["PREVIEW_NUM"]

  g.app_name = current_app.config["APP_NAME"]
  g.show_key = current_app.config["SHOW_KEY"]
  g.relations, g.keys = helper.key_helper(g.cnxn)
  # print(g.relations['donations'])
  if len(Users.query.all()) == 0:
    user_datastore.find_or_create_role(name = 'Admin')
    user_datastore.create_user(
                email = current_app.config["ADMIN_EMAIL"],
                password = hash_password(current_app.config["ADMIN_PASS"]),
                roles = ['Admin']
            )
    db.session.commit()



#Will use the following to extract foreign key reference data.

#   SELECT   
#     f.name AS foreign_key_name  
#    ,OBJECT_NAME(f.parent_object_id) AS table_name  
#    ,COL_NAME(fc.parent_object_id, fc.parent_column_id) AS constraint_column_name  
#    ,OBJECT_NAME (f.referenced_object_id) AS referenced_object  
#    ,COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS referenced_column_name  
#    ,is_disabled  
# FROM sys.foreign_keys AS f  
# INNER JOIN sys.foreign_key_columns AS fc   
#    ON f.object_id = fc.constraint_object_id   


@webApp.route('/download', methods=("POST", "GET"))
def download():
  if request.method == "GET":
    return f"No data given, please return to /main"
  sql = session.get("table")
  df = pd.read_sql(sql, g.cnxn)
  df = df.loc[:,~df.columns.duplicated()]
  resp = make_response(df.to_csv(index = False))

  resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
  resp.headers["Content-Type"] = "text/csv"

  return resp

@webApp.route('/save', methods=("POST", "GET"))
def save():
  # Need to do Error Handling
  if request.method == "GET":
    return f"No data given, please return to /main"

  sql = session.get("table")
  tables = session["names"]
  tName = session["tName"]
  ordering = session['ordering']
  order_descending = session["order_descending"]
  try:
    q = Queries(name = request.form.get("name"), tables = tables, tName = tName, sql = sql, 
                ordering = ordering, order_descending = order_descending)

    current_user.queries.append(q)

    db.session.commit()
    flash("success")
  except:
    flash("Name already exists")

  return redirect(url_for('webApp.html_table', index = 0), code = 307)

@webApp.route('/table', methods=("POST", "GET"))
@webApp.route('/table/<index>', methods=("POST", "GET"))
def html_table(index = 0, tName = None):
  # print(request.form)
  index = int(index)
  if request.method == 'POST':
    # print(request.form)
    if "table" not in session:
      if session['mode'] == 'custom':
        session['table'] = 'SELECT ' + request.form['input_1'] + " FROM " + session['tName'] + " " + request.form['input_2']
      else:
        table_name = session["tName"]
        ordering = request.form["ordering"]
        order_descending = request.form["order_descending"] == "true" # Make boolean

        # This is a crazy workaround to have the WHERE clause start with something
        # that does nothing, so that you can always append " AND " to it. 
        # We should rather have an if statement evaluating whether a WHERE clause is
        # required at all (any filters provided) and if a WHERE clause is required
        # the first condition should not start with AND
        sql = table_name
        conditions = []
        for k in request.form:
          cond = ""
          if k == "ordering" or k == "order_descending":
            continue
          temp = request.form.getlist(k)

          if len(temp) == 1 and temp[0] == "":
            continue
          print(temp)
          if "partial" in k and len(k) > 7 and len(temp) > 0:
            actual = k[7:]
            cond += actual + " LIKE '%" + temp[0] +  "%'"
            for j in range(1, len(temp)):
              cond += " OR " + actual + " LIKE '%" + temp[j] +  "%'"
            cond += ")"
          elif "exact" in k and len(k) > 5 and len(temp) > 0:
            actual = k[5:]
            cond += actual + " IN " + str(tuple(temp))
          # This block should be removed since it was for debugging -- leaving it 
          # in for testing at the moment, but it should not be invoked
          elif k in g.search_list_cols and len(temp) > 1:
            print("Length of temp is greater than 1 for a search column!")
            continue
          # This block filters on newline delimited list of values
          elif k in g.search_list_cols and len(temp) == 1:
            strings = temp[0].splitlines()
            cond += k + " IN ("
            for i in range(0, len(strings)):
              cond += "'" + strings[i] + "'"
              if i == len(strings)-1:
                cond += ")"
              else:
                cond += ","
          elif k in g.partial_variables:
            cond += k + " LIKE '%" + temp[0] +  "%'"
          elif k not in g.DATA_TYPES:
            temp = temp[0]
            actual = k[3:]
            if 'date' == g.DATA_TYPES[actual] or 'datetime' == g.DATA_TYPES[actual]:
              temp = "'" + temp + "'"
          
            
            if "min" == k[:3]:
              cond += actual + " >= " + temp
            else:
              cond += actual + " <= " + temp
          else:
            if len(temp) == 1:
              cond += k + " = '" + temp[0] + "'"
            else:
              cond += k + " IN " + str(tuple(temp))

          conditions.append(cond)
        
        if conditions:
          conditions = " WHERE " + " AND ".join(conditions)
        else:
          conditions = ""
        session["table"] = "SELECT * FROM " + sql + conditions
        session["ordering"] = ordering
        session["order_descending"] = order_descending
      
    sql = session["table"]

    if session['mode'] == 'input':

      ordering = session["ordering"]
      order_descending = session["order_descending"]
      # print(sql)
      n = int(pd.read_sql("SELECT count (*)" + sql.split("*")[1], g.cnxn).values[0][0])

      if order_descending:
        order_by_string = "CASE WHEN " + ordering + " IS NULL THEN 1 ELSE 0 END , " + ordering + " DESC"
      else:
        order_by_string = "CASE WHEN " + ordering + " IS NULL THEN 1 ELSE 0 END , " + ordering
      

      dt = {}
      for c in session['cols']:
        if g.DATA_TYPES[c] == 'int':
          dt[c.split('.')[1]] = 'Int64'
      sql += " ORDER BY " + order_by_string + " OFFSET " + str(index) + " ROWS FETCH NEXT " + str(g.PREVIEW_NUM) + " ROWS ONLY"
      df = pd.read_sql_query(sql, g.cnxn, dtype = dt)
      df.fillna(pd.NA, inplace = True)
      df = df.loc[:,~df.columns.duplicated()]
      df.sort_values(ordering.split('.')[1], ascending = not order_descending, na_position = 'last', inplace = True)
    else:
      if "ORDER BY" not in sql:
        sql += " ORDER BY 1"
      try:
        df = pd.read_sql_query(sql + " OFFSET " + str(index) + " ROWS FETCH NEXT " + str(g.PREVIEW_NUM) + " ROWS ONLY", g.cnxn)
        n = 0
      except:
        flash("invalid query")
        return redirect(url_for('webApp.custom'), code = 307)
    # Dealing with non encoded date
    # if g.date_column in df.columns:
    #   df[g.date_column] = pd.to_datetime(df[g.date_column], format = g.date_format).dt.date
    return render_template('table.html', app_name = g.app_name, column_names = df.columns.values, row_data = list(df.values.tolist()),
                          zip = zip, n = n, m = df.shape[0], i = min(n - n % g.PREVIEW_NUM, index + g.PREVIEW_NUM), j = max([index - g.PREVIEW_NUM, 0]), 
                          k = index, 
                          sql_query = sql,
                          admin = current_user.has_role("Admin") or current_user.has_role("SuperUser")) # , title = g.title ##Unused? g.title doesn't exist
  elif request.method == "GET":
    return f"Table name not given please return to /main"

@webApp.route('/')
@webApp.route('/main', methods = ['POST', 'GET'])
@login_required
def main():
  if not current_user.password_changed:
    flash("Please change your password before starting")
    return redirect(url_for('auth.change'))
  if "table" in session:
    session.pop("table")
  if "tName" in session:
    session.pop("tName")
    session.pop("names")
  names = pd.read_sql("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES", g.cnxn)["TABLE_NAME"]
  return render_template('main.html', app_name = g.app_name, names = names, admin = current_user.has_role("Admin") or current_user.has_role("SuperUser"), relations = g.relations)

@webApp.route('/saved', methods = ['POST', 'GET'])
@login_required
def saved():
  if "name" in request.form:
    name = request.form["name"]
    query = current_user.queries.filter(Queries.name == name).all()[0]
    session["tName"] = query.tName
    session["names"] = query.tables
    session["table"] = query.sql
    session["ordering"] = query.ordering
    session["order_descending"] = query.order_descending
    return redirect(url_for('webApp.html_table', index = 0), code = 307)

  queries = current_user.queries
  mapping = {q.name:q.sql for q  in queries}
  return render_template('saved.html', app_name = g.app_name, mapping = mapping, admin = current_user.has_role("Admin") or current_user.has_role("SuperUser"))

@webApp.route('/input', methods = ['POST', 'GET'])
@login_required
def input():
  # print(request.form)
  if request.method == 'POST':
    session["mode"] = "input"
    if "table" in session:
      session.pop("table")
    if "ordering" in session:
      session.pop("ordering")
    if "tName" in session:
      tName = session["tName"]
      names = session["names"]
    else:
      names = request.form.getlist('table')
      joinT = request.form.getlist('joinT')
      joinK = request.form.getlist('joinK')
      # print(names, joinT, joinK)
      tName = helper.generateTable(names, joinT, joinK, g.schema)

      names = ", ".join(names)
      session["tName"] = tName
      session["names"] = names
    if "cols" in session:
      session.pop("cols")

      
    # sql = "SELECT TOP 1 * FROM {s}".format(s = tName)

    t_names = names.split(", ")

    if len(t_names) == 1:
      sql = "SELECT DISTINCT COLUMN_NAME, TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '" + t_names[0] + "'"
    else:
      sql = "SELECT DISTINCT COLUMN_NAME, TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME IN " +  str(tuple(t_names))
    df = pd.read_sql(sql, g.cnxn)
    colN = list(np.char.add(list(df["TABLE_NAME"]), np.char.add(".", list(df["COLUMN_NAME"]))))
    # colN = list(colN.loc[:,~colN.columns.duplicated()].columns)
    unique_vals = dict()
    order_cand = []
    date_col = []
    bit_col = []
    for n in colN:
      if n in g.ordering:
        order_cand.append(n)
      if "varchar" in g.DATA_TYPES[n] and n not in unique_vals:
        if n not in g.partial_variables and n not in g.search_list_cols:
          sql = "SELECT DISTINCT {n} FROM {s}".format(n = n, s = tName)
          temp = pd.read_sql(sql, g.cnxn)
          unique_vals[n] = temp.iloc[:, 0].to_list()
      elif "date" == g.DATA_TYPES[n] or "datetime" == g.DATA_TYPES[n]:
        date_col.append(n)
      elif "bit" == g.DATA_TYPES[n]:
        bit_col.append(n)

    # names = ", ".join(names)
    # session["tName"] = tName
    # session["names"] = names
    session["cols"] = colN
    return render_template('input.html', app_name = g.app_name, names = names, tName = tName, column_names = colN, 
                          vals = unique_vals, partial = g.partial_variables, date = date_col, bit = bit_col, both = g.both, 
                          search_list = g.search_list_cols, order_cand = order_cand, showK = g.show_key, keys = g.keys, 
                           admin = current_user.has_role("Admin") or current_user.has_role("SuperUser"))
  if request.method == 'GET':
    return f"Table name not given please return to /main"

@webApp.route('/custom', methods = ['POST', 'GET'])
@login_required
def custom():
  
  if request.method == 'POST':
    session["mode"] = "custom"
    if "table" in session:
      session.pop("table")
    if "ordering" in session:
      session.pop("ordering")
    if "tName" in session:
      tName = session["tName"]
      names = session["names"]
    else:
      names = request.form.getlist('table')
      joinT = request.form.getlist('joinT')
      joinK = request.form.getlist('joinK')
    
      tName = helper.generateTable(names, joinT, joinK, g.schema)

      names = ", ".join(names)
      session["tName"] = tName
      session["names"] = names
    if "cols" in session:
      session.pop("cols")

    return render_template('custom.html', app_name = g.app_name, names = names, tName = tName,
                           admin = current_user.has_role("Admin") or current_user.has_role("SuperUser"))
  if request.method == 'GET':
    return f"Table name not given please return to /main"
    
  return
  

# if __name__ == "__main__":
#   app.run(debug = True)