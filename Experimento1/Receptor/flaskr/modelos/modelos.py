import datetime
import enum

from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()

class TipoEstado(enum.Enum):
    UnHealthy = "unHealthy"
    Healthy = "healthy"

class TipoEstadoEstadoAuditoria(enum.Enum):
    Pending = "pending"
    Completed = "completed"

class Auditoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_llamada = db.Column(db.String(50))
    fecha_registro = db.Column(db.DateTime, default=datetime.datetime.now)
    fecha_finalizacion = db.Column(db.DateTime, nullable=True)
    estado_principal = db.Column(db.Enum(TipoEstado))
    id_estado_principal = db.Column(db.String(50))
    estado_redundante = db.Column(db.Enum(TipoEstado))
    id_estado_redundante = db.Column(db.String(50))
    estado_auditoria = db.Column(db.Enum(TipoEstadoEstadoAuditoria))


    def __repr__(self):
        return "{}-{}-{}-{}-{}".format(self.id,self.id_llamada,self.fecha_registro,self.fecha_finalizacion,self.tipo_app)


class EnumADiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.value

class AuditoriaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Auditoria
        include_relationships = True
        load_instance = True

    estado_principal = EnumADiccionario(attribute='estado_principal')
    estado_redundante = EnumADiccionario(attribute='estado_redundante')
    estado_auditoria = EnumADiccionario(attribute='estado_auditoria')


