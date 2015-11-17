from flask import Flask
from flask_dropin import DropInManager


app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'

app.config['DROPINS'] = [
    'home',
    'login',
]


dropin = DropInManager(app)


if __name__ == '__main__':
    app.run(debug=True)
