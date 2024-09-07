from flask import request, Flask, jsonify
from google.cloud import pubsub_v1

import datetime
import json
import requests
import threading


with open('http-client.env.json') as config_file:
    config = json.load(config_file)['local']

project_id = config['id-proyecto']
topic_id = "replies"
subscription_id = "message.gestor-llamadas-principal"

publisher_client = pubsub_v1.PublisherClient()
topic_path = publisher_client.topic_path(project_id, topic_id)
subscriber_client = pubsub_v1.SubscriberClient()
subscription_path = subscriber_client.subscription_path(project_id, subscription_id)

app = Flask(__name__)

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
            new_message = {
                'message': json.dumps({
                    'id_auditoria': message_data.auditoria_id,
                    'id_llamada': message_data.id_llamada,
                    'componente': "Principal"
                })
            }
            message_data["componente"] = "Principal"
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


# Instancia del suscriptor (esto inicia la escucha de mensajes en segundo plano)
subscriber = PubSubSubscriber()

# Ruta de prueba en Flask
@app.route('/')
def home():
    return jsonify({"message": "Servidor en ejecución correctamente"})

if __name__ == '__main__':
    app.run(port=5002, debug=True)
