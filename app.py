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

##RUTAS##
ruta_inicio="index.html"
ruta_buscar="Buscar.html"
ruta_cartelera="Cartelera.html"
ruta_dashboard="Dashboard.html"
ruta_detalle="Detalle.html"
ruta_login="Iniciar-Sesion.html"
ruta_perfil="Perfil.html"
ruta_registro="Registro.html"
ruta_db="database.db"
##



app=Flask(__name__)
app.secret_key=os.urandom(24)

@app.route("/", methods=["GET","POST"])
def inicio():
    return render_template(ruta_inicio)

@app.route("/cartelera")
def cartelera():
    return render_template(ruta_cartelera)

@app.route("/detalle", methods=["GET","POST"])
def detalles():
    return render_template(ruta_detalle)

@app.route("/buscar", methods=["GET","POST"])
def buscar():
    return render_template(ruta_buscar)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        correo=escape(request.form["correo"])
        clave=escape(request.form["clave"])
        try:
                with sqlite3.connect(ruta_db) as con: 
                    cur=con.cursor()
                    cur.execute("SELECT clave FROM usuarios WHERE correo=?",[correo])
                    row = cur.fetchone()
                    if row is None:
                        return "Usuario no se encuentra en la base de datos"
                    else:
                        if check_password_hash(row[0],clave):
                            session["usuario"]=correo
                            return redirect("/")
                        else:
                            return "Clave incorrecta"
        except Error:
            print(Error)
    return render_template(ruta_login)

@app.route("/registro", methods=["GET","POST"])
def registro():
    if request.method=="POST":
        nombre=escape(request.form["nombres"])
        apellidos=escape(request.form["apellidos"])
        documento=escape(request.form["documento"])
        correo=escape(request.form["correo"])
        clave=escape(request.form["clave"])

        hash=generate_password_hash(clave)
        try:
            with sqlite3.connect(ruta_db) as con: 
                cur=con.cursor()
                cur.execute("SELECT correo FROM usuarios WHERE correo=?",[correo])
                row = cur.fetchone()
                if row is None:
                    try:
                        with sqlite3.connect(ruta_db) as con:
                            rol="usuario_final"
                            cur= con.cursor()
                            cur.execute(" INSERT INTO usuarios(nombre, apellidos, documento, correo, clave,rol) VALUES (?,?,?,?,?,?)", (nombre,apellidos,documento,correo,hash,rol))
                            con.commit()
                            return redirect("/login")
                    except  Error:
                        print(Error)
                else:
                    return "Usuario ya registrado"
        except Error:
            print(Error)
        
    return render_template(ruta_registro)

@app.route("/perfil", methods=["GET","POST"])
def perfil():
    return render_template(ruta_perfil)

if __name__=="__main__":
    app.run(debug=True, port=8000)

