from flask_restful import Resource

from ..modelos import db, Auditoria, TipoApp, AuditoriaSchema
from flask import request
import datetime

auditoria_schema = AuditoriaSchema()

class VistaAuditoria(Resource):

    def get(self):
        return [auditoria_schema.dumps(auditor) for auditor in Auditoria.query.all()]

    def post(self):
        #TODO: CONSULTAR SERVICIO DE MONITOR

        nueva_auditoria = Auditoria(id_llamada=request.json['id_llamada'],
                                    fecha_registro=datetime.datetime.now(),
                                    tipo_app=TipoApp.ACTIVO) #Check this value
        
        
        
        db.session.add(nueva_auditoria)
        db.session.commit()
        return auditoria_schema.dump(nueva_auditoria), 201
    
    """def post(self):
        nueva_cancion = Cancion(titulo=request.json['titulo'], \
                                minutos=request.json['minutos'], \
                                segundos=request.json['segundos'], \
                                interprete=request.json['interprete'])
        db.session.add(nueva_cancion)
        db.session.commit()
        return cancion_schema.dump(nueva_cancion)"""