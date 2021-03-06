import sqlite3
import base64
import hashlib
from flask import *
from flask import Flask, render_template,redirect, flash, request, session
from flask.scaffold import _matching_loader_thinks_module_is_package
from markupsafe import escape 
from logging import debug, error
from sqlite3 import Error
from sqlite3.dbapi2 import Cursor
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
ruta_editarFuncion="Editar-Funcion.html"
ruta_editarUsuario="Editar-Usuario.html"
ruta_agregarFuncion="Agregar-Funcion.html"
##

#crear el item de app
app=Flask(__name__)
app.secret_key=b'\xfcy\x9c\xea\xd8k\x80\xc4RW\xed\xd0\xc2w\xaaN\xddr\xc7|\x9c\xc5\xf1j' #antes os.urandom(24)

def roleID():
    try:
        with sqlite3.connect(ruta_db) as con: 
            cur=con.cursor()
            cur.execute("SELECT rol FROM usuarios WHERE correo=?",[session["usuario"]])
            row = cur.fetchone()
            rol=row[0]
            cur=con.cursor()
            cur.execute("SELECT id_usuario FROM usuarios WHERE correo=?",[session["usuario"]])
            row=cur.fetchone()
            id=row[0]
            return rol,id
    except Error:
        print(Error)

@app.route("/", methods=["GET","POST"])
def inicio():   
    if "usuario" in session:
        try:
            with sqlite3.connect(ruta_db) as con: 
                cur=con.cursor()
                cur.execute("SELECT rol FROM usuarios WHERE correo=?",[session["usuario"]])
                row = cur.fetchone()
                rol=row[0]
                cur=con.cursor()
                cur.execute("SELECT id_usuario FROM usuarios WHERE correo=?",[session["usuario"]])
                row=cur.fetchone()
                id=row[0]
                return render_template(ruta_inicio,rol=rol,id=id)
        except Error:
            print(Error)
    return render_template(ruta_inicio,rol=0,id=0)



@app.route("/cartelera")
def cartelera():
    if "usuario" in session:
        try:
            with sqlite3.connect(ruta_db) as con: 
                cur=con.cursor()
                cur.execute("SELECT rol FROM usuarios WHERE correo=?",[session["usuario"]])
                row = cur.fetchone()
                rol=row[0]
                con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute("SELECT * FROM peliculas WHERE enCartelera=? LIMIT 4",["True"])
                row_pelicula = cur.fetchall()  
                cur=con.cursor()
                cur.execute("SELECT id_usuario FROM usuarios WHERE correo=?",[session["usuario"]])
                row=cur.fetchone()
                id=row[0]
                return render_template(ruta_cartelera,rol=rol,row_pelicula=row_pelicula,id=id)
        except Error:
            print(Error)
    else:
        try:
            with sqlite3.connect(ruta_db) as con: 
                con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute("SELECT * FROM peliculas LIMIT 4")
                row_pelicula = cur.fetchall()
                
                return render_template(ruta_cartelera,rol=0,row_pelicula=row_pelicula,id=0)
        except Error:
            print(Error)
        return render_template(ruta_cartelera,rol=0)

