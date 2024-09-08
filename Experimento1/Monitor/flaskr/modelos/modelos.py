from datetime import datetime
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_sqlalchemy import SQLAlchemy
import pytz

db = SQLAlchemy()

class HealthCheck( db.Model ):
    __tablename__ = 'healthchecks'
    id = db.Column( db.Integer, primary_key = True )
    status = db.Column( db.String( 50 ), nullable = False )
    component = db.Column( db.String( 50 ), nullable = False )
    timestamp = db.Column( db.DateTime, default = lambda: datetime.now( pytz.timezone('America/Bogota') ) )

    def __init__(self, status, component):
        self.status = status
        self.component = component

class HealthCheckSchema( SQLAlchemyAutoSchema ):
    class Meta:
        model = HealthCheck
        load_instance = True