import datetime
import hashlib

import requests
from flask_restful import Resource, reqparse

from ..modelos import db, Auditoria, TipoEstadoEstadoAuditoria


class VistaReceptor(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('payload', type=str, required=True, help="El payload es obligatorio")
        args = parser.parse_args()

        payload = args['payload']
        checksum = hashlib.sha256(payload.encode('utf-8')).hexdigest()

        nueva_auditoria = Auditoria()

        nueva_auditoria.fecha_registro = datetime.datetime.now()
        nueva_auditoria.checksum1 = checksum
        nueva_auditoria.payload = payload
        nueva_auditoria.estado_auditoria = TipoEstadoEstadoAuditoria.Registered

        db.session.add(nueva_auditoria)
        db.session.commit()

        auditoria_id = nueva_auditoria.id

        auditoria_enviada = {
            "id": auditoria_id,
            "payload": payload
        }

        gestor_incidentes_url = "http://incidente:5001/incidente"

        try:
            respuesta = requests.post(gestor_incidentes_url, json=auditoria_enviada)

            if respuesta.status_code == 200 or respuesta.status_code == 201:
                return {"message": "Auditoría registrada y enviada correctamente"}, 201
            else:
                return {"message": "Error al enviar auditoría a GestorIncidentes'",
                        "status_code": respuesta.status_code}, respuesta.status_code

        except requests.exceptions.RequestException as e:
            return {"message": "Fallo al conectar con GestorIncidentes", "error": str(e)}, 500