@app.route("/detalle/<string:id>", methods=["GET","POST"])
def detalles(id=id):
    if "usuario" in session:
        try:
            with sqlite3.connect(ruta_db) as con: 
                cur=con.cursor()
                cur.execute("SELECT rol FROM usuarios WHERE correo=?",[session["usuario"]])
                row = cur.fetchone()
                rol=row[0]
                cur=con.cursor()
                cur.execute("SELECT id_usuario FROM usuarios WHERE correo=?",[session["usuario"]])
                row=cur.fetchone()
                id_usuario=row[0]
                con.row_factory = sqlite3.Row
                cur=con.cursor()
                cur.execute("SELECT * FROM comentarios WHERE id_pelicula=?",[id])
                row_comentarios=cur.fetchall()
                cur=con.cursor()
                cur.execute("SELECT avg(puntaje) from comentarios where id_pelicula=?",[id])
                row=cur.fetchone()
                promedio=row[0]
                print(promedio)
                cur=con.cursor()
                cur.execute("update peliculas SET puntajePromedio=? where id_pelicula=?",(promedio,id))
                con.commit()
                con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute("SELECT * FROM peliculas WHERE id_pelicula=?",[id])
                row_pelicula = cur.fetchone()
                return render_template(ruta_detalle,rol=rol,row_pelicula=row_pelicula,id=id_usuario,row_comentarios=row_comentarios)
        except Error:
            print(Error)
    else:
        try:
            with sqlite3.connect(ruta_db) as con: 
                con.row_factory = sqlite3.Row
                cur=con.cursor()
                cur.execute("SELECT * FROM comentarios WHERE id_pelicula=?",[id])
                row_comentarios=cur.fetchall()
                cur=con.cursor()
                cur.execute("SELECT avg(puntaje) from comentarios where id_pelicula=?",[id])
                row=cur.fetchone()
                promedio=row[0]
                print(promedio)
                cur=con.cursor()
                cur.execute("update peliculas SET puntajePromedio=? where id_pelicula=?",(promedio,id))
                con.commit()
                con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute("SELECT * FROM peliculas WHERE id_pelicula=?",[id])
                row_pelicula = cur.fetchone()
                return render_template(ruta_detalle,rol=0,row_pelicula=row_pelicula,id=id,row_comentarios=row_comentarios)
        except Error:
            print(Error)
        return "No existe esta pelicula"

    
