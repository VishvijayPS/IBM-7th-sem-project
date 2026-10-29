"""LibraryHub: a transactional Flask library management system."""
from datetime import date, timedelta
from functools import wraps
import csv, io, os, sqlite3
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for, Response
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get('LIBRARYHUB_DB', os.path.join(BASE_DIR, 'libraryhub.db'))
LOAN_DAYS, FINE_PER_DAY = 14, 5
MAX_ACTIVE_LOANS = int(os.environ.get('LIBRARYHUB_LOAN_LIMIT', '3'))
app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY', 'change-this-secret-before-deployment'), SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')
SAMPLE_BOOKS = [('The Silent Patient','Alex Michaelides','9781250301697','Fiction',4),('Atomic Habits','James Clear','9780735211292','Self-help',5),('Clean Code','Robert C. Martin','9780132350884','Technology',3),('The Alchemist','Paulo Coelho','9780062315007','Fiction',4),('A Brief History of Time','Stephen Hawking','9780553380163','Science',2),('Introduction to Algorithms','Thomas H. Cormen','9780262046305','Technology',2)]

def db():
    con=sqlite3.connect(DB_PATH, timeout=10); con.row_factory=sqlite3.Row; con.execute('PRAGMA foreign_keys=ON'); return con

def init_db():
    with db() as con:
        con.executescript('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT NOT NULL,email TEXT NOT NULL UNIQUE COLLATE NOCASE,password_hash TEXT NOT NULL,role TEXT NOT NULL CHECK(role IN ('admin','student')),created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS books(id INTEGER PRIMARY KEY,title TEXT NOT NULL,author TEXT NOT NULL,isbn TEXT NOT NULL UNIQUE,category TEXT NOT NULL,total_copies INTEGER NOT NULL CHECK(total_copies>=0),available_copies INTEGER NOT NULL CHECK(available_copies>=0 AND available_copies<=total_copies));
        CREATE TABLE IF NOT EXISTS loans(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id),book_id INTEGER NOT NULL REFERENCES books(id),issued_on TEXT NOT NULL,due_on TEXT NOT NULL,returned_on TEXT,fine_rupees INTEGER NOT NULL DEFAULT 0 CHECK(fine_rupees>=0),paid_rupees INTEGER NOT NULL DEFAULT 0 CHECK(paid_rupees>=0 AND paid_rupees<=fine_rupees));
        CREATE INDEX IF NOT EXISTS idx_loans_active ON loans(returned_on,due_on);''')
        if con.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0]==0: con.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,'admin')",('Library Administrator','admin@library.local',generate_password_hash('Admin@123')))
        if con.execute('SELECT COUNT(*) FROM books').fetchone()[0]==0: con.executemany('INSERT INTO books(title,author,isbn,category,total_copies,available_copies) VALUES(?,?,?,?,?,?)',[(t,a,i,c,n,n) for t,a,i,c,n in SAMPLE_BOOKS])

def login_required(fn):
    @wraps(fn)
    def wrapped(*a,**kw):
        if not session.get('user_id'): flash('Please sign in to continue.','error'); return redirect(url_for('login',next=request.path))
        return fn(*a,**kw)
    return wrapped

def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapped(*a,**kw):
        if session.get('role')!='admin': abort(403)
        return fn(*a,**kw)
    return wrapped

def current_user():
    if not session.get('user_id'): return None
    with db() as con: return con.execute('SELECT id,name,email,role FROM users WHERE id=?',(session['user_id'],)).fetchone()

@app.context_processor
def inject_globals(): return {'current_user':current_user(),'today':date.today().isoformat(),'loan_limit':MAX_ACTIVE_LOANS}

@app.route('/')
def index():
    q=request.args.get('q','').strip()
    with db() as con: books=con.execute("SELECT * FROM books WHERE (?='' OR title LIKE ? OR author LIKE ? OR isbn LIKE ? OR category LIKE ?) ORDER BY title LIMIT 30",(q,*([f'%{q}%']*4))).fetchall()
    return render_template('index.html',books=books,q=q)

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=request.form.get('name','').strip(); email=request.form.get('email','').strip().lower(); password=request.form.get('password','')
        if len(name)<2 or len(name)>100: flash('Enter a name between 2 and 100 characters.','error')
        elif '@' not in email or len(email)>254: flash('Enter a valid email address.','error')
        elif len(password)<8: flash('Password must be at least 8 characters.','error')
        else:
            try:
                with db() as con: con.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,'student')",(name,email,generate_password_hash(password)))
                flash('Account created. You can now sign in.','success'); return redirect(url_for('login'))
            except sqlite3.IntegrityError: flash('That email is already registered.','error')
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        with db() as con: user=con.execute('SELECT * FROM users WHERE email=?',(request.form.get('email','').strip().lower(),)).fetchone()
        if user and check_password_hash(user['password_hash'],request.form.get('password','')):
            session.clear(); session.update(user_id=user['id'],name=user['name'],role=user['role']); return redirect(url_for('admin_dashboard' if user['role']=='admin' else 'student_dashboard'))
        flash('Email or password is incorrect.','error')
    return render_template('login.html')

@app.post('/logout')
def logout(): session.clear(); flash('You have signed out.','success'); return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    with db() as con:
        stats={'copies':con.execute('SELECT COALESCE(SUM(total_copies),0) FROM books').fetchone()[0],'titles':con.execute('SELECT COUNT(*) FROM books').fetchone()[0],'students':con.execute("SELECT COUNT(*) FROM users WHERE role='student'").fetchone()[0],'active':con.execute('SELECT COUNT(*) FROM loans WHERE returned_on IS NULL').fetchone()[0],'overdue':con.execute("SELECT COUNT(*) FROM loans WHERE returned_on IS NULL AND due_on<?",(date.today().isoformat(),)).fetchone()[0],'fines':con.execute('SELECT COALESCE(SUM(fine_rupees-paid_rupees),0) FROM loans').fetchone()[0]}
        recent=con.execute('SELECT l.*,u.name student,b.title FROM loans l JOIN users u ON u.id=l.user_id JOIN books b ON b.id=l.book_id ORDER BY l.id DESC LIMIT 8').fetchall()
    return render_template('admin_dashboard.html',stats=stats,recent=recent)

@app.route('/books')
@admin_required
def manage_books():
    q=request.args.get('q','').strip()
    with db() as con: books=con.execute("SELECT * FROM books WHERE (?='' OR title LIKE ? OR author LIKE ? OR isbn LIKE ? OR category LIKE ?) ORDER BY title",(q,*([f'%{q}%']*4))).fetchall()
    return render_template('manage_books.html',books=books,q=q)

@app.route('/books/new',methods=['GET','POST'])
@app.route('/books/<int:book_id>/edit',methods=['GET','POST'])
@admin_required
def book_form(book_id=None):
    with db() as con: book=con.execute('SELECT * FROM books WHERE id=?',(book_id,)).fetchone() if book_id else None
    if book_id and not book: abort(404)
    if request.method=='POST':
        title,author,isbn,category=[request.form.get(k,'').strip() for k in ('title','author','isbn','category')]
        try: total=int(request.form.get('total_copies',''))
        except ValueError: total=-1
        if not all((title,author,isbn,category)): flash('All book fields are required.','error')
        elif total<0: flash('Total copies must be zero or more.','error')
        elif book and total<book['total_copies']-book['available_copies']: flash('Total copies cannot be less than copies currently on loan.','error')
        else:
            try:
                with db() as con:
                    if book: con.execute('UPDATE books SET title=?,author=?,isbn=?,category=?,total_copies=?,available_copies=? WHERE id=?',(title,author,isbn,category,total,total-(book['total_copies']-book['available_copies']),book_id))
                    else: con.execute('INSERT INTO books(title,author,isbn,category,total_copies,available_copies) VALUES(?,?,?,?,?,?)',(title,author,isbn,category,total,total))
                flash('Book saved.','success'); return redirect(url_for('manage_books'))
            except sqlite3.IntegrityError: flash('ISBN must be unique.','error')
    return render_template('book_form.html',book=book)

@app.post('/books/<int:book_id>/delete')
@admin_required
def delete_book(book_id):
    with db() as con:
        if con.execute('SELECT COUNT(*) FROM loans WHERE book_id=? AND returned_on IS NULL',(book_id,)).fetchone()[0]: flash('Return all active loans before deleting this book.','error')
        else:
            try: con.execute('DELETE FROM books WHERE id=?',(book_id,)); flash('Book deleted.','success')
            except sqlite3.IntegrityError: flash('This book has loan history and cannot be deleted.','error')
    return redirect(url_for('manage_books'))

@app.route('/students')
@admin_required
def students():
    with db() as con: rows=con.execute("SELECT u.*,COUNT(CASE WHEN l.returned_on IS NULL THEN 1 END) active FROM users u LEFT JOIN loans l ON l.user_id=u.id WHERE u.role='student' GROUP BY u.id ORDER BY u.name").fetchall()
    return render_template('students.html',students=rows)

@app.route('/issue',methods=['GET','POST'])
@admin_required
def issue():
    with db() as con: books=con.execute('SELECT * FROM books WHERE available_copies>0 ORDER BY title').fetchall(); students=con.execute("SELECT id,name,email FROM users WHERE role='student' ORDER BY name").fetchall()
    if request.method=='POST':
        try: sid=int(request.form.get('student_id','')); bid=int(request.form.get('book_id',''))
        except ValueError: flash('Choose a valid student and book.','error'); return redirect(url_for('issue'))
        try:
            with db() as con:
                con.execute('BEGIN IMMEDIATE'); student=con.execute("SELECT id FROM users WHERE id=? AND role='student'",(sid,)).fetchone(); book=con.execute('SELECT id,available_copies FROM books WHERE id=?',(bid,)).fetchone(); active=con.execute('SELECT COUNT(*) FROM loans WHERE user_id=? AND returned_on IS NULL',(sid,)).fetchone()[0]
                if not student or not book: raise ValueError('Choose a valid student and book.')
                if active>=MAX_ACTIVE_LOANS: raise ValueError(f'A student may have at most {MAX_ACTIVE_LOANS} active loans.')
                if book['available_copies']<1: raise ValueError('That book is currently unavailable.')
                now=date.today(); con.execute('INSERT INTO loans(user_id,book_id,issued_on,due_on) VALUES(?,?,?,?)',(sid,bid,now.isoformat(),(now+timedelta(days=LOAN_DAYS)).isoformat())); con.execute('UPDATE books SET available_copies=available_copies-1 WHERE id=? AND available_copies>0',(bid,))
            flash('Book issued. It is due in 14 days.','success'); return redirect(url_for('loans'))
        except ValueError as e: flash(str(e),'error')
    return render_template('issue.html',books=books,students=students)

@app.route('/loans')
@admin_required
def loans():
    filt=request.args.get('filter','all'); cond="WHERE l.returned_on IS NULL" if filt=='active' else "WHERE l.returned_on IS NULL AND l.due_on<date('now','localtime')" if filt=='overdue' else ''
    with db() as con: rows=con.execute(f"SELECT l.*,u.name student,u.email,b.title,b.author,MAX(0,CAST(julianday(COALESCE(l.returned_on,date('now','localtime')))-julianday(l.due_on) AS INTEGER))*? estimated_fine FROM loans l JOIN users u ON u.id=l.user_id JOIN books b ON b.id=l.book_id {cond} ORDER BY l.returned_on IS NULL DESC,l.due_on",(FINE_PER_DAY,)).fetchall()
    return render_template('loans.html',loans=rows,filter=filt)

@app.post('/loans/<int:loan_id>/return')
@admin_required
def return_book(loan_id):
    with db() as con:
        con.execute('BEGIN IMMEDIATE'); loan=con.execute('SELECT * FROM loans WHERE id=?',(loan_id,)).fetchone()
        if not loan: flash('Loan record not found.','error')
        elif loan['returned_on']: flash('This book has already been returned.','error')
        else:
            returned=date.today(); fine=max(0,(returned-date.fromisoformat(loan['due_on'])).days)*FINE_PER_DAY
            con.execute('UPDATE loans SET returned_on=?,fine_rupees=? WHERE id=? AND returned_on IS NULL',(returned.isoformat(),fine,loan_id))
            if con.execute('SELECT changes()').fetchone()[0]==1: con.execute('UPDATE books SET available_copies=available_copies+1 WHERE id=? AND available_copies<total_copies',(loan['book_id'],)); flash(f'Return recorded. Fine: ₹{fine}.','success')
    return redirect(request.referrer or url_for('loans'))

@app.post('/loans/<int:loan_id>/pay')
@admin_required
def pay_fine(loan_id):
    try: amount=int(request.form.get('amount',''))
    except ValueError: amount=0
    if amount<=0: flash('Payment must be a positive whole number of rupees.','error')
    else:
        with db() as con:
            loan=con.execute('SELECT * FROM loans WHERE id=?',(loan_id,)).fetchone()
            if not loan: flash('Loan record not found.','error')
            elif amount>loan['fine_rupees']-loan['paid_rupees']: flash('Payment exceeds the outstanding fine.','error')
            else: con.execute('UPDATE loans SET paid_rupees=paid_rupees+? WHERE id=? AND paid_rupees+?<=fine_rupees',(amount,loan_id,amount)); flash(f'Payment of ₹{amount} recorded.','success')
    return redirect(request.referrer or url_for('loans'))

@app.route('/student')
@login_required
def student_dashboard():
    if session['role']!='student': return redirect(url_for('admin_dashboard'))
    with db() as con: rows=con.execute("SELECT l.*,b.title,b.author,MAX(0,CAST(julianday(COALESCE(l.returned_on,date('now','localtime')))-julianday(l.due_on) AS INTEGER))*? fine_due FROM loans l JOIN books b ON b.id=l.book_id WHERE l.user_id=? ORDER BY l.id DESC",(FINE_PER_DAY,session['user_id'])).fetchall()
    return render_template('student_dashboard.html',loans=rows,active=sum(1 for x in rows if x['returned_on'] is None))

@app.route('/reports')
@admin_required
def reports():
    with db() as con:
        summary=con.execute("SELECT COUNT(*) total,SUM(CASE WHEN returned_on IS NULL THEN 1 ELSE 0 END) active,SUM(CASE WHEN returned_on IS NULL AND due_on<date('now','localtime') THEN 1 ELSE 0 END) overdue,COALESCE(SUM(fine_rupees),0) fines,COALESCE(SUM(paid_rupees),0) paid FROM loans").fetchone(); categories=con.execute('SELECT category,COUNT(*) titles,SUM(total_copies) copies,SUM(available_copies) available FROM books GROUP BY category ORDER BY category').fetchall()
    return render_template('reports.html',summary=summary,categories=categories)

@app.route('/reports/export.csv')
@admin_required
def export_csv():
    out=io.StringIO(); w=csv.writer(out); w.writerow(['Loan ID','Student','Email','Book','ISBN','Issued','Due','Returned','Fine (INR)','Paid (INR)'])
    with db() as con: rows=con.execute('SELECT l.id,u.name,u.email,b.title,b.isbn,l.issued_on,l.due_on,l.returned_on,l.fine_rupees,l.paid_rupees FROM loans l JOIN users u ON u.id=l.user_id JOIN books b ON b.id=l.book_id ORDER BY l.id').fetchall()
    w.writerows([tuple(r) for r in rows]); return Response('\ufeff'+out.getvalue(),mimetype='text/csv',headers={'Content-Disposition':'attachment; filename=libraryhub-loans.csv'})

@app.errorhandler(403)
def forbidden(_): return render_template('error.html',code=403,message='You do not have permission to view this page.'),403
@app.errorhandler(404)
def not_found(_): return render_template('error.html',code=404,message='The page or record could not be found.'),404

init_db()
if __name__=='__main__': app.run(debug=os.environ.get('FLASK_DEBUG')=='1',host='127.0.0.1',port=int(os.environ.get('PORT','5000')))
