from flask import Flask
from flask import render_template, request, redirect, session 
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory  # nos permite obtener informacion de esta imagen 
import os


app=Flask(__name__)
app.secret_key='develoteca'

# Database etapa de conexcion con la db

mysql=MySQL()

app.config['MYSQL_DATABASE_HOST']       ='localhost'
app.config['MYSQL_DATABASE_USER']       ='root'
app.config['MYSQL_DATABASE_PASSWORD']   ='ange2964'
app.config['MYSQL_DATABASE_DB']         ='sitio'
mysql.init_app(app)


# Esta es la seccion del sitio

@app.route('/')
def inicio():
    return render_template('sitio/index.html')


@app.route('/img/<imagen>')
def imagenes(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/img'), imagen)


@app.route('/libros')
def libros():
    
     # Esta es la seccion permite la visualizacion de informacion de la db en la vista
    conexion=mysql.connect()                    # generamos la conexion
    cursor= conexion.cursor()                   # armamos un cursor
    cursor.execute("SELECT * FROM `libros`")    # para poder ejecutar la instruccion de seleccion sql
    libros = cursor.fetchall()                  # recuperamos todos los libros y los almacenamos en una variable
    conexion.commit()                           # se realisa la ejecucion de grabado
    print(libros) 
    
    return render_template('sitio/libros.html', libros=libros)


@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')

# Esta es la seccion de administracion

@app.route('/admin/')
def admin_index(): 
    if not 'login' in session:
        return redirect('/admin/login')
    
    
    return render_template('admin/index.html')


@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')


@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    _usuario = request.form['txtUsuario']
    _password = request.form['txtPassword']
    print(_usuario)
    print(_password)
    
    
    # lo que hace este if es preguntar si el usuario y el password son los correctos
    if _usuario=="admin" and _password=="123":  # validamos si ingreso un usuario y una clave
        session["login"]= True                  # creamos una variable de secionnque evaluara si existe un login
        session["usuario"]= "Administrador"     # en el usuario guardaremos el valor de administrador
        return redirect("/admin")               # redireccionamos al administrador
            
    return render_template('admin/login.html')


@app.route('/admin/cerrar')          # aca reccepcionamos los datos
def admin_login_cerrar():            # utilizamos la funcion
    session.clear()                  # limpiamo las variable de session
    return redirect('/admin/login')  # redirect nos envia al login


@app.route('/admin/libros')
def admin_libros():
    
    if not 'login' in session:
        return redirect('/admin/login')
    
    
    # Esta es la seccion permite la visualizacion de informacion de la db en la vista
    conexion=mysql.connect()                    # generamos la conexion
    cursor= conexion.cursor()                   # armamos un cursor
    cursor.execute("SELECT * FROM `libros`")    # para poder ejecutar la instruccion de seleccion sql
    libros = cursor.fetchall()                  # recuperamos todos los libros y los almacenamos en una variable
    conexion.commit()                           # se realisa la ejecucion de grabado
    print(libros)                               # permite ve la informacion recuperada en consola 
        
    return render_template('admin/libros.html', libros=libros)


@app.route('/admin/libros/guardar', methods=['POST']) # la informacion viene por esta url
def admin_libros_guardar():  # en esta linea guardamos la informacion
    
    _nombre=request.form['txtNombre']
    _url=request.form['txtUrl']
    _archivo=request.files['txtImagen']
    
    tiempo = datetime.now()
    horaActual = tiempo.strftime('%Y%H%M%S')
    
    if _archivo.filename!="":   # se ira a la carpeta img por que detectaveste nuevo arcvo
        nuevoNombre = horaActual+"_"+_archivo.filename  # le pone y respeta la hora en que se adjunta el archivo
        _archivo.save("templates/sitio/img/"+nuevoNombre)  # y se copia a la nueva ruta donde esta el nuevoArchivo
        
     
        
    # en estas lineas guardamos la informacion para la db    
    sql="INSERT INTO `libros` (`id`, `nombre`, `imagen`, `url`) VALUES (NULL, %s, %s, %s);"
    datos=(_nombre, nuevoNombre, _url)  # y se guarda en la db con ese mismo nombre
    
    
    
    
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)# con datos lo registrabos en la db
    conexion.commit()
    
    
    print(_nombre)
    print(_url)
    print(_archivo)
        
    return redirect('/admin/libros')


@app.route('/admin/libros/borrar', methods=['POST'])
def admin_libros_borrar(): # en esta linea guardamos la inform
    _id=request.form['txtID']
    print(_id)
    
    
    conexion=mysql.connect()                                        # generamos la conexion a la db
    cursor= conexion.cursor()                                       # armamos un cursor
    cursor.execute("SELECT imagen FROM `libros` WHERE id=%s", (_id))     # acá busca la imagen y la almacenamos en libros
    libro = cursor.fetchall()                                       # recuperamos todos los libros y los almacenamos en una variable
    conexion.commit()                                               # se realisa la ejecucion de 
    print(libro)                                                    # permite ve la informacion recuperada en consola 
    
    
    if os.path.exists('templates/sitio/img/'+str(libro[0][0])):     # pregunta si existe esa imagen
        os.unlink("templates/sitio/img/"+str(libro[0][0]))          # y si existe la borra 
    
    
    # Esta es la seccion nos permite eliminar los registros de la db
    conexion=mysql.connect()                                        # generamos la conexion a la db
    cursor= conexion.cursor()                                       # armamos un cursor
    cursor.execute("DELETE FROM libros WHERE id=%s", (_id))         # para poder ejecutar la instruccion de seleccion sql DELETE
    conexion.commit()                                               # se realisa la ejecucion de grabado

    return redirect('/admin/libros')





if __name__ == '__main__':
    app.run(debug=True)