@app.route("/buscar", methods=["GET","POST"])
def buscar():
    if request.method=="POST":

        year=escape(request.form["year"])
        genero=escape(request.form["genero"])
        palabra=escape(request.form["busqueda"])
        if "usuario" in session:
            rol,id=roleID()
            print(rol)
            print(id)
            if year =="":
                if genero=="-seleccionar-":
                    if palabra=="":
                        ##000##
                        return "Ingrese datos para buscar"
                    else:
                        ##100##
                        try:
                            with sqlite3.connect(ruta_db) as con: 
                                con.row_factory =sqlite3.Row
                                cur=con.cursor()
                                cur.execute("select * from peliculas WHERE nombrePelicula LIKE '%'||?||'%'",[palabra])
                                row=cur.fetchall()
                                return render_template(ruta_buscar,rol=rol,id=id,row_busqueda=row)
                        except Error:
                            print(Error)
                else:
                    if palabra=="":
                        ##010##
                        try:
                            with sqlite3.connect(ruta_db) as con: 
                                con.row_factory =sqlite3.Row
                                cur=con.cursor()
                                cur.execute("Select * from peliculas where genero=?",[genero])

                                row=cur.fetchall()
                        
                                return render_template(ruta_buscar,rol=rol,id=id,row_busqueda=row)
                        except Error:
                            print(Error)
                    else:
                        ##011##
                        try:
                            with sqlite3.connect(ruta_db) as con: 
                                con.row_factory =sqlite3.Row
                                cur=con.cursor()
                                cur.execute("Select * from peliculas where genero=? or nombrePelicula LIKE '%'||?||'%'",[genero,palabra])
                                row=cur.fetchall()

                                return render_template(ruta_buscar,rol=rol,id=id,row_busqueda=row)
                        except Error:
                            print(Error)
            else:
                if genero=="-seleccionar-":
                    if palabra=="":
                        ##100##
                        try:
                            with sqlite3.connect(ruta_db) as con: 
                                con.row_factory =sqlite3.Row
                                cur=con.cursor()
                                cur.execute("Select * from peliculas where year=?",[year])
                                row=cur.fetchall()
                                return render_template(ruta_buscar,rol=rol,id=id,row_busqueda=row)
                        except Error:
                            print(Error)
                    else:
                        ##101##
                        try:
                            with sqlite3.connect(ruta_db) as con: 
                                con.row_factory =sqlite3.Row
                                cur=con.cursor()
                                cur.execute("Select * from peliculas where year=? or nombrePelicula LIKE '%'||?||'%'",[year,palabra])
                                row=cur.fetchall()
                                return render_template(ruta_buscar,rol=rol,id=id,row_busqueda=row)
                        except Error:
                            print(Error)
                else:
                    if palabra=="":
                        ##110##
                        print("110")
                        try:
                            with sqlite3.connect(ruta_db) as con: 
                                con.row_factory =sqlite3.Row
                                cur=con.cursor()
                                cur.execute("Select * from peliculas where year=? or genero=?",[year,genero])
                                row=cur.fetchall()
                                return render_template(ruta_buscar,rol=rol,id=id,row_busqueda=row)
                        except Error:
                            print(Error)  
                    else:
                        ##111##
                        try:
                            with sqlite3.connect(ruta_db) as con: 
                                con.row_factory =sqlite3.Row
                                cur=con.cursor()
                                cur.execute("Select * from peliculas where year=? or genero=? or nombrePelicula LIKE '%'||?||'%'",[year,genero,palabra])
                                row=cur.fetchall()
                                return render_template(ruta_buscar,rol=rol,id=id,row_busqueda=row)
                        except Error:
                            print(Error)
        else:
            if year =="":
                if genero=="-seleccionar-":
                    if palabra=="":
                        ##000##
                        return "Ingrese datos para buscar"
                    else:
                        ##100##
                        try:
                            with sqlite3.connect(ruta_db) as con: 
                                con.row_factory =sqlite3.Row
                                cur=con.cursor()
                                cur.execute("select * from peliculas WHERE nombrePelicula LIKE '%'||?||'%'",[palabra])
                                row=cur.fetchall()
                                return render_template(ruta_buscar,rol=0,id=0,row_busqueda=row)
                        except Error:
                            print(Error)
                else:
                    if palabra=="":
                        ##010##
                        try:
                            with sqlite3.connect(ruta_db) as con: 
                                con.row_factory =sqlite3.Row
                                cur=con.cursor()
                                cur.execute("Select * from peliculas where genero=?",[genero])

                                row=cur.fetchall()
                        
                                return render_template(ruta_buscar,rol=0,id=0,row_busqueda=row)
                        except Error:
                            print(Error)
                    else:
                        ##011##
                        try:
                            with sqlite3.connect(ruta_db) as con: 
                                con.row_factory =sqlite3.Row
                                cur=con.cursor()
                                cur.execute("Select * from peliculas where genero=? or nombrePelicula LIKE '%'||?||'%'",[genero,palabra])
                                row=cur.fetchall()

                                return render_template(ruta_buscar,rol=0,id=0,row_busqueda=row)
                        except Error:
                            print(Error)
            else:
                if genero=="-seleccionar-":
                    if palabra=="":
                        ##100##
                        try:
                            with sqlite3.connect(ruta_db) as con: 
                                con.row_factory =sqlite3.Row
                                cur=con.cursor()
                                cur.execute("Select * from peliculas where year=?",[year])
                                row=cur.fetchall()
                                return render_template(ruta_buscar,rol=0,id=0,row_busqueda=row)
                        except Error:
                            print(Error)
                    else:
                        ##101##
                        try:
                            with sqlite3.connect(ruta_db) as con: 
                                con.row_factory =sqlite3.Row
                                cur=con.cursor()
                                cur.execute("Select * from peliculas where year=? or nombrePelicula LIKE '%'||?||'%'",[year,palabra])
                                row=cur.fetchall()
                                return render_template(ruta_buscar,rol=0,id=0,row_busqueda=row)
                        except Error:
                            print(Error)
                else:
                    if palabra=="":
                        ##110##
                        print("110")
                        try:
                            with sqlite3.connect(ruta_db) as con: 
                                con.row_factory =sqlite3.Row
                                cur=con.cursor()
                                cur.execute("Select * from peliculas where year=? or genero=?",[year,genero])
                                row=cur.fetchall()
                                return render_template(ruta_buscar,rol=0,id=0,row_busqueda=row)
                        except Error:
                            print(Error)  
                    else:
                        ##111##
                        try:
                            with sqlite3.connect(ruta_db) as con: 
                                con.row_factory =sqlite3.Row
                                cur=con.cursor()
                                cur.execute("Select * from peliculas where year=? or genero=? or nombrePelicula LIKE '%'||?||'%'",[year,genero,palabra])
                                row=cur.fetchall()
                                return render_template(ruta_buscar,rol=0,id=0,row_busqueda=row)
                        except Error:
                            print(Error)
    if "usuario" in session:
        rol,id=roleID()
        return render_template(ruta_buscar,rol=rol,id=0,row_busqueda=0)
    return render_template(ruta_buscar,rol=0,id=0,row_busqueda=0)

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
                            return render_template(ruta_login,id=0)
        except Error:
            print(Error)
    return render_template(ruta_login,id=0)

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
        
    return render_template(ruta_registro,id=0)

