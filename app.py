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
    return render_template(ruta_login)

@app.route("/registro", methods=["GET","POST"])
def registro():
    return render_template(ruta_registro)

@app.route("/perfil", methods=["GET","POST"])
def perfil():
    return render_template(ruta_perfil)

if __name__=="__main__":
    app.run(debug=True, port=8000)

