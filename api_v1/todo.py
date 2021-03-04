from flask import jsonify
from flask import request, session
from flask import Blueprint
import requests
from . import api
from models import Todo, db, Fcuser
import datetime


def send_slack(msg):
    # 할일 생성 시 알려주는 코드 들어가는 자리.
    res = requests.post('https://hooks.slack.com/services/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', json={
        'text': msg
    }, headers={'Content-Type': 'application/json'})



@api.route('/todos/done', methods=['PUT'])
def todos_done():
    userid = session.get('userid', None)
    if not userid:
        return jsonify(), 401
    data = request.get_json()
    todo_id = data.get('todo_id')
    todo = Todo.query.filter_by(id=todo_id).first()
    fcuser = Fcuser.query.filter_by(userid=userid).first()
    if todo.fcuser_id != fcuser.id:
        return jsonify(), 400
    todo.status = 1
    db.session.commit()
    send_slack('TODO가 완료되었습니다\n사용자: %s\n할일 제목: %s' %(fcuser.userid, todo.title))

    return jsonify()


@api.route('/todos/delete', methods=['DELETE'])
def todos_del():
    userid = session.get('userid', None)
    if not userid:
        return jsonify(), 401
    data = request.get_json()
    todo_id = data.get('todo_id')
    todo = Todo.query.filter_by(id=todo_id).first()
    fcuser = Fcuser.query.filter_by(userid=userid).first()
    if todo.fcuser_id != fcuser.id:
        return jsonify(), 400
    db.session.delete(todo)
    db.session.commit()
    return jsonify(), 203


@api.route('/todos', methods=['GET', 'POST', 'DELETE'])
def todos():
    userid = session.get('userid', None)
    if not userid:
        return jsonify(), 401

    if request.method == 'POST':
        data = request.get_json()
        todo = Todo()
        todo.title = data.get('title')
        fcuser = Fcuser.query.filter_by(userid=userid).first()
        todo.fcuser_id = fcuser.id
        todo.due = data.get('due')
        todo.status = 0
        db.session.add(todo)
        db.session.commit()
        send_slack('TODO가 생성되었습니다\n사용자: %s\n할일 제목: %s\n기한: %s'%(fcuser.userid, todo.title, todo.due))
        return jsonify(), 201

    elif request.method == 'GET':
        todos = Todo.query.filter_by(fcuser_id=userid)

        return jsonify([t.serialize for t in todos])

    elif request.method == 'DELETE':
        data = request.get_json()
        todo_id = data.get('todo_id')
        todo = Todo.query.filter_by(id=todo_id).first()
        db.session.delete(todo)
        db.session.commit()
        return jsonify(), 203

    return jsonify(data)


@api.route('/slack/todos', methods=['POST'])
def slack_todos():
    res = request.form['text'].split(' ')
    cmd, *args = res
    ret_msg = ''
    if cmd == 'create':
        todo_user_id = args[0]
        todo_name = args[1]
        todo_due = args[2]

        fcuser = Fcuser.query.filter_by(userid=todo_user_id).first()

        todo = Todo()
        todo.fcuser_id = fcuser.id
        todo.title = todo_name
        todo.due = todo_due
        todo.status = 0

        db.session.add(todo)
        db.session.commit()
        ret_msg = 'Todo가 생성되었습니다'

        send_slack('[%s] "%s" 할 일을 만들었습니다.'%(str(datetime.datetime.now()), todo_name))  # 사용자 정보, 할일 제목, 기한.
    elif cmd == 'list':
        todo_user_id = args[0]
        fcuser = Fcuser.query.filter_by(userid=todo_user_id).first()
        todos = Todo.query.filter_by(fcuser_id=fcuser.id)
        for todo in todos: # 인덱스 번호와 값을 묶어서 튜플 형태로 반환해줌.
            ret_msg += '%d. "%s (~ %s, %s)\n'%(todo.id, todo.title, todo.due, ('미완료', '완료')[todo.status])

    elif cmd == 'done':
        todo_id = args[0]
        todo = Todo.query.filter_by(id=todo_id).first()
        todo.status = 1
        db.session.commit()
        ret_msg = 'Todo가 완료 처리되었습니다.'

    elif cmd == 'undo':
        todo_id = args[0]
        todo = Todo.query.filter_by(id=todo_id).first()
        todo.status = 0
        db.session.commit()
        ret_msg = 'Todo가 미완료 처리되었습니다.'




    return ret_msg