@app.route("/perfil/<string:id>", methods=["GET","POST"])
def perfil(id=id):
    if "usuario" in session:
        try:
            with sqlite3.connect(ruta_db) as con: 
                con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute("SELECT * FROM usuarios WHERE id_usuario=?",[id])
                row_perfil = cur.fetchone()
                cur=con.cursor()
                cur.execute("SELECT rol FROM usuarios WHERE correo=?",[session["usuario"]])
                row = cur.fetchone()
                rol=row[0]
                con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute("SELECT * FROM comentarios WHERE usuario=?",[session["usuario"]])
                row_comentarios = cur.fetchall()
                return render_template(ruta_perfil,row_usuario=row_perfil,rol=rol,row_comentarios=row_comentarios)
        except Error:
            print(Error)
    return redirect("/login")

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
                    return "No tiene los permisos para esta acci??n"
                con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute("SELECT * FROM usuarios")
                row_usuarios = cur.fetchall()  
                cur=con.cursor()
                cur.execute("SELECT id_usuario FROM usuarios WHERE correo=?",[session["usuario"]])
                row=cur.fetchone()
                id=row[0]
                con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute("SELECT * FROM peliculas")
                row_peliculas = cur.fetchall()  
                return render_template(ruta_dashboard,rol=rol,row_usuarios=row_usuarios,id=id,row_peliculas=row_peliculas)
        except Error:
            print(Error)
    return redirect("/login")


@app.route("/comprar/<string:id>",methods=["GET","POST"])
def comprar(id=id):
    if request.method=="POST":
        if "usuario" in session:
            try:
                with sqlite3.connect(ruta_db) as con:
                    tiquetes=escape(request.form["tiquetes"]) 
                    cur=con.cursor()
                    cur.execute("SELECT rol FROM usuarios WHERE correo=?",[session["usuario"]])
                    row = cur.fetchone()
                    rol=row[0]
                    cur=con.cursor()
                    cur.execute("update peliculas SET tiquetesTotales=tiquetesTotales-?, tiquetesVendidos=? where id_pelicula=?",(tiquetes,tiquetes,id))
                    con.commit()
                    
                    cur=con.cursor()
                    cur.execute("SELECT id_usuario FROM usuarios WHERE correo=?",[session["usuario"]])
                    row=cur.fetchone()
                    id_usuario=row[0]
                    con.row_factory = sqlite3.Row
                    cur = con.cursor()
                    cur.execute("SELECT * FROM comentarios WHERE id_pelicula=?",[id])
                    row_comentarios = cur.fetchall()
                    cur = con.cursor()
                    cur.execute("SELECT nombrePelicula FROM peliculas WHERE id_pelicula=?",[id])
                    row = cur.fetchone()
                    nombre_pelicula=row[0]
                    cur = con.cursor()
                    cur.execute("INSERT INTO tiquetes(usuario, pelicula) VALUES (?,?)",(session["usuario"], nombre_pelicula))
                    con.commit()
                    cur=con.cursor()
                    cur.execute("SELECT avg(puntaje) from comentarios where id_pelicula=?",[id])
                    row=cur.fetchone()
                    promedio=row[0]
                    cur=con.cursor()
                    cur.execute("update peliculas SET puntajePromedio=? where id_pelicula=?",(promedio,id))
                    con.commit()
                    con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                    cur = con.cursor()
                    cur.execute("SELECT * FROM peliculas WHERE id_pelicula=?",[id])
                    row_pelicula = cur.fetchone()
                    return render_template(ruta_detalle,rol=rol,row_pelicula=row_pelicula,id=id,row_comentarios=row_comentarios)
            except Error:
                print(Error)
        else:
            return "Debe iniciar sesion para poder comprar"
        
