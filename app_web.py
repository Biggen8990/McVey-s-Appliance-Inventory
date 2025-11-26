from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
import os
import csv

app = Flask(__name__)
app.secret_key = 'supersecretkey'

import os
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///appliances.db')

db = SQLAlchemy(app)

from datetime import datetime

class Appliance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(80), nullable=False)
    item_number = db.Column(db.String(80), nullable=False)
    brand = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    serial = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(40), nullable=False)
    notes = db.Column(db.String(255))
    archived = db.Column(db.Boolean, default=False)
    invoice_file = db.Column(db.String(255))
    last_updated = db.Column(db.String(30), nullable=False, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class StatusHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appliance_id = db.Column(db.Integer, db.ForeignKey('appliance.id'))
    timestamp = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(40), nullable=False)
    appliance = db.relationship('Appliance', backref='status_history')

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(30), nullable=False)
    action = db.Column(db.String(80), nullable=False)
    details = db.Column(db.String(255), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'store'
    store = db.Column(db.String(80))  # Only for stores
    active = db.Column(db.Boolean, default=True)

from datetime import datetime

def log_action(action, details):
    entry = AuditLog(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        action=action,
        details=details
    )
    db.session.add(entry)
    db.session.commit()

from werkzeug.security import check_password_hash

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, active=True).first()
        if user and check_password_hash(user.password_hash, password):
            session['username'] = username
            session['role'] = user.role
            session['store'] = user.store
            if user.role == 'admin':
                return redirect('/admin-dashboard')
            else:
                return redirect('/store-portal')
        else:
            error = "Invalid credentials"
    return render_template('login.html', error=error)

@app.route('/manage-users')
def manage_users():
    if session.get('role') != 'admin':
        return redirect('/')
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/deactivate-user/<int:user_id>', methods=['POST'])
def deactivate_user(user_id):
    if session.get('role') != 'admin':
        return redirect('/')
    user = User.query.get(user_id)
    if user:
        user.active = False
        db.session.commit()
        flash("User deactivated.", "success")
    return redirect('/manage-users')

@app.route('/activate-user/<int:user_id>', methods=['POST'])
def activate_user(user_id):
    if session.get('role') != 'admin':
        return redirect('/')
    user = User.query.get(user_id)
    if user:
        user.active = True
        db.session.commit()
        flash("User activated.", "success")
    return redirect('/manage-users')

from werkzeug.security import generate_password_hash

@app.route('/change-password/<int:user_id>', methods=['GET', 'POST'])
def change_password(user_id):
    # Only allow admin or the user themselves to change password
    user = User.query.get(user_id)
    if not user or (session['role'] != 'admin' and session['username'] != user.username):
        return redirect('/')
    error = None
    if request.method == 'POST':
        new_password = request.form['new_password']
        user.password_hash = generate_password_hash(new_password, method="pbkdf2:sha256")
        db.session.commit()
        flash('Password changed successfully', 'success')
        return redirect('/manage-users')
    return render_template('change_password.html', user=user, error=error)

from werkzeug.security import generate_password_hash

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Only allow admin to register new users
    if not session.get('role') == 'admin':
        return redirect('/')
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        store = request.form['store'] if role == 'store' else None

        # Check if username exists
        if User.query.filter_by(username=username).first():
            error = 'That username is already taken.'
        else:
            user = User(
                username=username,
                password_hash=generate_password_hash(password, method="pbkdf2:sha256"),
                role=role,
                store=store
            )
            db.session.add(user)
            db.session.commit()
            flash('User created successfully!', 'success')
            return redirect('/admin-dashboard')
    return render_template('register.html', error=error)

from flask import Response

@app.route('/file-options')
def file_options_web():
    if session.get('role') != 'admin':
        return redirect('/')
    return render_template('file_options.html')

@app.route('/export-audit-csv')
def export_audit_csv_web():
    if session.get('role') != 'admin':
        return redirect('/')
    import io
    output = io.StringIO()
    fieldnames = ['timestamp', 'action', 'details']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for entry in AuditLog.query.all():
        writer.writerow({
            'timestamp': entry.timestamp,
            'action': entry.action,
            'details': entry.details,
        })
    csv_data = output.getvalue()
    output.close()
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=audit_log.csv'}
    )

