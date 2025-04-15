from flask import Flask,render_template,request,redirect,url_for,session,g
import sqlite3,time,os
from werkzeug.security import generate_password_hash,check_password_hash

app=Flask(__name__)
app.secret_key='Rdjzan0sUsSP7KfPoheB'
BASE_DIR='/var/lib/chat_app'
DATABASE=os.path.join(BASE_DIR,'chat.db')
LOG_FILE=os.path.join('/var/log/chat_app','chat.log')

# Инициализация БД
def get_db():
    db=getattr(g,'_database',None)
    if db is None:db=g._database=sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(e):
    db=getattr(g,'_database',None)
    if db is not None:db.close()

def init_db():
    with app.app_context():
        db=get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL)''')
        db.execute('''CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id))''')
        db.commit()

# Маршруты
@app.route('/',methods=['GET','POST'])
def login():
    if 'username' in session:return redirect(url_for('chat'))
    error=None
    if request.method=='POST':
        u=request.form['username'].strip()
        p=request.form['password'].strip()
        db=get_db()
        if 'register' in request.form:  # Регистрация
            if db.execute('SELECT id FROM users WHERE username=?',(u,)).fetchone():
                error='Username exists'
            else:
                db.execute('INSERT INTO users(username,password)VALUES(?,?)',
                    (u,generate_password_hash(p)))
                db.commit()
                session['username']=u
                return redirect(url_for('chat'))
        else:  # Вход
            user=db.execute('SELECT id,password FROM users WHERE username=?',(u,)).fetchone()
            if not user or not check_password_hash(user[1],p):
                error='Invalid credentials'
            else:
                session['username']=u
                return redirect(url_for('chat'))
    return render_template('login.html',error=error)

@app.route('/chat',methods=['GET','POST'])
def chat():
    if 'username' not in session:return redirect(url_for('login'))
    if request.method=='POST':  # Обработка сообщения
        m=request.form['message'].strip()
        if m:
            db=get_db()
            uid=db.execute('SELECT id FROM users WHERE username=?',
                (session['username'],)).fetchone()[0]
            db.execute('INSERT INTO messages(user_id,username,message,timestamp)VALUES(?,?,?,?)',
                (uid,session['username'],m,int(time.time())))
            db.commit()
        return redirect(url_for('chat'))  # PRG-паттерн
    
    # Получение сообщений (без лимита)
    msgs=get_db().execute('''
        SELECT username,message,timestamp FROM messages 
        ORDER BY timestamp ASC''').fetchall()
    return render_template('chat.html',
        username=session['username'],
        messages=[(m[0],m[1],time.strftime('%H:%M:%S',time.localtime(m[2])))for m in msgs])

@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('login'))

# Инициализация
if __name__=='__main__':
    os.makedirs(BASE_DIR,exist_ok=True)
    os.makedirs(os.path.dirname(LOG_FILE),exist_ok=True)
    try:
        os.chmod(BASE_DIR,0o750)
        if os.path.exists(DATABASE):os.chmod(DATABASE,0o600)
    except PermissionError as e:print(f'Warning:{e}')
    init_db()
