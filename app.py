from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
from threading import Timer

import Models
from config import TIME_OUT,QUERY_LIMIT

# object for the Flask
app = Flask(__name__)

# configuration
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://user_1:user@127.0.0.1:1433/py_history?driver=SQL+Server'

# object for the SQLAlchemy
db = SQLAlchemy(app)


@app.route('/add_query/<user>', methods=['POST'])
def add_query(user):
    # добавляет запрос в историю
    # post /add_query/123 HTTP/1.1
    # Content - type: text/plain
    # Content - length:7
    # здесь пустая строка
    # query 0

    try:
        data_query = request.get_data().decode('utf-8')
        new_query = Models.users_history(user, data_query, datetime.utcnow())
        db.session.add(new_query)
        db.session.commit()
    except TypeError:
        db.session.rollback()
    return "adding the query successfully"


@app.route('/delete_history/<user>', methods=['DELETE'])
def delete_history(user):
    # очищает историю запросов пользователя
    try:
        del_query = db.session.query(Models.users_history).filter(
            Models.users_history.history_user == user).all()
        for i in del_query:
            db.session.delete(i)
        db.session.commit()
    except TypeError:
        db.session.rollback()
    return "deleting the history successfully"


@app.route('/get_history/<user>', methods=['GET'])
def get_history(user):
    # возвращает историю запросов пользователя
    get_query = db.session.query(Models.users_history).filter(Models.users_history.history_user == user).all()
    return jsonify([item.get_date_query for item in get_query])


@app.route('/get_last_queries/<user>/<query_count>', methods=['GET'])
def get_last_queries(user, query_count):
    # возвращает последние N запросов пользователя
    get_query = db.session.query(Models.users_history).filter(
        Models.users_history.history_user == user).order_by(
        Models.users_history.history_id.desc()).limit(query_count).all()
    return jsonify([item.get_date_query for item in get_query])


def delete_query_every_hour():
    # очищает историю запросов каждый час, если число запросов превысило предел
    # threading.Timer(TIME_OUT, delete_query_every_hour).start()  # Перезапуск функции каждый час
    for user in db.session.query(Models.users_history).all():  # итерируемся по каждому пользователю
        query_count = db.session.query(Models.users_history).filter(
            Models.users_history.history_user == user.history_user).count()

        if query_count > QUERY_LIMIT:  # если количество запросов пользователя превышает предел
            reverse_history = db.session.query(Models.users_history).filter(
                Models.users_history.history_user == user.history_user).order_by(
                Models.users_history.history_id.desc()).all()  # выбираем все запросы в обратном порядке

            for item in range(QUERY_LIMIT, query_count):
                db.session.delete(reverse_history[item])
            db.session.commit()

if __name__ == '__main__':
    Timer(TIME_OUT, delete_query_every_hour).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
