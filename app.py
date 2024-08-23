from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
from config import get_db_connection

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/exam', methods=['GET', 'POST'])
def exam():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        connection.close()
        
        if user:
            user_id = user[0]
            return render_template('exam.html', user_id=user_id)
        else:
            return render_template('index.html', error='E-posta veya şifre yanlış!')
    
    return render_template('index.html')

@app.route('/get_questions', methods=['GET'])
def get_questions():
    subject = request.args.get('subject')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Seçilen konuya göre soruları getir
    cursor.execute("""
        SELECT q.id, q.question_text 
        FROM questions q 
        WHERE q.Subject = %s
    """, (subject,))
    questions = cursor.fetchall()

    # Her soru için seçenekleri getir
    for question in questions:
        cursor.execute("""
            SELECT a.id, a.answer_text 
            FROM answers a 
            WHERE a.question_id = %s
        """, (question['id'],))
        question['answers'] = cursor.fetchall()
    
    connection.close()
    # Her sorunun text ve her cevabın text değerini doğru şekilde aktaralım
    return jsonify({
        'questions': [
            {
                'id': question['id'],
                'text': question['question_text'],
                'answers': [
                    {'id': answer['id'], 'text': answer['answer_text']}
                    for answer in question['answers']
                ]
            } for question in questions
        ]
    })


@app.route('/submit', methods=['POST'])
def submit():
    user_id = request.form['user_id']
    score = 0
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, correct_answer FROM questions")
    questions = cursor.fetchall()

    for question in questions:
        question_id = question[0]
        correct_answer = question[1]
        user_answer = request.form.get(f'question_{question_id}')
        if user_answer == correct_answer:
            score += 1

    cursor.execute("INSERT INTO results (user_id, score) VALUES (%s, %s)", (user_id, score))
    cursor.execute("UPDATE users SET highscore = LEAST(highscore, %s) WHERE id = %s", (score, user_id))
    connection.commit()
    connection.close()

    return render_template('result.html', score=score)

if __name__ == '__main__':
    app.run(debug=True)
