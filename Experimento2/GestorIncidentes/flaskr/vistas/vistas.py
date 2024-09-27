from flask_restful import Resource

from flask import request, Flask, request, jsonify
from google.cloud import pubsub_v1

import json
import threading



project_id = "abcall"
topic_id = "incidente"
subscription_id = "incidente.verificador"
id=0
payload = ""

publisher_client = pubsub_v1.PublisherClient()
topic_path = publisher_client.topic_path(project_id, topic_id)
subscriber_client = pubsub_v1.SubscriberClient()
subscription_path = subscriber_client.subscription_path(project_id, subscription_id)


class VistaGestorIncidente(Resource):

   def post(self):
        try:
            self.id = request.json["id"]
            self.payload = request.json["payload"]

            PubSubSubscriber()
                        
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
            print(message)
            message_data = json.loads(message.data.decode('utf-8'))
            id_auditoria = self.id
            payload = self.payload

            new_message =  json.dumps({
                                                    'id': id_auditoria,
                                                    'payload': payload,                                                    
                                                })

            print(f"Received message: {message_data}")
            print(f"New message: {new_message}")

            future = publisher_client.publish(topic_path, new_message.encode('utf-8'))
            future.result()

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

