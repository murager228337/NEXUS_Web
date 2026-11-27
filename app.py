import os
import secrets
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from database import Database
from patterns.factory import TicketFactory
from patterns.observer import TicketManager, TicketNotification
from patterns.strategy import PriorityStrategyFactory
from patterns.decorator import TimestampDecorator
from patterns.adapter import FileLogger, FileLoggerAdapter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')
db = Database()
db.db_name = os.path.join(BASE_DIR, 'support.db')
db.initialize()
manager = TicketManager()
manager.attach(TimestampDecorator(TicketNotification()))
manager.attach(TimestampDecorator(
    FileLoggerAdapter(FileLogger(os.path.join(BASE_DIR, 'notifications.log')))
))
CATEGORIES = ('Network', 'Hardware', 'Software')
PRIORITIES = ('Low', 'Medium', 'High')
STATUSES = ('Open', 'In Progress', 'Closed')

@app.before_request
def csrf_protect():
    if 'csrf' not in session:
        session['csrf'] = secrets.token_hex(24)
    if request.method == 'POST' and not secrets.compare_digest(request.form.get('csrf', ''), session['csrf']):
        abort(400, 'Invalid CSRF token')

@app.context_processor
def context():
    return {'csrf': session.get('csrf', ''), 'current_user': session.get('user')}

def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapped

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('dashboard' if 'user' in session else 'login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = db.verify_user(request.form.get('username', '').strip(), request.form.get('password', ''))
        if user:
            session.clear()
            session['user'] = user
            session['csrf'] = secrets.token_hex(24)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.post('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.get('/dashboard')
@login_required
def dashboard():
    user = session['user']
    return render_template('dashboard.html', stats=db.get_ticket_stats(user['id'], user['role']), recent=db.get_recent_tickets(user['id'], user['role']))

@app.get('/tickets')
@login_required
def tickets():
    user = session['user']
    all_tickets = db.get_tickets(user['id'], user['role'])
    q = request.args.get('q', '').lower().strip()
    status = request.args.get('status', '')
    if q:
        all_tickets = [t for t in all_tickets if q in t[1].lower() or q in t[2].lower() or q in str(t[0])]
    if status in STATUSES:
        all_tickets = [t for t in all_tickets if t[5] == status]
    return render_template('tickets.html', tickets=all_tickets, categories=CATEGORIES, priorities=PRIORITIES, statuses=STATUSES, selected_status=status, q=q)

@app.post('/tickets/create')
@login_required
def create_ticket():
    user = session['user']
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    category = request.form.get('category', '')
    priority = request.form.get('priority', '')
    if not title or not description or len(title) > 150 or len(description) > 5000 or category not in CATEGORIES or priority not in PRIORITIES:
        flash('Please enter valid ticket details.', 'error')
        return redirect(url_for('tickets'))
    ticket = TicketFactory.create_ticket(category, title, description, priority, user['id'])
    db.create_ticket(ticket.title, ticket.description, category, ticket.priority, ticket.user_id)
    flash(PriorityStrategyFactory.get_strategy(priority).process(), 'success')
    return redirect(url_for('tickets'))

@app.post('/tickets/<int:ticket_id>/status')
@login_required
def update_status(ticket_id):
    if session['user']['role'] not in ('Admin', 'IT Support'):
        abort(403)
    status = request.form.get('status', '')
    if status not in STATUSES:
        abort(400)
    with db.connect() as conn:
        found = conn.execute('SELECT id FROM tickets WHERE id=?', (ticket_id,)).fetchone()
    if not found:
        abort(404)
    db.update_ticket_status(ticket_id, status)
    manager.change_status(ticket_id, status)
    flash(f'Ticket #{ticket_id} updated.', 'success')
    return redirect(url_for('tickets'))

@app.post('/tickets/<int:ticket_id>/duplicate')
@login_required
def duplicate_ticket(ticket_id):
    user = session['user']
    row = db.get_ticket(ticket_id)
    if not row or (user['role'] not in ('Admin', 'IT Support') and row[6] != user['id']):
        abort(404)
    original = TicketFactory.create_ticket(row[3], row[1], row[2], row[4], row[6])
    copy = original.clone()
    copy.title = f'Copy of {original.title}'[:150]
    copy.user_id = user['id']
    db.create_ticket(copy.title, copy.description, copy.category, copy.priority, copy.user_id)
    flash(f'Ticket duplicated as "{copy.title}".', 'success')
    return redirect(url_for('tickets'))

if __name__ == '__main__':
    app.run(debug=True)