@app.route('/import-csv', methods=['POST'])
def import_csv_web():
    if session.get('role') != 'admin':
        return redirect('/')
    file = request.files.get('csvfile')
    if not file:
        return redirect('/file-options')
    import io
    stream = io.StringIO(file.stream.read().decode('UTF8'), newline=None)
    reader = csv.DictReader(stream)
    for row in reader:
        if 'store_name' in row and 'item_number' in row:
            exists = Appliance.query.filter_by(
                store_name=row['store_name'],
                item_number=row['item_number']
            ).first()
            if not exists:
                new_app = Appliance(
                    store_name=row['store_name'],
                    item_number=row['item_number'],
                    brand=row.get('brand', ''),
                    model=row.get('model', ''),
                    serial=row.get('serial', ''),
                    status=row.get('status', ''),
                    notes=row.get('notes', ''),
                    archived=False,
                    invoice_file=None
                )
                db.session.add(new_app)
    db.session.commit()
    return redirect('/file-options')

@app.route('/bulk-actions', methods=['GET', 'POST'])
def bulk_actions_web():
    if session.get('role') != 'admin':
        return redirect('/')
    message = ""
    if request.method == 'POST':
        store = request.form['store_name']
        status = request.form['status']
        action = request.form['action']
        count = 0

        # Use a database query to get all appliances with the right store and status!
        apps = Appliance.query.filter_by(store_name=store, status=status).all()
        for app_rec in apps:
            if action == 'archive' and not app_rec.archived:
                app_rec.archived = True
                count += 1
            elif action == 'unarchive' and app_rec.archived:
                app_rec.archived = False
                count += 1
        db.session.commit()
        message = f"{count} appliances {'archived' if action == 'archive' else 'restored'}."

    stores = sorted(set(app.store_name for app in Appliance.query.all()))
    return render_template('bulk_actions.html', stores=stores, status_options=STATUS_OPTIONS, message=message)

import csv
import io
from flask import Response

@app.route('/export-csv')
def export_csv_web():
    if session.get('role') != 'admin':
        return redirect('/')
    import io
    output = io.StringIO()
    fieldnames = ['store_name', 'item_number', 'brand', 'model', 'serial', 'status', 'notes']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for app in Appliance.query.filter_by(archived=False).all():
        writer.writerow({
            'store_name': app.store_name,
            'item_number': app.item_number,
            'brand': app.brand,
            'model': app.model,
            'serial': app.serial,
            'status': app.status,
            'notes': app.notes,
        })
    csv_data = output.getvalue()
    output.close()
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=appliances.csv'}
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

STATUS_OPTIONS = ["In", "Checked", "Parts Ordered", "Repaired", "Loaded", "Delivered"]

@app.route('/admin-dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/')
    summary = {}
    for app_rec in Appliance.query.filter_by(archived=False).all():
        store = app_rec.store_name
        status = app_rec.status
        summary.setdefault(store, {})
        summary[store][status] = summary[store].get(status, 0) + 1
    return render_template('admin_dashboard.html', summary=summary)

UPLOAD_FOLDER = 'invoices'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from flask import flash

@app.route('/add', methods=['GET', 'POST'])
def add_appliance_web():
    if request.method == 'POST':
        new_app = Appliance(
            store_name=request.form['store_name'],
            item_number=request.form['item_number'],
            brand=request.form['brand'],
            model=request.form['model'],
            serial=request.form['serial'],
            status=request.form['status'],
            notes=request.form['notes'],
            archived=False,
            invoice_file=None
        )
        db.session.add(new_app)
        db.session.commit()
        log_action('add', f'Added {new_app.store_name}/{new_app.item_number}')
        flash('Appliance added successfully', 'success')
        return redirect('/admin-dashboard')
    return render_template('add.html', status_options=STATUS_OPTIONS)

@app.route('/view-audit-log')
def view_audit_log():
    if session.get('role') != 'admin':
        return redirect('/')
    log = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    return render_template('view_audit_log.html', log=log)

from datetime import datetime
from flask import flash

@app.route('/edit/<store_name>/<item_number>', methods=['GET', 'POST'])
def edit_appliance_web(store_name, item_number):
    app_rec = Appliance.query.filter_by(store_name=store_name, item_number=item_number).first()
    if not app_rec:
        return 'Appliance not found', 404
    if request.method == 'POST':
        old_store = app_rec.store_name
        old_item = app_rec.item_number
        old_status = app_rec.status
        app_rec.store_name = request.form['store_name']
        app_rec.item_number = request.form['item_number']
        app_rec.brand = request.form['brand']
        app_rec.model = request.form['model']
        app_rec.serial = request.form['serial']
        app_rec.status = request.form['status']
        app_rec.notes = request.form['notes']
        # Status history log
        if app_rec.status != old_status:
            new_history = StatusHistory(
                appliance_id=app_rec.id,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                status=app_rec.status
            )
            db.session.add(new_history)
        app_rec.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Invoice logic...
        if app_rec.status.lower() in ["delivered", "loaded"]:
            file = request.files.get('invoice')
            if file and file.filename:
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                app_rec.invoice_file = filename
                flash('Invoice Added Successfully', 'success')
        db.session.commit()
        log_action('edit', f'Edited {app_rec.store_name}/{app_rec.item_number}')
        flash('Appliance Updated', 'success')
        # If store or item number changed, redirect to the new edit URL
        if (app_rec.store_name != old_store) or (app_rec.item_number != old_item):
            return redirect(f"/edit/{app_rec.store_name}/{app_rec.item_number}")
        return redirect('/list')
    return render_template('edit.html', appliance=app_rec, status_options=STATUS_OPTIONS)

