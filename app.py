from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
import threading

import Models

# object for the Flask
app = Flask(__name__)

# configuration
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://user_1:user@127.0.0.1:1433/py_history?driver=SQL+Server'

# object for the SQLAlchemy
db = SQLAlchemy(app)


@app.route('/add_query', methods=['POST'])
def add_query():
    # добавляет запрос в историю
    try:
        data = request.get_json()
        query = data["query"]
        user = data["user"]
        new_query = Models.history_users(user, query, datetime.utcnow())
        db.session.add(new_query)
        db.session.commit()
    except TypeError:
        db.session.rollback()
    return "adding the query successfully"


@app.route('/delete_history', methods=['DELETE'])
def delete_history():
    # очищает историю запросов пользователя
    try:
        data = request.get_json()
        user = data["user"]
        del_query = db.session.query(Models.history_users).filter(
            Models.history_users.history_user == user).all()
        for i in del_query:
            db.session.delete(i)
        db.session.commit()
    except TypeError:
        db.session.rollback()
    return "deleting the history successfully"


@app.route('/get_history', methods=['GET'])
def get_history():
    # возвращает историю запросов пользователя
    data = request.get_json()
    user = data["user"]
    query = db.session.query(Models.history_users).filter(Models.history_users.history_user == user).all()
    return jsonify([item.get_date_query for item in query])


@app.route('/get_last_queries', methods=['GET'])
def get_last_queries():
    # возвращает последние N запросов пользователя
    data = request.get_json()
    user = data["user"]
    query_count = data["n"]
    query = db.session.query(Models.history_users).filter(
        Models.history_users.history_user == user).order_by(
        Models.history_users.history_in.desc()).limit(query_count).all()
    return jsonify([item.get_date_query for item in query])


def delete_query_every_hour():
    # очищает историю запросов каждый час, если число запросов превысило предел
    one_hour = 60 * 60
    threading.Timer(one_hour, delete_query_every_hour).start()  # Перезапуск функции каждый час

    query_limit = 100  # размер буффера запросов

    for user in db.session.query(Models.history_users).all():  # итерируемся по каждому пользователю
        query_count = db.session.query(Models.history_users).filter(
            Models.history_users.history_user == user.history_user).count()

        if query_count > query_limit:  # если количество запросов пользователя превышает предел
            reverse_history = db.session.query(Models.history_users).filter(
                Models.history_users.history_user == user.history_user).order_by(
                Models.history_users.history_in.desc()).all()  # выбираем все запросы в обратном порядке

            for item in range(query_limit, query_count):
                db.session.delete(reverse_history[item])
            db.session.commit()


if __name__ == '__main__':
    delete_query_every_hour()
    app.run(debug=True)
