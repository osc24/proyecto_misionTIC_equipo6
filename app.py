from flask import Flask, app, render_template

app=Flask(__name__)

num_sillas=90
lista_usuarios={
    "111": "pedro",
    "222": "daniela",
    "333": "maria"
}

Lista_peliculas={
    "111": "Venom",
    "222": "Los locos adams",
    "333": "El ultimo duelo"
}

@app.route("/", methods=["GET"])
def inicio():
    return render_template("Cartelera.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    return render_template("Registro-de-Usuario.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("Iniciar-Sesion.html")

@app.route("/perfil")
def perfil1():
    return render_template("Perfil-de-Usuario.html")

@app.route("/perfil/<id_usuario>",methods=["GET"])
def perfil(id_usuario):

    if id_usuario in lista_usuarios:
        return f"Perfil del usuario {lista_usuarios[id_usuario]}"
    else: 
        return "Perfil del usuario no encontrado"

@app.route("/dashboard",methods=["GET"])
def dashboard():
    return render_template("Dashboard.html")

@app.route("/cartelera", methods=["GET", "POST"])
def cartelera():
    return render_template("Cartelera.html")

@app.route("/detalles")
def detalles():
    return render_template("Detalle.html")


@app.route("/pelicula/<id_pelicula>",methods=["GET"])
def detalle(id_pelicula):
    if (id_pelicula in Lista_peliculas):
        return f"Detalle de funcion de la pelicula: {Lista_peliculas[id_pelicula]}"
    else:
        return "No se encontro la funcion"

@app.route("/buscar",methods=["GET","POST"])
def busqueda():
    return render_template("Buscar.html")


@app.route("/restablecer-contraseña")
def restablecer_contraseña():
    return render_template("Restablecer-contraseña.html")

@app.route("/comprar")
def comprar():
    if num_sillas>0:
        return render_template("Comprar.html")
    else:
        return "No hay sillas libres"



if __name__=="__main__":
    app.run(debug=True, port=8000)

