from flask import Flask
from api_v1 import api as api_v1
import os
from models import db, Fcuser, Todo
from flask import request, redirect, render_template, session
from forms import RegisterForm, LoginForm


app = Flask(__name__)
app.register_blueprint(api_v1, url_prefix='/api/v1')


@app.route('/', methods=['GET'])
def home():
    userid = session.get('userid', None)
    todos = []
    if userid:
        fcuser = Fcuser.query.filter_by(userid=userid).first()
        todos = Todo.query.filter_by(fcuser_id=fcuser.id)
    return render_template('home.html', userid=userid, todos=todos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['userid'] = form.data.get('userid')
        return redirect('/')
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('userid', None)
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        fcuser = Fcuser()
        fcuser.userid = form.data.get('userid')
        fcuser.password = form.data.get('password')

        db.session.add(fcuser)
        db.session.commit() # commit()은 모든 변경, 추가 이력을 반영한다.
        return redirect('/login')

    return render_template('register.html', form=form) # 앞에서 만든 form을 템플릿으로 전달.



basdir = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(basdir, 'db.sqlite')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'skfjdcksjdmnclksdmlvjnsdk'

db.init_app(app)
db.app = app
db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)