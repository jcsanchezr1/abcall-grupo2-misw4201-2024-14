from flask_restful import Api
from Monitor import create_app
from .modelos import db, HealthCheck
from .vistas import VistaHealthChecks

import time
import threading
import requests

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

api = Api(app)
api.add_resource( VistaHealthChecks, '/monitor/healthcheck' )

_timer_iniciado = False

def check_health(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        with app.app_context():
            nuevo_dato = HealthCheck(
                status = data.get('status'),
                component = data.get('component'),
            )
            db.session.add(nuevo_dato)
            db.session.commit()
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}, 500

def ejecutar_periodicamente(intervalo):
    while True:
        with app.app_context():
            check_health( 'http://127.0.0.1:9999/redundante/healthcheck' )
            check_health( 'http://127.0.0.1:9999/principal/healthcheck' )
        time.sleep(intervalo)

def iniciar_timer():
    hilo = threading.Thread(
        target = ejecutar_periodicamente,
        args = (10,)
    )
    hilo.daemon = True
    hilo.start()

@app.before_request
def activar_timer():
    global _timer_iniciado
    if not _timer_iniciado:
        iniciar_timer()
        _timer_iniciado = True

if __name__ == '__main__':
    app.run( debug = True )