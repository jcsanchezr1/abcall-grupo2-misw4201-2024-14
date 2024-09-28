import json
import random

from flask import request
from flask_restful import Resource
from google.cloud import pubsub_v1

project_id = "abcall"
topic_id = "incidente"

publisher_client = pubsub_v1.PublisherClient()
topic_path = publisher_client.topic_path(project_id, topic_id)
subscriber_client = pubsub_v1.SubscriberClient()


class VistaGestorIncidente(Resource):

    def retornar_modifcacion_aleatorio(self):
        return random.choice([True, False])

    def post(self):
        try:
            print("Creando Incidente")

            payload = request.json["payload"]

            if self.retornar_modifcacion_aleatorio():
                payload_decoded = json.loads(payload)
                payload_decoded["descripcion"] = "Descripcion Modificada"
                payload = json.dumps(payload_decoded)

            new_message = json.dumps({
                'id': request.json["id"],
                'payload': payload
            })

            print(f"New message: {new_message}")

            future = publisher_client.publish(topic_path, new_message.encode('utf-8'))
            print(f"message published")

            future.result()

            return future.result(), 200
        except Exception as e:
            print(e)
            return {'error': f'Ocurrió un error: {str(e)}'}, 500