@app.route("/calificar/<string:id>",methods=["GET","POST"])
def calificar(id=id):
    if request.method=="POST":
        if "usuario" in session:
            try:
                with sqlite3.connect(ruta_db) as con:
                    cur=con.cursor()
                    cur.execute("SELECT rol FROM usuarios WHERE correo=?",[session["usuario"]])
                    row = cur.fetchone()
                    rol=row[0]
                    comentario=escape(request.form["comentario"])
                    calificacion=escape(request.form["calificacion"])
                    cur=con.cursor()
                    cur.execute("SELECT id_usuario FROM usuarios WHERE correo=?",[session["usuario"]])
                    row=cur.fetchone()
                    id_usuario=row[0]
                    cur=con.cursor()
                    cur.execute("SELECT nombrePelicula FROM peliculas WHERE id_pelicula=?",[id])
                    row=cur.fetchone()
                    nombrePelicula=row[0]
                    print(nombrePelicula)
                    cur = con.cursor()
                    cur.execute("INSERT INTO comentarios(usuario, comentario,id_pelicula,puntaje,nombrePelicula) VALUES (?,?,?,?,?)",(session["usuario"],comentario, id,calificacion,nombrePelicula))
                    con.commit()
                    print("Si lo hizo")
                    con.row_factory = sqlite3.Row
                    cur = con.cursor()
                    cur.execute("SELECT * FROM comentarios WHERE id_pelicula=?",[id])
                    row_comentarios = cur.fetchall()
                    cur=con.cursor()
                    cur.execute("SELECT avg(puntaje) from comentarios where id_pelicula=?",[id])
                    row=cur.fetchone()
                    promedio=row[0]
                    cur=con.cursor()
                    cur.execute("update peliculas SET puntajePromedio=? where id_pelicula=?",(promedio,id))
                    con.commit()
                    cur = con.cursor()
                    con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                    cur = con.cursor()
                    cur.execute("SELECT * FROM peliculas WHERE id_pelicula=?",[id])
                    row_pelicula = cur.fetchone()
                    return render_template(ruta_detalle,rol=rol,row_pelicula=row_pelicula,id=id,row_comentarios=row_comentarios)
            except Error:
                print(Error)
        else:
            return "Debe iniciar sesion para poder comentar"
    return "Metodo erroneo"


@app.route("/eliminarComentario/<string:id_comentario>/<string:id_usuario>",methods=["GET","POST"])
def eliminarComentario(id_comentario=None,id_usuario=None):
    if "usuario" in session:
        try:
            with sqlite3.connect(ruta_db) as con: 
                con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute("SELECT * FROM usuarios WHERE id_usuario=?",[id_usuario])
                row_perfil = cur.fetchone()
                cur=con.cursor()
                cur.execute("SELECT rol FROM usuarios WHERE correo=?",[session["usuario"]])
                row = cur.fetchone()
                rol=row[0]
                cur = con.cursor()
                cur.execute("DELETE FROM comentarios Where id_comentario = ?",[id_comentario])


                con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute("SELECT * FROM comentarios WHERE usuario=?",[session["usuario"]])
                row_comentarios = cur.fetchall()
                return render_template(ruta_perfil,row_usuario=row_perfil,rol=rol,row_comentarios=row_comentarios)
        except Error:
            print(Error)

@app.route("/editarUsuario/<string:id>")
def editarUsuario(id=None):
    try:
        with sqlite3.connect(ruta_db) as con: 
            con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
            cur = con.cursor()
            cur.execute("SELECT * FROM usuarios WHERE id_usuario=?",[id])
            row_usuario = cur.fetchone()
            cur=con.cursor()
            cur.execute("SELECT rol from usuarios WHERE correo=?",[session["usuario"]])
            row=cur.fetchone()
            rol=row[0]
            return render_template(ruta_editarUsuario, row_usuario=row_usuario,id=row_usuario["id_usuario"],rol=rol)
    except Error:
            print(Error)

