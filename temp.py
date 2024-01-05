from flask import Flask, render_template

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('main.html')

app.run(port=5002, host='0.0.0.0')