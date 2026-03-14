from flask import Flask, render_template, request, redirect
from models import db
from models import Favorite
import requests
import os

# Directorio base del proyecto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Ruta absoluta a la base de datos SQLite
DB_PATH = os.path.join(BASE_DIR, "instance", "app.db")

app = Flask(__name__)

# URL base de la API pública de Rick and Morty
API_URL = "https://rickandmortyapi.com/api/character"

# Configuración de inicialización de motor de base de datos local
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicialización del entorno de persistencia a nuestra aplicación
db.init_app(app)

# Creación en vivo del esquema y tablas dentro del entorno activo en caso de que aún no existan
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    """Ruta principal para explorar la lista global de personajes y acceder a la búsqueda."""
    
    # Obtener el número de página correspondiente de los parámetros GET. Su valor por defecto es 1.
    page = request.args.get("page", 1)

    # Identificar si existe alguna consulta de término específico por parámetro 'name'
    name = request.args.get("name")

    # Si hay búsqueda por nombre estricta, se inhabilita la lógica regular de paginación
    if name:
        response = requests.get(API_URL, params={"name": name})
        # El código 200 representa éxito; cualquier otro infiere como que el personaje estipulado no existe en la API
        if response.status_code != 200:
            return render_template("index.html", character=[], search=True, error_message='Personaje No encontrado')
        data = response.json()
        return render_template("index.html", characters=data["results"], search=True)
        
    # Lógica estándar de obtención del listado iterativo de personajes con base al valor de paginación referenciado
    response = requests.get(API_URL, params={"page": page})
    data = response.json()

    return render_template("index.html", characters=data["results"], info=data["info"], page=int(page), search=False)


@app.route("/save", methods=["POST"])
def save():
    """Ruta habilitada vía POST para persistir la identidad de un personaje en la lista de favoritos."""

    # Extracción en crudo de las variables ocultas suministradas vía datos del formulario front-end
    api_id = request.form["api_id"]
    name = request.form["name"]
    image = request.form["image"]
    page = request.form.get("page", 1)

    # Solo insertamos y consolidamos al personaje asumiendo que el identificador principal no exista en base de datos ya.
    # Así se previenen colisiones de consistencia de duplicados.
    if not Favorite.query.filter_by(api_id=api_id).first():

        fav = Favorite(api_id=api_id, name=name, image=image)

        db.session.add(fav)

        db.session.commit()

    # Redirecciona devuelta a la página activa exacta donde el usuario se encontraba al emitir el POST.
    return redirect(f"/?page={page}")

@app.route("/favorites")
def favorites():
    """Página general utilizada para enmarcar a todos los personajes favoritos del sistema alojados a nivel local."""
    favorites = Favorite.query.all()

    return render_template("favorites.html", favorites=favorites)


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    """Acceso que procesa la anulación permanente y segura de un personaje favorito a través de su identificador privado."""
    fav = Favorite.query.get(id)
    if fav:
        db.session.delete(fav)
        db.session.commit()
    
    return redirect("/favorites")


if __name__ == "__main__":
    # Inicio inmediato del servidor subyacente. Habilite depuración (debug mode).
    app.run(debug=True)