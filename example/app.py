from flask import Flask
from flask_dropin import DropInManager

dropin = DropInManager()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'
    app.config['DROPINS'] = ['home', 'auth']
    app.config['DROPS_LOADERS'] = ['flask_dropin:BlueprintsLoader', 'flask_dropin.nameddrops:NamedServicesLoader']
    app.config['DROPIN_BLUEPRINTS_TRANSFORM'] = {'/web': ''}
    dropin.init_app(app)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
