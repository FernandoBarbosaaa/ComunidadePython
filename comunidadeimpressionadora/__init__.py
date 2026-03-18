import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Pasta do pacote (onde estão static/ e templates/)
pasta_pacote = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,
            static_folder=os.path.join(pasta_pacote, 'static'),
            template_folder=os.path.join(pasta_pacote, 'templates'))


app.config['SECRET_KEY'] = 'ae9f09640c0a2789b02ac3b49f54729c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comunudade.db'

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Faça login para acessar esta página.'
login_manager.login_message_category = 'alert-primary'

from comunidadeimpressionadora import routes