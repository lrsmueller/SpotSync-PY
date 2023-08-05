import logging

from flask import Flask
from flask_session import Session
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import Config
from app.db import db
from app.worker import refresh_all_playlists

def create_app(config_class=Config):
    logging.basicConfig()
    
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)
    Session(app)
    sched = BackgroundScheduler(daemon=True) # Background Refresh Task
    
    # Adding Loggers
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)
    logging.getLogger('app.worker').setLevel(logging.DEBUG) 
    logging.getLogger('DBCacheHandler').setLevel(logging.DEBUG)
    
    app.logger.info("start3 " + Config.SQLALCHEMY_DATABASE_URI)
    
    with app.app_context():
        db.create_all() # Create DB #TODO only if it doesnt exsist
        
        # Schedule Refresh Jobs
        sched.add_job(refresh_all_playlists,trigger='cron', hour=Config.CRON_HOUR, minute=Config.CRON_MINUTE) #TODO config
        sched.start() 
        
        # Register blueprints
        from app.routes import bp as main_bp
        app.register_blueprint(main_bp)

        return app