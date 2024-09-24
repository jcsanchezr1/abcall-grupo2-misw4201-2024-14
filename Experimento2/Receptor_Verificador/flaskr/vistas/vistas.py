from flask_restful import Resource

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
            put_url = 'http://verificador:5003/auditorias'
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