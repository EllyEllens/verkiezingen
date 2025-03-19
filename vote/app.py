from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import time

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Nodig voor sessies

# Databaseconfiguratie
db_config = {
    'host': 'localhost',
    'user': 'root',  
    'password': '',  
    'database': 'stemapp'
}

# Splash Screen route
@app.route('/')
def index():
    time.sleep(7)  # Wacht 7 seconden voordat naar de homepage wordt verwezen
    return redirect(url_for('home'))  

# Route voor de homepage
@app.route('/home')
def home():
    return render_template('home.html')

# Route voor de instructies-pagina
@app.route('/instructies')
def instructies():
    return render_template('instructies.html')

# Route voor registratie
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        id_card_number = request.form['id_card_number']
        voting_code = request.form['voting_code']

        # Verbinden met de database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        try:
            # Invoegen van de gebruiker in de database
            cursor.execute("INSERT INTO users (id_card_number, voting_code) VALUES (%s, %s)", (id_card_number, voting_code))
            conn.commit()
            flash('Registratie succesvol! Je kunt nu inloggen.', 'success')
        except mysql.connector.IntegrityError:
            flash('ID-kaartnummer of stembiljetcode bestaat al!', 'error')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('register'))

    return render_template('register.html')

# Route voor inloggen
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id_card_number = request.form['id_card_number']
        voting_code = request.form['voting_code']

        if id_card_number == 'AD2025' and voting_code == '000':
            return redirect(url_for('register'))

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id_card_number = %s AND voting_code = %s", (id_card_number, voting_code))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['id_card_number'] = user['id_card_number']
            return redirect(url_for('vote'))
        else:
            flash('Ongeldig ID-kaartnummer of stembiljetcode!', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# Route voor stemmen
@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT has_voted FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()

    if user['has_voted']:
        flash('Je hebt al gestemd!', 'info')
        return redirect(url_for('results'))

    if request.method == 'POST':
        candidate_id = request.form['candidate']
        cursor.execute("UPDATE candidates SET vote_count = vote_count + 1 WHERE id = %s", (candidate_id,))
        cursor.execute("UPDATE users SET has_voted = TRUE WHERE id = %s", (session['user_id'],))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Bedankt voor je stem!', 'success')
        return redirect(url_for('results'))

    cursor.execute(""" 
        SELECT c.id, c.name AS candidate_name, p.name AS party_name 
        FROM candidates c 
        JOIN parties p ON c.party_id = p.id
    """)
    candidates = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('vote.html', candidates=candidates)

# Route voor resultaten bekijken
@app.route('/results')
def results():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute(""" 
        SELECT c.id, c.name AS candidate_name, p.name AS party_name, c.vote_count 
        FROM candidates c 
        JOIN parties p ON c.party_id = p.id
    """)
    candidates = cursor.fetchall()

    cursor.execute(""" 
        SELECT p.name AS party_name, SUM(c.vote_count) AS total_votes 
        FROM candidates c 
        JOIN parties p ON c.party_id = p.id 
        GROUP BY p.name
    """)
    parties = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('results.html', candidates=candidates, parties=parties)

# Route voor uitloggen
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