@app.route('/list')
def list_appliances_web():
    active = Appliance.query.filter_by(archived=False).all()
    return render_template('list.html', appliances=active)

@app.route('/details/<store_name>/<item_number>')
def details_web(store_name, item_number):
    app_rec = Appliance.query.filter_by(store_name=store_name, item_number=item_number).first()
    if not app_rec:
        return 'Appliance not found', 404
    return render_template('details.html', appliance=app_rec)

from datetime import datetime

@app.route('/archived')
def view_archived_web():
    archived = Appliance.query.filter_by(archived=True).all()
    return render_template('archived.html', appliances=archived)

from datetime import datetime
from flask import flash

@app.route('/archive/<store_name>/<item_number>', methods=['POST'])
def archive_web(store_name, item_number):
    app_rec = Appliance.query.filter_by(store_name=store_name, item_number=item_number).first()
    if app_rec:
        if app_rec.archived:
            flash("Item already archived.", "error")
        else:
            app_rec.archived = True
            app_rec.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.session.commit()
            log_action('archive', f'Archived {app_rec.store_name}/{app_rec.item_number}')
            flash("Appliance archived.", "success")
        return redirect('/list')
    flash("Appliance not found.", "error")
    return redirect('/list')

from datetime import datetime
from flask import flash

@app.route('/unarchive/<store_name>/<item_number>', methods=['POST'])
def unarchive_web(store_name, item_number):
    app_rec = Appliance.query.filter_by(store_name=store_name, item_number=item_number, archived=True).first()
    if app_rec:
        app_rec.archived = False
        app_rec.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.session.commit()
        log_action('unarchive', f'Unarchived {app_rec.store_name}/{app_rec.item_number}')
        flash('Item Unarchived', 'success')
        return redirect('/archived')
    return "Appliance not found or not archived.", 404

@app.route('/invoice-search', methods=['GET', 'POST'])
def invoice_search():
    results = []
    query = ""
    if request.method == 'POST':
        query = request.form['query'].strip().lower()
        print("Query:", query)
        print("Invoice files in DB:", [a.invoice_file for a in Appliance.query.all()])
        if query:
            results = Appliance.query.filter(
                Appliance.invoice_file.ilike(f"%{query}%")
            ).all()
        else:
            results = Appliance.query.filter(Appliance.invoice_file != None).all()
    return render_template('invoice_search.html', appliances=results, query=query)

@app.route('/store-portal')
def store_portal():
    store = session.get('store')
    store_items = Appliance.query.filter_by(store_name=store, archived=False).all()
    user = User.query.filter_by(username=session['username']).first()
    return render_template('store_portal.html', appliances=store_items, store=store, user=user)

@app.route('/invoices/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

from flask import flash

@app.route('/search', methods=['GET', 'POST'])
def search_appliances():
    if session.get('role') != 'admin':
        return redirect('/')
    results = []
    query = ""
    if request.method == 'POST':
        query = request.form['query'].strip().lower()
        if query:
            results = Appliance.query.filter(
                (Appliance.store_name.ilike(f"%{query}%")) |
                (Appliance.brand.ilike(f"%{query}%")) |
                (Appliance.model.ilike(f"%{query}%")) |
                (Appliance.serial.ilike(f"%{query}%")) |
                (Appliance.item_number.ilike(f"%{query}%")) |
                (Appliance.status.ilike(f"%{query}%"))
            ).filter_by(archived=False).all()
            if not results and query:
                flash('Item Not Found', 'error')
    return render_template('search.html', appliances=results, query=query)

@app.route('/create-default-admin')
def create_default_admin():
    from werkzeug.security import generate_password_hash
    if User.query.filter_by(username='admin').first():
        return "Admin user already exists."
    admin = User(
        username="admin",
        password_hash=generate_password_hash("main", method="pbkdf2:sha256"),
        role="admin",
        store=None,
        active=True  # If you have an `active` field
    )
    db.session.add(admin)
    db.session.commit()
    return "Admin user created! You can now log in as admin/main."

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

