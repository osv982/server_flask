from datetime import datetime
from app import db


class history_users(db.Model):
    __tablename__ = 'query_history'
    history_user = db.Column(db.Integer, unique=False, nullable=False)
    history_query = db.Column(db.String(max), unique=False, nullable=False)
    history_date = db.Column(db.DateTime, primary_key=True, nullable=False, default=datetime.utcnow)

    def __init__(self, history_user, history_query, history_date=datetime.utcnow):
        self.history_user = history_user
        self.history_query = history_query
        self.history_date = history_date

    @property
    def get_date_query(self):
        history_query = self.history_query
        history_date = self.history_date
        return {"query": history_query, "date": history_date}

    def represent(self):
        history_user = self.history_user
        return history_user
