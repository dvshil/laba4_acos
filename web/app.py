import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_in_production'

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        database=os.environ.get('DB_NAME', 'phonebook_db'),
        user=os.environ.get('DB_USER', 'phonebook_user'),
        password=os.environ.get('DB_PASSWORD', 'secure_password_123')
    )

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM contacts ORDER BY id')
    contacts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', contacts=contacts, edit_id=None, contact=None)

@app.route('/', methods=['POST'])
def add_contact():
    full_name = request.form.get('full_name')
    phone_number = request.form.get('phone_number')
    note = request.form.get('note', '')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            'INSERT INTO contacts (full_name, phone_number, note) VALUES (%s, %s, %s)',
            (full_name, phone_number, note)
        )
        conn.commit()
        flash('Контакт успешно добавлен!', 'success')
    except psycopg2.IntegrityError:
        conn.rollback()
        flash('Контакт с таким номером телефона уже существует!', 'error')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('index'))

@app.route('/edit/<int:id>')
def edit(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM contacts WHERE id = %s', (id,))
    contact = cur.fetchone()
    cur.close()
    conn.close()
    
    if not contact:
        flash('Контакт не найден!', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM contacts ORDER BY id')
    contacts = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('index.html', contacts=contacts, edit_id=id, contact=contact)

@app.route('/edit/<int:id>', methods=['POST'])
def update_contact(id):
    full_name = request.form.get('full_name')
    phone_number = request.form.get('phone_number')
    note = request.form.get('note', '')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            'UPDATE contacts SET full_name = %s, phone_number = %s, note = %s WHERE id = %s',
            (full_name, phone_number, note, id)
        )
        conn.commit()
        flash('Контакт успешно обновлен!', 'success')
    except psycopg2.IntegrityError:
        conn.rollback()
        flash('Контакт с таким номером телефона уже существует!', 'error')
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM contacts WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Контакт успешно удален!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
