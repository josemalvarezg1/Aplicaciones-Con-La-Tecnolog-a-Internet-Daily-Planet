from flask import Flask, render_template, request, session, json
from pymongo import *
from werkzeug import secure_filename
from bson import BSON
from bson import json_util
import time
 
app = Flask(__name__, template_folder = 'templates', static_folder = 'static')
app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
# MongoDB Connection with PyMongo
client = MongoClient()

db = client.dailyplanet
users = db.users
comments = db.comments
posts = db.posts
username = ""
# Routes Definition
#Validar que exista una SESSION

@app.route('/')
def index():
	return render_template('articulosDeHoyNoSesion.html')

@app.route('/inicio')
def indexSesion():
	return render_template('articulosDeHoy.html', user = session['name'])

@app.route('/login', methods=['POST'])
def login():
	username = request.form['email']
	password  = request.form['pass']
	user = users.find_one({ "correo": username })
	#debe ser articulosDeHoyNoSesion con un param modal de datos invalidos
	if (user is None) or (len(user) == 0):
		return render_template('articulosDeHoyNoSesion.html', error = "true")
	if user["pass"] == password:
		session['name'] = username
		return render_template('articulosDeHoy.html', user = username)
	return render_template('articulosDeHoyNoSesion.html', error = "true")

@app.route('/logout')
def indexNoSesion():
	session.pop('name', None)
	return render_template('articulosDeHoyNoSesion.html')

@app.route('/create')
def create():
	return render_template('crearArticulo.html', user = session['name'])

@app.route('/crear', methods=['POST'])
def crear():
	username = session['name']
	titulo = request.form['titulo']
	resumen  = request.form['resumen']
	imagen = request.form['pic']
	clave = request.form['clave']
	contenido = request.form['contenido']
	user = users.find_one({ "correo": username })
	nombre = user["nombre"]
	apellido = user["apellido"]
	nombreCompleto = nombre+" "+apellido
	fechaPublic = time.strftime("%d/%m/%Y")
	posts.insert_one({"titulo": titulo, "resumen": resumen, "imagen": imagen, "clave": clave, "contenido": contenido, "nombre": nombreCompleto, "fecha": fechaPublic})
	return render_template('articulosDeHoy.html', user = session['name'], created = "true", titulo = titulo)

@app.route('/register', methods=['POST'])
def register():
	nombre = request.form['nombre']
	apellido  = request.form['apellido']
	correo = request.form['correo']
	fechaNac = request.form['fechaNac']
	avatar = request.form['avatar']
	#filename = secure_filename(avatar.filename)
	#avatar.save(os.path.join("hola/", filename))
	pais = request.form['pais']
	tipo = request.form['tipo']
	descripcion = request.form['descripcion']
	password = request.form['password1']
	users.insert_one({"nombre": nombre, "apellido": apellido, "correo": correo, "fechaNac": fechaNac, "avatar": avatar, "pais": pais, "tipo": tipo, "descripcion": descripcion, "pass": password})
	return render_template('articulosDeHoyNoSesion.html', reg = "true")

@app.route('/articulo', methods=['GET'])
def article():
	#Debo pasarle allComents y solo del articulo en donde estoy
	username = session['name']
	allComents = list(comments.find())
	return render_template('articuloX.html', user = username, allComents = json.dumps(allComents, default=json_util.default))

@app.route('/comment', methods=['POST'])
def comment():
	username = session['name']
	#Falta identificar el articulo en el que se comenta
	id_article = 1
	user = users.find_one({ "correo": username })
	nombre = user["nombre"]
	apellido = user["apellido"]
	nombreCompleto = nombre+" "+apellido
	fechaPublic = time.strftime("%d/%m/%Y")
	content = request.form.get('content')
	comments.insert_one({"id_article": id_article, "nombre": nombreCompleto, "fecha": fechaPublic, "contenido": content})
	#Debo pasarle allComents y solo del articulo en donde estoy
	allComents = list(comments.find())
	return render_template('articuloX.html', user = username, allComents = json.dumps(allComents, default=json_util.default))


if __name__ == '__main__':
	app.debug = True
	app.run()