@app.route("/editarUsuario2/<string:id>", methods=["GET", "POST"])
def editarUsuario2(id=None):
    if request.method=="POST":
        try:
            with sqlite3.connect(ruta_db) as con: 
                nombre=escape(request.form["nombre"])
                apellidos=escape(request.form["apellidos"])
                documento=escape(request.form["cedula"])
                correo=escape(request.form["correo"])
                rol=escape(request.form["rol"])
                print("Guardo datos")
                cur=con.cursor()
                cur.execute("UPDATE usuarios SET nombre=?, apellidos=?, documento=?, correo=?, rol=? where id_usuario=?",(nombre,apellidos,documento,correo,rol,id))
                con.commit()
                con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute("SELECT * FROM usuarios WHERE id_usuario=?",[id])
                row_usuario = cur.fetchone()
                cur=con.cursor()
                cur.execute("SELECT rol from usuarios WHERE correo=?",[session["usuario"]])
                row=cur.fetchone()
                rol=row[0]
                return render_template(ruta_editarUsuario, row_usuario=row_usuario,rol=rol)
        except Error:
                print(Error)
    return "Error en el metodo"

@app.route("/editarFuncion/<string:id>")
def editarFuncion(id=None):
    try:
        with sqlite3.connect(ruta_db) as con: 
            con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
            cur = con.cursor()
            cur.execute("SELECT * FROM peliculas WHERE id_pelicula=?",[id])
            row_pelicula = cur.fetchone()
            cur=con.cursor()
            cur.execute("SELECT rol from usuarios WHERE correo=?",[session["usuario"]])
            row=cur.fetchone()
            rol=row[0]
            return render_template(ruta_editarFuncion, row_pelicula=row_pelicula,rol=rol)
    except Error:
            print(Error)

@app.route("/editarFuncion2/<string:id>", methods=["GET", "POST"])
def editarFuncion2(id=None):
    if request.method=="POST":
        try:
            with sqlite3.connect(ruta_db) as con:
                nombrePelicula=escape(request.form["titulo"])
                genero=escape(request.form["genero"])
                duracion=escape(request.form["duracion"])
                year=escape(request.form["year"])
                enCartelera=escape(request.form.get("activa"))
                if (enCartelera!="True"):
                    enCartelera="False"
                tiquetesTotales=escape(request.form["tiquetes"])
                tiquetesVendidos=escape(request.form["tiquetesVendidos"])

                poster=request.files["poster"]
                posterBinario= base64.b64encode(poster.read())
                posterBinario2=posterBinario.decode("utf-8") 
                cur=con.cursor()
                cur.execute("UPDATE peliculas SET nombrePelicula=?, genero=?, duracion=?, year=?, enCartelera=?, tiquetesTotales=?, tiquetesVendidos=?, poster=? where id_pelicula=?",(nombrePelicula,genero,duracion,year,enCartelera,tiquetesTotales,tiquetesVendidos,posterBinario2,id))
                con.commit()
                con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute("SELECT * FROM peliculas WHERE id_pelicula=?",[id])
                row_pelicula = cur.fetchone()
                cur=con.cursor()
                cur.execute("SELECT rol from usuarios WHERE correo=?",[session["usuario"]])
                row=cur.fetchone()
                rol=row[0]
                return render_template(ruta_editarFuncion, row_pelicula=row_pelicula,rol=rol)
        except Error:
                print(Error)
                return "Error al guardar en base de datos"
    else:
        return "Error en el metodo"

@app.route("/eliminarUsuario/<string:id>", methods=["GET","POST"])
def eliminarUsuario(id=None):
    try:
        with sqlite3.connect(ruta_db) as con:
            cur = con.cursor()
            cur.execute("DELETE FROM usuarios Where id_usuario = ?",[id])
            cur=con.cursor()
            cur.execute("SELECT rol FROM usuarios WHERE correo=?",[session["usuario"]])
            row = cur.fetchone()
            rol=row[0]
            con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
            cur = con.cursor()
            cur.execute("SELECT * FROM usuarios")
            row_usuarios = cur.fetchall()  
            cur=con.cursor()
            cur.execute("SELECT id_usuario FROM usuarios WHERE correo=?",[session["usuario"]])
            row=cur.fetchone()
            id=row[0]
            con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
            cur = con.cursor()
            cur.execute("SELECT * FROM peliculas")
            row_peliculas = cur.fetchall()  
            return render_template(ruta_dashboard,rol=rol,row_usuarios=row_usuarios,id=id,row_peliculas=row_peliculas)
    except Error:
                print(Error)
                return "Error al borrar en base de datos"

