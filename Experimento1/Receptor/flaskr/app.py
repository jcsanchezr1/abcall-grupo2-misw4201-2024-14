from flaskr import create_app

from .modelos import db, Auditoria, TipoApp
from .modelos import AuditoriaSchema
from .vistas import VistaAuditoria
from flask_restful import Api


app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

api = Api(app)
api.add_resource(VistaAuditoria, '/auditorias')

#prueba
"""with app.app_context():
    auditoria_schema =  auditoriaschema()
    nueva_auditoria = auditoria(
        id_llamada="abc123",                    
        fecha_registro=datetime.datetime.now(),           
        fecha_finalizacion=datetime.datetime.now(),  
        tipo_app=TipoApp.ACTIVO                  
    )

    
    db.session.add(nueva_auditoria)
    db.session.commit()
    #print(auditoria.query.all())
    print([auditoria_schema.dumps(auditor) for auditor in auditoria.query.all()])"""


