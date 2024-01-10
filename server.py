from flask import Flask, render_template, url_for, redirect, request, jsonify, send_file
from docx import Document
from docx.shared import Pt, Inches
import uuid
import json
import os
import math
import io
import base64

app = Flask(__name__)
@app.route('/admin')
def mentor_login():
    return render_template('user.html')

@app.route('/dashboard/<mentor_uuid>')
def mentor_dashboard(mentor_uuid):
    return render_template('dashboard.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    with open('./assets/mentor_ids.json', 'r') as f:
        ids = json.load(f)

    if data['nickname'] not in list(ids['id_password'].keys()) or data["password"] != ids["id_password"][data["nickname"]]:
        return jsonify({"message": "비밀번호가 틀렸습니다"})

    else:
        return redirect(url_for('mentor_dashboard', mentor_uuid=ids["id_uuid"][data["nickname"]]))

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    with open('./assets/mentor_ids.json', 'r') as f:
        ids = json.load(f)

    if data['nickname'] == "":
        return jsonify({"message" : "이름을 입력해주세요"})

    if data['nickname'] in list(ids['id_password'].keys()):
        return jsonify({"message": "이미 등록된 이름입니다"})

    if data['password'] != data['passwordCheck']:
        return jsonify({"message": "두 비밀번호가 다릅니다"})

    #JSON에 멘토명-비밀번호 등록
    ids["id_password"][data["nickname"]] = data["password"]
    temp_uuid = str(uuid.uuid4())[:8]
    ids["id_uuid"][data["nickname"]] = temp_uuid
    ids["uuid_id"][temp_uuid] = data["nickname"]
    with open('./assets/mentor_ids.json', 'w') as f:
        json.dump(ids, f)
    #멘토명 폴더 생성
    os.mkdir(os.path.join('./assets', temp_uuid))
    with open(os.path.join('./assets', temp_uuid, 'school_ids.json'), 'w') as f:
        json.dump({"school_uuid" : {}, "uuid_school" : {}}, f)
    return jsonify({"message" : "성공적으로 등록되었습니다"})

@app.route('/school/<mentor_uuid>', methods=['POST', 'GET'])
def add_school_and_student(mentor_uuid):
    if request.method == 'POST':
        data = request.form
        with open('./assets/mentor_ids.json', 'r') as f:
            ids = json.load(f)
        school_dir = os.path.join('assets', mentor_uuid, data["school-name"] + ' ' + data["field"])
        os.mkdir(school_dir)
        students = []
        for i in range(1, ((len(data) - 2) // 2) + 1):
            students.append({data["student-number-" + str(i)] : data["student-name-" + str(i)]})
        metadata = {
            "school_name" : data["school-name"],
            "field" : data["field"],
            "students" : students,
            "class_info" : {},
            "attendance" : {},
            "class_screenshot" : {}
        }
        with open(os.path.join(school_dir, "metadata.json"), 'w') as f:
            json.dump(metadata, f)
        with open(os.path.join('assets', mentor_uuid, 'school_ids.json'), 'r') as f:
            school_ids = json.load(f)
        cur_school_id = str(uuid.uuid4())[:8]
        school_ids["school_uuid"][data["school-name"] + ' ' + data['field']] = cur_school_id
        school_ids["uuid_school"][cur_school_id] = data["school-name"] + ' ' + data['field']
        with open(os.path.join('assets', mentor_uuid, 'school_ids.json'), 'w') as f:
            json.dump(school_ids, f)
        return "YAAY"

    elif request.method == 'GET':
        res = os.listdir(os.path.join('./assets', mentor_uuid))
        res.remove('school_ids.json')
        return res

@app.route('/students/<mentor_uuid>', methods=["POST"])
def get_students(mentor_uuid):
    data = request.json
    school_name = data["school_name"]
    with open(os.path.join('assets', mentor_uuid, school_name, 'metadata.json'), 'r') as f:
        school_info = json.load(f)
    students = school_info["students"]
    return students

@app.route('/metadata/<mentor_uuid>', methods=['POST'])
def get_class_metadata(mentor_uuid):
    data = request.form
    print(data)
    school_dir = os.path.join('assets', mentor_uuid, data['schoolName'], 'metadata.json')
    with open(school_dir, 'r') as f:
        school_metadata = json.load(f)
    school_metadata['class_info'] = data
    with open(school_dir, 'w') as f:
        json.dump(school_metadata, f)
    return jsonify({"message" : "Success"})

@app.route('/attendance/<mentor_uuid>', methods=['POST'])
def get_attendance(mentor_uuid):
    data = request.form
    print(data)
    school_dir = os.path.join('assets', mentor_uuid, data['schoolName'], 'metadata.json')
    with open(school_dir, 'r') as f:
        school_metadata = json.load(f)
    school_metadata['attendance'] = data
    with open(school_dir, 'w') as f:
        json.dump(school_metadata, f)
    return jsonify({"message" : "Success"})

@app.route('/classdata/<mentor_uuid>', methods=['POST'])
def get_class_data(mentor_uuid):
    data = request.json
    with open(os.path.join('assets', mentor_uuid, data['school_name'], 'metadata.json'), 'r') as f:
        metadata = json.load(f)
    return jsonify(metadata)

@app.route('/screenshots/<mentor_uuid>', methods=['POST'])
def get_screenshots(mentor_uuid):
    data = request.json
    print(data)
    school_dir = os.path.join('assets', mentor_uuid, data['school_name'], 'metadata.json')
    with open(school_dir, 'r') as f:
        metadata = json.load(f)
    data.pop('school_name')
    metadata['class_screenshot'] = data
    with open(school_dir, 'w') as f:
        json.dump(metadata, f)
    return jsonify({"message" : "Success"})

@app.route('/export/<mentor_uuid>', methods=['POST'])
def get_class_report(mentor_uuid):
    data = request.form
    for file in os.listdir(os.path.join('assets', mentor_uuid, data['school_name'])):
        if '.docx' in file:
            os.remove(os.path.join('assets', mentor_uuid, data['school_name'], file))
    school_dir = os.path.join('assets', mentor_uuid, data['school_name'], 'metadata.json')
    with open(school_dir, 'r') as f:
        metadata = json.load(f)
    doc = Document('ClassReport_Empty.docx')
    doc.tables[0].rows[0].cells[2].paragraphs[0].text = ''
    run = doc.tables[0].rows[0].cells[2].paragraphs[0].add_run(metadata['school_name'])
    run.font.size = Pt(12)
    doc.tables[0].rows[1].cells[2].paragraphs[0].text = ''
    run = doc.tables[0].rows[1].cells[2].paragraphs[0].add_run('  ' + metadata['field'] + ' ' + metadata['class_info']['className'])
    run.font.size = Pt(12)
    doc.tables[0].rows[2].cells[2].paragraphs[0].text = ''
    run = doc.tables[0].rows[2].cells[2].paragraphs[0].add_run(metadata['class_info']['mentorName'])
    run.font.size = Pt(12)
    for i in range(1, 7):
        doc.tables[1].rows[i].cells[1].paragraphs[0].text = metadata['class_info']['classOverview' + str(i)].replace('\r\n', '\n')
        doc.tables[1].rows[i].cells[2].paragraphs[0].text = metadata['class_info']['classDetails' + str(i)].replace('\r\n', '\n')
    doc.tables[1].rows[7].cells[1].paragraphs[0].text = metadata['class_info']['classOverviewOffline'].replace('\r\n', '\n')
    doc.tables[1].rows[7].cells[2].paragraphs[0].text = metadata['class_info']['classDetailsOffline'].replace('\r\n', '\n')

    doc.tables[2].rows[1].cells[1].paragraphs[0].text = metadata['class_info']['teamTopic'].replace('\r\n', '\n')
    doc.tables[2].rows[2].cells[1].paragraphs[0].text = metadata['class_info']['individualInterest'].replace('\r\n', '\n')

    cur_row = 2
    for student in metadata['students']:
        print('-' * 50)
        student_number = list(student.keys())[0]
        student_name = student[student_number]
        doc.tables[3].rows[cur_row].cells[0].paragraphs[0].text = student_number
        doc.tables[3].rows[cur_row].cells[1].paragraphs[0].text = student_name
        print(student_number, student_name)
        for key in metadata['attendance'].keys():
            status_str = ""
            if 'attendance-' + student_number in key:
                print(key)
                col_num = int(key.split('-')[-1])
                status_str = metadata['attendance'][key]

                if status_str == '결석' or status_str == '지각':
                    status_str += '\n(' + metadata['attendance']['reason-' + student_number + '-' + str(col_num)] + ')'
                print(status_str, cur_row, col_num)
                doc.tables[3].rows[cur_row].cells[col_num + 1].paragraphs[0].text = status_str
            elif 'time-' in key:
                col_num = int(key.split('-')[-1])
                doc.tables[3].rows[1].cells[col_num + 1].paragraphs[0].text = ''
                run = doc.tables[3].rows[1].cells[col_num + 1].paragraphs[0].add_run(metadata['attendance'][key].replace('\r\n', '\n'))
                run.font.size = Pt(9)
        cur_row += 1

    for k, v in metadata['class_screenshot'].items():
        binary = base64.b64decode(v.split(',')[1])
        run = doc.tables[3 + math.ceil(int(k) / 2)].rows[1].cells[(int(k) + 1) % 2].paragraphs[0].add_run()
        run.add_picture(io.BytesIO(binary), width=Inches(3))

    final_dir = os.path.join('assets', mentor_uuid, data['school_name'], data['file_name'] + '.docx')
    doc.save(final_dir)
    return send_file(final_dir, download_name=data['file_name'] + '.docx', as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=False)