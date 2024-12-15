from flask import Flask, render_template, request, redirect, url_for, flash
import redis
from waitress import serve

# Configuración de Flask
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Para manejar sesiones y mensajes flash

keydb = redis.Redis(host="localhost", port= 6379, db=0, decode_responses=True)

# Rutas de la aplicación
@app.route("/")
def index():
    """Página principal que muestra el listado de recetas."""
    try:
        claves = keydb.keys()
        print(f"✅ Claves encontradas: {claves}")
    except redis.ConnectionError as e:
        print(f"❌ Error al conectar con KeyDB: {e}")
    except Exception as e:
        print(f"❌ Otro error: {e}")
    recetas = [{"nombre": clave} for clave in claves]
    return render_template("index.html", recetas=recetas)


@app.route("/receta/<nombre>")
def ver_receta(nombre):
    """Ver los detalles de una receta."""
    if not keydb.exists(nombre):
        flash("❌ La receta no existe.")
        return redirect(url_for("index"))

    receta = keydb.hgetall(nombre)
    return render_template("receta.html", nombre=nombre, receta=receta)


@app.route("/agregar", methods=["GET", "POST"])
def agregar_receta():
    """Agregar una nueva receta."""
    if request.method == "POST":
        nombre = request.form["nombre"]
        ingredientes = request.form["ingredientes"]
        pasos = request.form["pasos"]

        if keydb.exists(nombre):
            flash("❌ Ya existe una receta con ese nombre.")
            return redirect(url_for("agregar_receta"))

        keydb.hset(nombre, mapping={"ingredientes": ingredientes, "pasos": pasos})
        flash("✅ Receta agregada exitosamente.")
        return redirect(url_for("index"))

    return render_template("agregar.html")


@app.route("/editar/<nombre>", methods=["GET", "POST"])
def editar_receta(nombre):
    """Editar una receta existente."""
    if not keydb.exists(nombre):
        flash("❌ La receta no existe.")
        return redirect(url_for("index"))

    if request.method == "POST":
        nuevos_ingredientes = request.form["ingredientes"]
        nuevos_pasos = request.form["pasos"]

        keydb.hset(nombre, mapping={"ingredientes": nuevos_ingredientes, "pasos": nuevos_pasos})
        flash("✅ Receta actualizada exitosamente.")
        return redirect(url_for("ver_receta", nombre=nombre))

    receta = keydb.hgetall(nombre)
    return render_template("editar.html", nombre=nombre, receta=receta)


@app.route("/eliminar/<nombre>", methods=["POST"])
def eliminar_receta(nombre):
    """Eliminar una receta existente."""
    if not keydb.exists(nombre):
        flash("❌ La receta no existe.")
    else:
        keydb.delete(nombre)
        flash("✅ Receta eliminada exitosamente.")

    return redirect(url_for("index"))


# Iniciar la aplicación Flask
if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)
