from flask import Flask, render_template, url_for, redirect, request, jsonify
import uuid
import json
import os

app = Flask(__name__)
@app.route('/admin')
def mentor_login():
    return render_template('user.html')

@app.route('/dashboard')
def mentor_dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['POST'])
def login():
    return redirect(url_for('mentor_dashboard'))

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    with open('./assets/mentor_ids.json', 'r') as f:
        ids = json.load(f)

    if data["nickname"] not in ids:
        #JSON에 멘토명-비밀번호 등록
        ids[data["nickname"]] = data["password"]
        with open('./assets/mentor_ids.json', 'w') as f:
            json.dump(ids, f)
        #멘토명 폴더 생성
        os.mkdir(os.path.join('./assets', data['nickname']))
        return jsonify({"message" : "Success"})

    elif data["password"] != ids[data["nickname"]]:
        return jsonify({"message" : "Wrong Password"})

    else:
        return jsonify({"message" : "Success"})



app.run(host='0.0.0.0', port=5002)