from flask import Flask, send_file

app = Flask(__name__)


@app.route("/")
def index():
    return send_file("static/partials/index.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0')
