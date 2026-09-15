from flask import Flask, render_template, request, redirect, url_for # type: ignore
import sqlite3
from textblob import TextBlob    # type: ignore

app = Flask(__name__)

# Initialize DB
def init_db():
    conn = sqlite3.connect("warehouse.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    marks INTEGER NOT NULL,
                    feedback TEXT,
                    sentiment TEXT
                )''')
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = sqlite3.connect("warehouse.db")
    c = conn.cursor()
    c.execute("SELECT * FROM performance")
    data = c.fetchall()
    conn.close()
    return render_template("index.html", records=data)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form["student_name"]
        subject = request.form["subject"]
        marks = int(request.form["marks"])
        feedback = request.form["feedback"]

        # Sentiment analysis
        sentiment_score = TextBlob(feedback).sentiment.polarity
        if sentiment_score > 0:
            sentiment = "Positive"
        elif sentiment_score < 0:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        conn = sqlite3.connect("warehouse.db")
        c = conn.cursor()
        c.execute("INSERT INTO performance (student_name, subject, marks, feedback, sentiment) VALUES (?, ?, ?, ?, ?)",
                  (name, subject, marks, feedback, sentiment))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/view/<int:record_id>")
def view(record_id):
    conn = sqlite3.connect("warehouse.db")
    c = conn.cursor()
    c.execute("SELECT * FROM performance WHERE id=?", (record_id,))
    record = c.fetchone()
    conn.close()
    return render_template("view.html", record=record)

@app.route("/analytics")
def analytics():
    conn = sqlite3.connect("warehouse.db")
    c = conn.cursor()

    # Average marks per subject
    c.execute("SELECT subject, AVG(marks) FROM performance GROUP BY subject")
    avg_marks = c.fetchall()

    # Sentiment count
    c.execute("SELECT sentiment, COUNT(*) FROM performance GROUP BY sentiment")
    sentiments = c.fetchall()

    conn.close()

    return render_template(
        "analytics.html",
        avg_marks=avg_marks,
        sentiments=sentiments
    )
@app.route("/delete/<int:record_id>", methods=["POST"])
def delete(record_id):
    conn = sqlite3.connect("warehouse.db")
    c = conn.cursor()

    c.execute("DELETE FROM performance WHERE id=?", (record_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("index"))
if __name__ == "__main__":
    init_db()
    app.run(debug=True)

