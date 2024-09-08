from flask_restful import Api
from flaskr import create_app
from .modelos import db, HealthCheck
from .vistas import VistaHealthChecks

import schedule
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

def ejecutar_periodicamente():
    print("se llama al ejecutar_periodicamente")
    check_health('http://mockserver:8080/redundante/healthcheck')
    check_health('http://mockserver:8080/principal/healthcheck')

def job():
    with app.app_context():
        ejecutar_periodicamente()

schedule.every(1).seconds.do(job)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)  # Espera 1 segundo entre cada verificación

scheduler_thread = threading.Thread(target=run_schedule)
scheduler_thread.daemon = True
scheduler_thread.start()

if __name__ == '__main__':
    app.run(debug=True)
