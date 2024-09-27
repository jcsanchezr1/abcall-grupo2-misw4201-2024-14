from flask_restful import Resource

from flask import request, Flask, request, jsonify
from google.cloud import pubsub_v1

import json

project_id = "abcall"
topic_id = "incidente"
subscription_id = "incidente"

publisher_client = pubsub_v1.PublisherClient()
topic_path = publisher_client.topic_path(project_id, topic_id)
subscriber_client = pubsub_v1.SubscriberClient()
subscription_path = subscriber_client.subscription_path(project_id, subscription_id)


class VistaGestorIncidente(Resource):

   def post(self):
        try:
            print("Creando Incidente")            
            
            new_message =  json.dumps({
                                                    'id': request.json["id"],
                                                    'payload': request.json["payload"]                                                    
                                                })
            
            print(f"New message: {new_message}")

            future = publisher_client.publish(topic_path, new_message.encode('utf-8'))
            print(f"message published")

            future.result()
                        
            return future.result(), 200
        except Exception as e:
            print(e)
            return {'error': f'Ocurrió un error: {str(e)}'}, 500
