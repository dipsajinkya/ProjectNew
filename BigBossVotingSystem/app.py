from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Import database configuration
from database_config import db_connection

# Candidate List
CANDIDATES = [
    "Ankita", "Aarya", "Abhijeet", "Arbaaz", "Dhanananjay", "Ghanshyam",
    "Irina", "Janhvi", "Nikhil", "Nikki", "Pandarinath", "Suraj",
    "Vaibhav", "Varsha", "Yogita"
]

@app.route('/')
def home():
    return render_template('home.html')

# Sign-up Route
@app.route('/index', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        voter_name = request.form['votername']
        password = request.form['password']
        email = request.form['email']
        address = request.form['address']

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO voter (name, password, email, address) VALUES (%s, %s, %s, %s)",
            (voter_name, hashed_password, email, address)
        )
        db_connection.commit()
        cursor.close()

        flash("Sign-up successful! Please login.")
        return redirect(url_for('login'))

    return render_template('index.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        voter_name = request.form['votername']
        password = request.form['password']

        cursor = db_connection.cursor()
        cursor.execute(
            "SELECT * FROM voter WHERE name=%s", (voter_name,)
        )
        voter = cursor.fetchone()
        cursor.close()

        if voter and check_password_hash(voter[2], password):  # Verify password
            session['voter_id'] = voter[0]
            flash("Login successful!")
            return redirect(url_for('candidates'))
        else:
            flash("Invalid votername or password.")  # Clear error message

    return render_template('login.html')

# List of Candidates
@app.route('/candidates')
def candidates():
    return render_template('candidates.html', candidates=CANDIDATES)

# Profile Route with Voting Logic
@app.route('/profile/<candidate_name>', methods=['GET', 'POST'])
def profile(candidate_name):
    if 'voter_id' not in session:  # Ensure user is logged in
        flash("Please log in to vote.")
        return redirect(url_for('login'))

    voter_id = session['voter_id']

    # Check if the voter has already voted
    cursor = db_connection.cursor()
    cursor.execute("SELECT candidate_name FROM votes WHERE voter_id=%s", (voter_id,))
    vote = cursor.fetchone()
    cursor.close()

    if vote:
        flash(f"You have already voted for {vote[0]}.")  # Display a flash message
        return redirect(url_for('candidates'))  # Redirect to candidates list with flash

    if request.method == 'POST':
        # Insert the vote if not already voted
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO votes (voter_id, candidate_name) VALUES (%s, %s)",
            (voter_id, candidate_name)
        )
        db_connection.commit()
        cursor.close()

        flash(f"You have voted for {candidate_name} successfully!")
        return redirect(url_for('vote_success', candidate_name=candidate_name))

    return render_template('profile.html', candidate_name=candidate_name)
@app.route('/vote_success/<candidate_name>')
def vote_success(candidate_name):
    return render_template('vote_success.html', candidate_name=candidate_name)

# Logout Route to Display Flash Message
@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    flash("You have been logged out.")
    return render_template('logout.html')

# Winner Calculation Route
@app.route('/winner')
def winner():
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT candidate_name, COUNT(*) AS votes FROM votes GROUP BY candidate_name ORDER BY votes DESC LIMIT 1"
    )
    winner = cursor.fetchone()
    cursor.close()

    if winner:
        return f"The winner is {winner[0]} with {winner[1]} votes."
    else:
        return "No votes yet."

if __name__ == '__main__':
    app.run(debug=True)
