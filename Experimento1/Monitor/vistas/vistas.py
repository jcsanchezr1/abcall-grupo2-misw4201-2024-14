from flask_restful import Resource
from ..modelos import db, HealthCheck, HealthCheckSchema
from sqlalchemy import desc

healhtcheck_schema = HealthCheckSchema()

class VistaHealthChecks( Resource ):

    def get(self):

        ultimo_principal = HealthCheck.query.filter_by(component = 'Principal').order_by( desc( HealthCheck.timestamp ) ).first()
        ultimo_redundante = HealthCheck.query.filter_by(component = 'Redundante').order_by( desc( HealthCheck.timestamp ) ).first()

        response = {
            'principal': healhtcheck_schema.dump(ultimo_principal),
            'redundante': healhtcheck_schema.dump(ultimo_redundante)
        }

        return response