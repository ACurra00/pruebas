from sqlalchemy import Column, Integer, String


from db.base_class import Base


class Roles(Base):
    ci = Column(Integer,primary_key = True, index=True)
    name = Column(String,nullable= False)
    apellidos = Column(String,nullable=False)
    ocupacion = Column(String)
    resumen_rol = Column(String,nullable = False)
    correo = Column(String,nullable=False)
    