from flask_restful import Resource

from ..modelos import db, Auditoria, AuditoriaSchema,TipoEstadoEstadoAuditoria, TipoEstado
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

    def get(self):
        return [auditoria_schema.dumps(auditor) for auditor in Auditoria.query.all()]

    def post(self):

        monitor_url = 'http://127.0.0.1:5000/monitor/healthcheck'
        try:
            monitor_response = requests.get(monitor_url)
            if monitor_response.status_code != 200:
                return {'error': 'Monitor service is unavailable or returned an error'}, 503

            monitor_data = monitor_response.json()

            principal_status = monitor_data['principal']['status'].upper()
            principal_id = monitor_data['principal']['id']
            redundante_status = monitor_data['redundante']['status'].upper()
            redundante_id = monitor_data['redundante']['id']
            estado_auditoria = TipoEstadoEstadoAuditoria.Pending

            id_llamada = request.json['id_llamada']
            fecha_registro = datetime.datetime.now()

            nueva_auditoria = Auditoria(
                id_llamada=id_llamada,
                fecha_registro=fecha_registro,
                estado_principal=TipoEstado(principal_status),
                id_estado_principal=str(principal_id),
                estado_redundante=TipoEstado(redundante_status),
                id_estado_redundante=str(redundante_id),
                estado_auditoria=estado_auditoria
            )

            db.session.add(nueva_auditoria)
            db.session.commit()

            auditoria_id = nueva_auditoria.id

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

            data = response.json()
            print("Respuesta JSON:", data)
            return auditoria_schema.dump(nueva_auditoria), 201
        except Exception as e:
            return {'error': f'Ocurrió un error: {str(e)}'}, 500

    def put(self):
        try:
            id_auditoria = request.json["id_auditoria"]
            id_llamada = request.json["id_llamada"]
            componente = request.json["componente"]
            print(id_auditoria)

            if not id_auditoria or not id_llamada or not componente:
                print("Faltan datos en el mensaje.")
                message.nack()
                return

            auditoria = Auditoria.query.get(id_auditoria)
            print(auditoria)
            if not auditoria:
                print(f"Auditoría con id {id_auditoria} no encontrada.")
                message.nack()
                return

            if componente == 'Principal':
                if auditoria.estado_principal == TipoEstado.Healthy:
                    auditoria.estado_auditoria = TipoEstadoEstadoAuditoria.Completed
                    auditoria.fecha_finalizacion = datetime.datetime.now()
                    print(f"Auditoría {id_auditoria} completada por componente Principal (Healthy).")
                    db.session.commit()
            elif componente == 'Redundante':
                if auditoria.estado_principal == TipoEstado.UnHealthy:
                    auditoria.estado_auditoria = TipoEstadoEstadoAuditoria.Completed
                    auditoria.fecha_finalizacion = datetime.datetime.now()
                    print(f"Auditoría {id_auditoria} completada por componente Redundante (unHealthy).")
                    db.session.commit()

            return "", 200
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

        try:
            # Usar el contexto de aplicación para acceder a la base de datos

            message_data = json.loads(message.data.decode('utf-8'))
            print(f"Received message: {message_data}")
            put_url = 'http://localhost:5001/auditorias'
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