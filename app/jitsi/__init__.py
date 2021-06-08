import eventlet
import os
from jitsi import testfactory as tf
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS
from config import config, basedir
from flask_mail import Mail
import logging

logging.basicConfig(filename="flask.log", level=logging.DEBUG)
logger = logging.getLogger(__name__)

eventlet.monkey_patch(socket=True)

staticdir = os.path.join(basedir, 'client/js')

db = SQLAlchemy()
socketio = SocketIO()
mail = Mail()
testf = tf.TestFactory()

# Register socket events with SocketIO instance
from . import events  # noqa


def create_app(config_name):
    '''
    Factory function that returns the created application instance
    '''
    app = Flask(__name__, static_folder=staticdir)
    app_config = config[config_name]()
    app.config.from_object(app_config)
    app_config.init_app(app)

    from jitsi import main

    # Endpoints
    app.register_blueprint(main.main)

    # Enable cross-origin requests
    CORS(app)

    # Database
    db.init_app(app)

    # Email
    mail.init_app(app)

    # SocketIO
    queue = app_config.MESSAGE_QUEUE
    socketio.init_app(app, cors_allowed_origins='*', message_queue=queue)

    # S3
    logger.info("initializing fac")
    testf.init_app(app)
    logger.info("factory initialized")

    return app


def run_eventlet(app):
    socketio.init_app(app, async_mode="eventlet")
    socketio.run(app, host='0.0.0.0', port=os.getenv('FLASK_RUN_PORT'))
