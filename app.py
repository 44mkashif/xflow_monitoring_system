from flask import Flask, render_template, request, redirect

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/core_router')
def router():
    return render_template('core_router.html')

@app.route('/core_switch1')
def core_switch1():
    return render_template('core_switch1.html')

@app.route('/core_switch2')
def core_switch2():
    return render_template('core_switch2.html')

@app.route('/access_switch1')
def access_switch1():
    return render_template('access_switch1.html')

@app.route('/access_switch2')
def access_switch2():
    return render_template('access_switch2.html')

if __name__ == "__main__":
    app.run(debug=True, host='172.30.211.14')
