import datetime
import enum

from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()

class EstadoVerificacion(enum.Enum):
    Modified = "Modified"
    NoModified = "NoModified"

class TipoEstadoEstadoAuditoria(enum.Enum):
    Registered = "Registered"
    Completed = "completed"

class Auditoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.datetime.now)
    fecha_finalizacion = db.Column(db.DateTime, nullable=True)
    estado_verificacion = db.Column(db.Enum(EstadoVerificacion))
    checksum1 = db.Column(db.String(1000))
    checksum2 = db.Column(db.String(1000))
    payload = db.Column(db.String(1000))
    payload2 = db.Column(db.String(1000))
    estado_auditoria = db.Column(db.Enum(TipoEstadoEstadoAuditoria))

    def __repr__(self):
        return "{}-{}-{}-{}-{}-{}-{}-{}-{}".format(self.id,self.fecha_registro,self.fecha_finalizacion,self.estado_verificacion,self.checksum1,self.checksum2,self.payload,self.payload2, self.estado_auditoria)


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

    estado_verificacion = EnumADiccionario(attribute='estado_verificacion')
    estado_auditoria = EnumADiccionario(attribute='estado_auditoria')


