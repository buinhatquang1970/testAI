from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql://test_quiz_user:BiasoHIhE3vFOLUvwHRSPaNylhlODczD@'
    'dpg-d0t36qje5dus738r5170-a.oregon-postgres.render.com:5432/test_quiz'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(200), nullable=False)
    answer_a = db.Column(db.String(100), nullable=False)
    answer_b = db.Column(db.String(100), nullable=False)
    answer_c = db.Column(db.String(100), nullable=False)
    answer_d = db.Column(db.String(100), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)

class QuizResult(db.Model):
    __tablename__ = 'quiz_result'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    score = db.Column(db.Integer, nullable=False)

@app.route('/')
def index():
    questions = Question.query.all()
    return render_template('index.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    name = data.get('name')
    score = data.get('score')
    start_time_str = data.get('start_time')

    if not name or score is None or not start_time_str:
        return jsonify({'error': 'Thiếu dữ liệu'}), 400

    try:
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
    except:
        return jsonify({'error': 'Sai định dạng ngày giờ'}), 400

    result = QuizResult(name=name, score=score, start_time=start_time)
    db.session.add(result)
    db.session.commit()
    return jsonify({'message': 'Lưu kết quả thành công'})
import random
from flask import jsonify

@app.route('/api/get_questions')
def get_questions():
    questions_all = Question.query.all()
    selected = random.sample(questions_all, min(len(questions_all), 25))
    result = []
    for q in selected:
        result.append({
            'id': q.id,
            'question_text': q.question_text,
            'answer_a': q.answer_a,
            'answer_b': q.answer_b,
            'answer_c': q.answer_c,
            'answer_d': q.answer_d,
            'correct_answer': q.correct_answer
        })
    return jsonify(result)

@app.route('/admin/questions')
def admin_questions():
    questions = Question.query.order_by(Question.id.asc()).all()
    return render_template('admin_questions.html', questions=questions)

@app.route('/admin/results')
def admin_results():
    results = QuizResult.query.order_by(QuizResult.start_time.desc()).all()
    return render_template('admin.html', results=results)

@app.route('/admin/questions/add', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        question_text = request.form.get('question_text', '').strip()
        answer_a = request.form.get('answer_a', '').strip()
        answer_b = request.form.get('answer_b', '').strip()
        answer_c = request.form.get('answer_c', '').strip()
        answer_d = request.form.get('answer_d', '').strip()
        correct_answer = request.form.get('correct_answer', '').strip().upper()

        if not all([question_text, answer_a, answer_b, answer_c, answer_d, correct_answer]):
            return render_template('add_question.html', error="Vui lòng nhập đầy đủ thông tin!")

        if correct_answer not in ['A', 'B', 'C', 'D']:
            return render_template('add_question.html', error="Đáp án đúng phải là A, B, C hoặc D.")

        try:
            new_q = Question(
                question_text=question_text,
                answer_a=answer_a,
                answer_b=answer_b,
                answer_c=answer_c,
                answer_d=answer_d,
                correct_answer=correct_answer
            )
            db.session.add(new_q)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return render_template('add_question.html', error=f"Lỗi khi lưu câu hỏi: {str(e)}")

        return redirect(url_for('admin_questions'))

    return render_template('add_question.html')

@app.route('/admin/questions/edit/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        question_text = request.form.get('question_text', '').strip()
        answer_a = request.form.get('answer_a', '').strip()
        answer_b = request.form.get('answer_b', '').strip()
        answer_c = request.form.get('answer_c', '').strip()
        answer_d = request.form.get('answer_d', '').strip()
        correct_answer = request.form.get('correct_answer', '').strip().upper()

        if not all([question_text, answer_a, answer_b, answer_c, answer_d, correct_answer]):
            return render_template('edit_question.html', question=question, error="Vui lòng nhập đầy đủ thông tin!")

        if correct_answer not in ['A', 'B', 'C', 'D']:
            return render_template('edit_question.html', question=question, error="Đáp án đúng phải là A, B, C hoặc D.")

        try:
            question.question_text = question_text
            question.answer_a = answer_a
            question.answer_b = answer_b
            question.answer_c = answer_c
            question.answer_d = answer_d
            question.correct_answer = correct_answer

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return render_template('edit_question.html', question=question, error=f"Lỗi khi cập nhật câu hỏi: {str(e)}")

        return redirect(url_for('admin_questions'))

    return render_template('edit_question.html', question=question)

@app.route('/admin/questions/delete/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    try:
        db.session.delete(question)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    return redirect(url_for('admin_questions'))

if __name__ == '__main__':
    app.run(debug=True)