@app.route("/eliminarFuncion/<string:id>", methods=["GET","POST"])
def eliminarFuncion(id=None):
    try:
        with sqlite3.connect(ruta_db) as con:
            cur = con.cursor()
            cur.execute("DELETE FROM peliculas Where id_pelicula = ?",[id])
            cur=con.cursor()
            cur.execute("SELECT rol FROM usuarios WHERE correo=?",[session["usuario"]])
            row = cur.fetchone()
            rol=row[0]
            con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
            cur = con.cursor()
            cur.execute("SELECT * FROM usuarios")
            row_usuarios = cur.fetchall()  
            cur=con.cursor()
            cur.execute("SELECT id_usuario FROM usuarios WHERE correo=?",[session["usuario"]])
            row=cur.fetchone()
            id=row[0]
            con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
            cur = con.cursor()
            cur.execute("SELECT * FROM peliculas")
            row_peliculas = cur.fetchall()  
            return render_template(ruta_dashboard,rol=rol,row_usuarios=row_usuarios,id=id,row_peliculas=row_peliculas)
    except Error:
                print(Error)
                return "Error al borrar en base de datos"


@app.route("/agregarPelicula")
def agregarFuncion():
    try:
        with sqlite3.connect(ruta_db) as con:
            cur=con.cursor()
            cur.execute("SELECT rol FROM usuarios WHERE correo=?",[session["usuario"]])
            row = cur.fetchone()
            rol=row[0]
            return render_template(ruta_agregarFuncion,rol=rol)
    except Error:
            print(Error)
            
    return render_template(ruta_agregarFuncion)

@app.route("/agregarPelicula2",methods=["GET","POST"])
def agregarFuncion2():
    if request.method=="POST":
        try:
            with sqlite3.connect(ruta_db) as con:
                nombrePelicula=escape(request.form["titulo"])
                genero=escape(request.form["genero"])
                duracion=escape(request.form["duracion"])
                year=escape(request.form["year"])
                enCartelera=escape(request.form.get("activa"))
                if (enCartelera!="True"):
                    enCartelera="False"
                tiquetesTotales=escape(request.form["tiquetes"])
                tiquetesVendidos=escape(request.form["tiquetesVendidos"])

                poster=request.files["poster"]
                posterBinario= base64.b64encode(poster.read())
                posterBinario2=posterBinario.decode("utf-8") 
                cur=con.cursor()
                cur.execute("INSERT INTO peliculas (nombrePelicula,genero,duracion,year,enCartelera,tiquetesTotales,tiquetesVendidos,poster) VALUES (?,?,?,?,?,?,?,?)",(nombrePelicula,genero,duracion,year,enCartelera,tiquetesTotales,tiquetesVendidos,posterBinario2))
                con.commit()
                
                cur=con.cursor()
                cur.execute("SELECT rol FROM usuarios WHERE correo=?",[session["usuario"]])
                row = cur.fetchone()
                rol=row[0]
                con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute("SELECT * FROM usuarios")
                row_usuarios = cur.fetchall()  
                cur=con.cursor()
                cur.execute("SELECT id_usuario FROM usuarios WHERE correo=?",[session["usuario"]])
                row=cur.fetchone()
                id=row[0]
                con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute("SELECT * FROM peliculas")
                row_peliculas = cur.fetchall()  
                return render_template(ruta_dashboard,rol=rol,row_usuarios=row_usuarios,id=id,row_peliculas=row_peliculas)
        except Error:
                    print(Error)
                    return "Error al borrar en base de datos"


if __name__=="__main__":
    app.run(debug=True, port=8000)

