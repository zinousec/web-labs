import math
import io
import csv

from flask import Blueprint, render_template, request, send_file
from flask_login import login_required, current_user
from app import db
from auth import check_rights

bp = Blueprint('visits', __name__, url_prefix='/visits')

PER_PAGE = 10

@bp.route('/stat')
@login_required
@check_rights("show_stat")
def stat():
    download_status = False
    if request.args.get('download_csv'):
        download_status = True
    query = '''
    SELECT visit_logs.path, count(visit_logs.path) AS count
    FROM visit_logs GROUP BY visit_logs.path ORDER BY count DESC
    '''
    with db.connection.cursor(named_tuple = True) as cursor:
        cursor.execute(query)
        print(cursor.statement)
        db_stat = cursor.fetchall()
    if download_status:
        f = io.BytesIO()
        f.write("№,Path,Counter\n".encode("utf-8"))
        for i, row in enumerate(db_stat):
            f.write(f'{i+1},{row.path},{row.count}\n'.encode("utf-8"))
        f.seek(0)
        return send_file(f, as_attachment=True, download_name="stat.csv", mimetype="text/csv")
        
    return render_template('visits/stat.html', stats = db_stat)

@bp.route('/stat_users')
@login_required
@check_rights("show_stat")
def stat_users():
    download_status = False
    if request.args.get('download_csv'):
        download_status = True
    query = '''
    SELECT users.last_name, users.first_name, users.middle_name, COUNT(*) AS count 
    FROM visit_logs LEFT JOIN users ON visit_logs.user_id = users.id 
    GROUP BY visit_logs.user_id ORDER BY count DESC
    '''
    with db.connection.cursor(named_tuple = True) as cursor:
        cursor.execute(query)
        print(cursor.statement)
        db_stat = cursor.fetchall()
    
    if download_status:
        f = io.BytesIO()
        f.write("№,Name,Counter\n".encode("utf-8"))
        for i, row in enumerate(db_stat):
            last_name = str(row.last_name) + ' '
            first_name = str(row.first_name) + ' '
            middle_name = str(row.middle_name)
            if last_name == "None ":
                last_name = 'Неаутентифицированный пользователь'
            if first_name == "None ":
                first_name = ''
            if middle_name == "None":
                middle_name = '' 
            f.write(f'{i+1},{last_name}{first_name}{middle_name},{row.count}\n'.encode("utf-8"))
        f.seek(0)
        return send_file(f, as_attachment=True, download_name="stat_users.csv", mimetype="text/csv")
        
    return render_template('visits/stat_users.html', stats = db_stat)

@bp.route('/logs')
@login_required
def logs():
    page = request.args.get('page', 1, type=int)
    query = '''
    SELECT visit_logs.*, users.login
    FROM visit_logs
    LEFT JOIN users ON visit_logs.user_id = users.id
    LIMIT %s
    OFFSET %s
    '''
    query_counter = 'SELECT count(*) as page_count FROM visit_logs'
    with db.connection.cursor(named_tuple = True) as cursor:
        cursor.execute(query,(PER_PAGE, PER_PAGE * (page - 1)))
        print(cursor.statement)
        db_logs = cursor.fetchall()

    with db.connection.cursor(named_tuple = True) as cursor:
        cursor.execute(query_counter)
        print(cursor.statement)
        db_counter = cursor.fetchone().page_count
    
    page_count = math.ceil(db_counter / PER_PAGE)
        
    return render_template('visits/logs.html', logs = db_logs, page = page, page_count = page_count)

