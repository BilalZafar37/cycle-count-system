from flask import Flask, render_template, request, redirect
import pandas as pd
from Upload_db import upload_file_to_db, db_connection
from create_count_in_db import make_count_sheet
from sqlalchemy import text
import re

app = Flask(__name__)

@app.route("/")
def call_home():
  return render_template('dashboard.html')

@app.route("/profile")
def profile():
  return render_template('profile.html')

@app.route("/count_job", methods=['GET', 'POST'])
def counting():
  return render_template('count_job.html')

#handle count when worker submits it to db
@app.route("/submit_count", methods=['GET', 'POST'])
def submit_count():
  if  request.method =='POST':
    back = request.referrer
    test = request.form['counter0']
    print(test)
    return redirect(back)
    engine = db_connection()
    with engine.connect() as conn:
      pass

@app.route("/options1", methods=['GET', 'POST'])
@app.route("/count_jobs", methods=['GET', 'POST'])
def counting_jobs_assigned():
  engine = db_connection()
  with engine.connect() as conn:
    #Accept the assigned table and start counting the table
    if request.method =='POST' and "accepted" in request.form:
      sheet_name = request.form['accepted']
      #get the accepted table data
      get_tables = conn.execute(text("Select * from inventory."+str(sheet_name)+""))
      table = []
      columns_of_tables= get_tables.keys()
      for row in get_tables.all():
        table.append(dict(zip(columns_of_tables, row)))

      # print(table[0]["Article"])
      return render_template('count_job_list.html', table = table)
    
    #this gets the names of all the count lists ASSIGNED in the database
    get_all_count_lists_names = conn.execute(text("Select * from information_schema.tables Where table_name like '%_assigned'"))
    column_names = get_all_count_lists_names.keys()
    count_list = []
    for row in get_all_count_lists_names.all():
      count_list.append(dict(zip(column_names, row)))

    #This gets all the actual lists using the names from above code
    get_tables = conn.execute(text("Select * from inventory."+count_list[0]["TABLE_NAME"]+""))
    table = []
    columns_of_tables= get_tables.keys()
    for row in get_tables.all():
      table.append(dict(zip(columns_of_tables, row)))

      
  return render_template('count_jobs_list.html', count_list = count_list, lists = table)

@app.route("/options_for_lists", methods=['GET', 'POST'])
@app.route("/created_jobs", methods=['GET', 'POST'] )
def jobs():
  engine = db_connection()
  with engine.connect() as conn:

    #this gets the names of all the count lists created in the database
    get_all_count_lists_names = conn.execute(text("Select * from information_schema.tables Where table_name like 'tmp_tbl_%'"))
    column_names = get_all_count_lists_names.keys()
    count_list = []
    for row in get_all_count_lists_names.all():
      count_list.append(dict(zip(column_names, row)))
    print(count_list)
    #This gets all the actual lists using the names from above code
    get_tables = conn.execute(text("Select * from inventory."+count_list[0]["TABLE_NAME"]+""))
    table = []
    columns_of_tables= get_tables.keys()
    for row in get_tables.all():
      table.append(dict(zip(columns_of_tables, row)))

    #Assign the table
    if request.method =='POST' and "assign" in request.form:
      sheet_name = request.form['assign']
      assign = conn.execute(text("ALTER TABLE "+sheet_name+" RENAME "+sheet_name+"_assigned;"))

  return render_template('created_counts.html', count_list = count_list, lists = table)

@app.route("/create_new")
@app.route("/make_sheet", methods=['GET', 'POST'] )
def make_jobs():
  engine = db_connection()
  with engine.connect() as conn:
    get_all_master_file_names = conn.execute(text("Select table_name from information_schema.tables Where table_name like '%_master'"))
    sheet = []
    for row in get_all_master_file_names.all():
      row = re.sub(r"[^A-Za-z-0-9_\s]", "", str(row))
      sheet.append(str(row))
    if request.method =='POST' and "file_select" in request.form:
      file = request.form['file']
      file = re.sub(r"[^A-Za-z-0-9-_\s]", "", str(file))

      unique_site =conn.execute(text("SELECT distinct Site FROM inventory."+str(file)+";"))
      site = []
      for row in unique_site.all():
          row = re.sub(r"[^A-Za-z-0-9-_\s]", "", str(row))
          site.append(str(row))
      unique_sloc =conn.execute(text("SELECT distinct Sloc FROM inventory."+str(file)+";"))
      sloc = []
      for row in unique_sloc.all():
          row = re.sub(r"[^A-Za-z-0-9_\s]", "", str(row))
          sloc.append(str(row))
      unique_cat =conn.execute(text("SELECT distinct Category FROM inventory."+str(file)+";"))
      cat = []
      for row in unique_cat.all():
          row = re.sub(r"[^A-Za-z-0-9-_\s]", "", str(row))
          cat.append(str(row))
      return render_template('create_job.html', sheet=sheet, site= site, sloc= sloc, cat = cat)
    
    if request.method =='POST' and "choice" in request.form:
      file = request.form['file']
      file = re.sub(r"[^A-Za-z1-9-_\s]", "", file)
      catagory= request.form['Catagory']
      site= request.form['Site']
      sloc= request.form['Sloc']
      # store= request.form['Store']
      #makes a new table
      make_count_sheet(catagory=catagory, site=site, sloc=sloc, file=file)
    return render_template('create_job.html', sheet=sheet)

@app.route("/upload_file", methods=['GET', 'POST'])
def upload_sheet():
  return render_template('upload_file.html')
@app.route("/data", methods=['GET', 'POST'])
def data():
  if request.method == 'POST':
    file = request.form['upload-file']
    data = pd.read_excel(file)
    file = file.split(".")
    file = file[0]
    upload_file_to_db(file=file)

    return render_template('upload_file.html', data=data.to_html(classes="table align-items-center mb-0"))


# @app.route("/make_sheet", methods=['GET', 'POST'] )
# def get_db_columns():
#   if request.method =='POST':
#     catagory= request.form['Catagory']
#     site= request.form['Site']
#     sloc= request.form['Sloc']
#     store= request.form['Store']
#     file = request.form['file']
#     file = re.sub(r"[^A-Za-z-_\s]", "", file)
#     make_count_sheet(catagory=catagory, site=site, sloc=sloc, store=store, file=file)
#     return site

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)