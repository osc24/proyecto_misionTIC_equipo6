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
    if "usuario" in session:
        try:
            with sqlite3.connect(ruta_db) as con: 
                cur=con.cursor()
                cur.execute("SELECT rol FROM usuarios WHERE correo=?",[session["usuario"]])
                row = cur.fetchone()
                rol=row[0]
                return render_template(ruta_inicio,rol=rol)
        except Error:
            print(Error)
    return render_template(ruta_inicio,rol=0)



@app.route("/cartelera")
def cartelera():
    if "usuario" in session:
        try:
            with sqlite3.connect(ruta_db) as con: 
                cur=con.cursor()
                cur.execute("SELECT rol FROM usuarios WHERE correo=?",[session["usuario"]])
                row = cur.fetchone()
                rol=row[0]
                return render_template(ruta_cartelera,rol=rol)
        except Error:
            print(Error)
    return render_template(ruta_cartelera,rol=0)

@app.route("/detalle", methods=["GET","POST"])
def detalles():
    if "usuario" in session:
        try:
            with sqlite3.connect(ruta_db) as con: 
                cur=con.cursor()
                cur.execute("SELECT rol FROM usuarios WHERE correo=?",[session["usuario"]])
                row = cur.fetchone()
                rol=row[0]
                return render_template(ruta_detalle,rol=rol)
        except Error:
            print(Error)
    return render_template(ruta_detalle,rol=0)

@app.route("/buscar", methods=["GET","POST"])
def buscar():
    if "usuario" in session:
        try:
            with sqlite3.connect(ruta_db) as con: 
                cur=con.cursor()
                cur.execute("SELECT rol FROM usuarios WHERE correo=?",[session["usuario"]])
                row = cur.fetchone()
                rol=row[0]
                return render_template(ruta_buscar,rol=rol)
        except Error:
            print(Error)
    return render_template(ruta_buscar,rol=0)

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

@app.route("/logout")
def logout():
    if "usuario" in session:
        session.pop("usuario",None)
        return render_template(ruta_inicio,rol=0)
    else:
        return "No hay sesion activa"

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
    if "usuario" in session:
        return render_template(ruta_perfil)
    return "Debe iniciar sesion"

@app.route("/dashboard")
def dashboard():
    if ("usuario" in session):
        try:
            with sqlite3.connect(ruta_db) as con: 
                cur=con.cursor()
                cur.execute("SELECT rol FROM usuarios WHERE correo=?",[session["usuario"]])
                row = cur.fetchone()
                rol=row[0]
                if rol=="usuario_final":
                    return "No tiene los permisos para esta acción"
                return render_template(ruta_dashboard,rol=rol)
        except Error:
            print(Error)
    return "Debe iniciar sesion"


if __name__=="__main__":
    app.run(debug=True, port=8000)

