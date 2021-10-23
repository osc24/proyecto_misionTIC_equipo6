from logging import debug, error
from sqlite3.dbapi2 import Cursor
from flask import Flask, render_template, request, flash,session,redirect
import os
from flask import *
from flask.scaffold import _matching_loader_thinks_module_is_package
import sqlite3
from sqlite3 import Error

from markupsafe import escape 
import hashlib
from werkzeug.exceptions import UnsupportedMediaType
from werkzeug.security import generate_password_hash, check_password_hash

app=Flask(__name__)
ruta_db="database.db"

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

@app.route("/registro",methods=['GET', 'POST'])
def registro():
    if request.method=="POST":
        documento=escape(request.form["documento"])
        correo=escape(request.form["correo"])
        nombre=escape(request.form["nombres"])
        apellidos=escape(request.form["apellidos"])
        clave=escape(request.form["clave"])

       
        hash=generate_password_hash(clave)
        try:
            with sqlite3.connect(ruta_db) as con:
                cur= con.cursor()
                cur.execute(" INSERT INTO usuarios(nombre, apellidos, numeroDocumento, correo, clave) VALUES (?,?,?,?,?)", (nombre,apellidos,documento,correo,hash))
                con.commit()
                return redirect("/")
        except  Error:
            print(Error)

    return render_template("Registro-de-Usuario.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="POST":
        usuario=escape(request.form["correo"])
        password=escape(request.form["clave"])
        try:
            with sqlite3.connect(ruta_db) as con: 
                cur=con.cursor()
                cur.execute("SELECT clave FROM usuarios WHERE correo=?",[usuario])
                row = cur.fetchone()
                if row is None:
                    return "Usuario no se encuentra en la base de datos"
                    
                else:
                    if check_password_hash(row[0],password):
                        session["usuario"]=usuario
                        return redirect("/cartelera")
                    else:
                        return "Clave incorrecta"
        except Error:
            print(Error)
    return "Error en el metodo"

@app.route("/IniciarSesion")
def iniciarSesion():
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

@app.route("/cartelera", methods=["GET"])
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

