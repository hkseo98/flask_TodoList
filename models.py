from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Todo(db.Model):
    __tablename__ = 'todo'

    id = db.Column(db.Integer, primary_key=True)
    fcuser_id = db.Column(db.Integer, db.ForeignKey('fcuser.id'), nullable=False)
    title = db.Column(db.String(256))
    status = db.Column(db.Integer)
    due = db.Column(db.String(64))
    tstamp = db.Column(db.DateTime, server_default=db.func.now())

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'fcuser': self.fcuser.userid,
            'tstamp': self.tstamp
        }


class Fcuser(db.Model):
    __tablename__ = 'fcuser'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(32))
    password = db.Column(db.String(128))
    # Todo와의 관계 지정 - Todo가 자신을 참조할 자신의 값을 그대로 가져갈 수 있게 함.
    # lazy=True - 데이터베이스에서 가지고 올 때 로드하겠다는 뜻.
    todos = db.relationship('Todo', backref='fcuser', lazy=True)
