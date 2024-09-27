from flask_restful import Resource, reqparse

from ..modelos import db, Auditoria, AuditoriaSchema,EstadoVerificacion, TipoEstadoEstadoAuditoria
from flask import request, Flask, request, jsonify
from google.cloud import pubsub_v1

import datetime
import json
import requests
import threading
import hashlib

auditoria_schema = AuditoriaSchema()

project_id = "abcall"
topic_id = "incidente"
subscription_id = "incidente.verificador"

publisher_client = pubsub_v1.PublisherClient()
topic_path = publisher_client.topic_path(project_id, topic_id)
subscriber_client = pubsub_v1.SubscriberClient()
subscription_path = subscriber_client.subscription_path(project_id, subscription_id)


class VistaAuditoria(Resource):

   def put(self):
        try:
            id = request.json["id"]
            payload = request.json["payload"]

            checksum = hashlib.sha256(payload.encode('utf-8')).hexdigest()
            print("Checksum del payload:", checksum)

            if not id or not payload:
                print("Faltan datos en el mensaje.")
                message.nack()
                return

            auditoria = Auditoria.query.get(id)
            print(auditoria)
            if not auditoria:
                print(f"Auditoría con id {id} no encontrada.")
                message.nack()
                return

            if auditoria.checksum1 == checksum:
                auditoria.estado_verificacion = EstadoVerificacion.NoModified
                print(f"Auditoría {id} completado pero auditoria NoModified.")
            else:
                auditoria.estado_verificacion = EstadoVerificacion.Modified
                print(f"Auditoría {id} completado auditoria Modified.")

            auditoria.checksum2 = checksum
            auditoria.fecha_finalizacion = datetime.datetime.now()
            auditoria.estado_auditoria = TipoEstadoEstadoAuditoria.Completed
            auditoria.payload2 = payload
            db.session.commit()

            return "", 200
        except Exception as e:
            print(e)
            return {'error': f'Ocurrió un error: {str(e)}'}, 500

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

        gestor_incidentes_url = "http://gestor-incidentes/api/incidentes"

        try: 
            respuesta = requests.post(gestor_incidentes_url, json=auditoria_enviada)

            if respuesta.status_code == 200 or respuesta.status_code == 201:
                return {"message": "Auditoría registrada y enviada correctamente"}, 201
            else:
                return {"message": "Error al enviar auditoría a GestorIncidentes'",
                        "status_code": respuesta.status_code}, respuesta.status_code

        except requests.exceptions.RequestException as e:
            return {"message": "Fallo al conectar con GestorIncidentes", "error": str(e)}, 500
# Clase separada para manejar la suscripción y la escucha continua de mensajes en segundo plano
class PubSubSubscriber:
    def __init__(self):
        # Iniciar el proceso de escucha de mensajes en un hilo separado
        print("Iniciando PubSubSubscriber en un hilo separado...")
        self.thread = threading.Thread(target=self.start_listening)
        self.thread.daemon = True  # Esto asegura que el hilo se cierre cuando el programa principal termine
        self.thread.start()  # Iniciar el hilo

    def callback(self, message):
        """
        Método que se invoca cuando llega un nuevo mensaje.
        """
        try:
            # Usar el contexto de aplicación para acceder a la base de datos

            message_data = json.loads(message.data.decode('utf-8'))
            put_url = 'http://localhost:5003/auditorias'
            response = requests.put(put_url, json=message_data)

            if response.status_code == 200:
                print("PUT request successful.")
            else:
                print(f"PUT request failed with status code {response.status_code}: {response.text}")
                message.nack()
                return

            # Reconocer (acknowledge) el mensaje una vez procesado
            message.ack()
        except Exception as e:
            print(f"Error processing message: {e}")
            message.nack()

    def start_listening(self):
        """
        Método para iniciar la escucha continua de nuevos mensajes.
        """
        print("Iniciando escucha de nuevos mensajes...")
        # Configurar el suscriptor para escuchar nuevos mensajes de forma indefinida
        try:
            future = subscriber_client.subscribe(subscription_path, self.callback)
            # Mantener el suscriptor en ejecución sin bloquear el hilo principal
            future.result()
        except Exception as e:
            print(f"Listening interrupted: {e}")

# Instancia del suscriptor (esto inicia la escucha de mensajes en segundo plano)
subscriber = PubSubSubscriber()
