from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import os

def setup_database():
    conn = sqlite3.connect("tattoo_inks.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        expiry_date TEXT NOT NULL,
                        batch_number TEXT NOT NULL)''')
    conn.commit()
    conn.close()

app = Flask(__name__)
setup_database()

@app.route('/')
def index():
    conn = sqlite3.connect("tattoo_inks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inks")
    inks = cursor.fetchall()
    conn.close()
    return render_template("index.html", inks=inks)

@app.route('/add_ink', methods=['POST'])
def add_ink():
    name = request.form["name"].strip()
    expiry_date = request.form["expiry_date"].strip()
    batch_number = request.form["batch_number"].strip()
    
    if name and expiry_date and batch_number:
        conn = sqlite3.connect("tattoo_inks.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inks (name, expiry_date, batch_number) VALUES (?, ?, ?)",
                       (name, expiry_date, batch_number))
        conn.commit()
        conn.close()
    return redirect(url_for("index"))

@app.route('/delete_ink/<int:ink_id>')
def delete_ink(ink_id):
    conn = sqlite3.connect("tattoo_inks.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inks WHERE id=?", (ink_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route('/select_inks', methods=['GET', 'POST'])
def select_inks():
    if request.method == 'POST':
        selected_inks = request.form.getlist("inks")
        client_name = request.form["client_name"].strip()
        date = request.form["date"].strip()
        
        report_text = f"Tattoo Session Ink Report\nClient: {client_name}\nDate: {date}\n\n"
        conn = sqlite3.connect("tattoo_inks.db")
        cursor = conn.cursor()
        
        for ink_id in selected_inks:
            cursor.execute("SELECT * FROM inks WHERE id=?", (ink_id,))
            ink = cursor.fetchone()
            report_text += f"Name: {ink[1]}, Expiry: {ink[2]}, Batch: {ink[3]}\n"
        
        conn.close()
        report_path = "tattoo_report.txt"
        with open(report_path, "w") as file:
            file.write(report_text)
        
        return send_file(report_path, as_attachment=True)
    
    conn = sqlite3.connect("tattoo_inks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inks")
    inks = cursor.fetchall()
    conn.close()
    return render_template("select_inks.html", inks=inks)

if __name__ == '__main__':
    app.run(debug=True)
