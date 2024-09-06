from flask_restful import Resource

from ..modelos import db, Auditoria, TipoApp, AuditoriaSchema
from flask import request, Flask, request, jsonify
from google.cloud import pubsub_v1

import datetime
import json
import requests
import threading

auditoria_schema = AuditoriaSchema()

with open('http-client.env.json') as config_file:
    config = json.load(config_file)['local']

project_id = config['id-proyecto']
topic_id = "message"
subscription_id = "replies.receptor"

publisher_client = pubsub_v1.PublisherClient()
topic_path = publisher_client.topic_path(project_id, topic_id)
subscriber_client = pubsub_v1.SubscriberClient()
subscription_path = subscriber_client.subscription_path(project_id, subscription_id)


class VistaAuditoria(Resource):
    def __init__(self):
        self.vista_topicos = VistaTopicos()  # Crear instancia de VistaTopicos

    def get(self):
        return [auditoria_schema.dumps(auditor) for auditor in Auditoria.query.all()]

    def post(self):
        #TODO: CONSULTAR SERVICIO DE MONITOR

        id_llamada = request.json['id_llamada']
        fecha_registro = datetime.datetime.now()
        tipo_app = TipoApp.Principal  # Check this value
        try:            
            nueva_auditoria = Auditoria(id_llamada=id_llamada,
                                        fecha_registro=fecha_registro,
                                        tipo_app=tipo_app)
            db.session.add(nueva_auditoria)
            db.session.commit()

            # Obtener el ID de la nueva auditoría
            auditoria_id = nueva_auditoria.id

            # Llamar al método post de VistaTopicos
            topicos_url = 'http://localhost:5001/publish'
            message = {
                'message': json.dumps({
                    'id_auditoria': auditoria_id,
                    'id_llamada': id_llamada,
                    'fecha_registro': fecha_registro.isoformat()
                })
            }
            response = requests.post(topicos_url, json=message)

            if response.status_code != 200:
                return {'error': 'Failed to publish message to topics'}, 500

            data = response.json()  # Si la respuesta es un JSON
            print("Respuesta JSON:", data)
            return auditoria_schema.dump(nueva_auditoria), 201
        except Exception as e:
            return {'error': f'Ocurrió un error: {str(e)}'}, 500

class VistaTopicos(Resource):

    def post(self):
        message = request.json.get('message', '')
        if not message:
            return {'error': 'Message is required'}, 400
        try:
            future = publisher_client.publish(topic_path, message.encode('utf-8'))
            message_id = future.result()
            return {'message_id': message_id}, 200
        except Exception as e:
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
        print("Callback ejecutado")
        try:
            print(f"Received message: {message.data.decode('utf-8')}")
            # Aquí puedes agregar la lógica para procesar el mensaje
            message.ack()  # Reconocer (acknowledge) el mensaje una vez procesado
        except Exception as e:
            print(f"Error processing message: {e}")

    def start_listening(self):
        """
        Método para iniciar la escucha continua de nuevos mensajes.
        """
        print("Iniciando escucha de nuevos mensajes...")
        # Configurar el suscriptor para escuchar nuevos mensajes de forma indefinida
        future = subscriber_client.subscribe(subscription_path, self.callback)

        # Mantener el suscriptor en ejecución sin bloquear el hilo principal
        try:
            future.result()
        except Exception as e:
            print(f"Listening interrupted: {e}")


# Instancia del suscriptor (esto inicia la escucha de mensajes en segundo plano)
subscriber = PubSubSubscriber()

# Asegúrate de que el resto de la aplicación continúe funcionando