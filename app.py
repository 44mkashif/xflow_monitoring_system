from flask import Flask, render_template, request, redirect

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('core_router.html')

if __name__ == "__main__":
    app.run(debug=True, host='172.30.211.14')
