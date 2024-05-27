from flask import Flask

app = Flask(__name__)

@app.route('/')
def flask_app():
    return 'Deploying Flask APP!'

if __name__ == "__main__":
    app.run()



