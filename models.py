from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Favorite(db.Model):
    """
    Modelo representativo principal de favoritos conectado de forma relacional con SQLAlchemy.
    Almacena las abstracciones requeridas por el usuario.
    """
    id = db.Column(db.Integer, primary_key=True) # Clave primaria autoincremental de la columna
    api_id = db.Column(db.Integer, unique=True) # Identificador en bruto de la API que evita duplicaciones lógicas
    name = db.Column(db.String(100)) # Entidad de cadena de texto correspondiente al nombre
    image = db.Column(db.String(255)) # Vínculo absoluto o hipervínculo contenedor de la imagen provista