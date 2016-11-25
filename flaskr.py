from flask import Flask, render_template, request, session, json
from pymongo import *
from werkzeug import secure_filename
from bson import BSON
from bson import json_util
from bson.objectid import ObjectId
import time
import os
 
app = Flask(__name__, template_folder = 'templates', static_folder = 'static')
app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
app.config['UPLOAD_FOLDER'] = 'static/imagenes/'
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
	fechaPublic = time.strftime("%d/%m/%Y")
	todaysPosts = list(posts.find({"fecha": fechaPublic, "publicado": 1}))
	return render_template('articulosDeHoyNoSesion.html', todaysPosts = json.dumps(todaysPosts, default=json_util.default))

@app.route('/inicio')
def indexSesion():
	allPosts = list(posts.find({"publicado": 1}))
	return render_template('articulosDeHoy.html', allPosts = json.dumps(allPosts, default=json_util.default))

@app.route('/login', methods=['POST'])
def login():
	username = request.form['email']
	password  = request.form['pass']
	user = users.find_one({ "correo": username })
	fechaPublic = time.strftime("%d/%m/%Y")
	todaysPosts = list(posts.find({"fecha": fechaPublic, "publicado": 1}))
	allPosts = list(posts.find({"publicado": 1}))
	if (user is None) or (len(user) == 0):
		return render_template('articulosDeHoyNoSesion.html', error = "true", todaysPosts = json.dumps(todaysPosts, default=json_util.default))
	if user["pass"] == password:
		session['name'] = username
		return render_template('articulosDeHoy.html', user = username, allPosts = json.dumps(allPosts, default=json_util.default))
	return render_template('articulosDeHoyNoSesion.html', error = "true", todaysPosts = json.dumps(todaysPosts, default=json_util.default))

@app.route('/logout')
def indexNoSesion():
	session.pop('name', None)
	fechaPublic = time.strftime("%d/%m/%Y")
	todaysPosts = list(posts.find({"fecha": fechaPublic, "publicado": 1}))
	return render_template('articulosDeHoyNoSesion.html', todaysPosts = json.dumps(todaysPosts, default=json_util.default))

@app.route('/create')
def create():
	return render_template('crearArticulo.html', user = session['name'])

@app.route('/draft')
def draft():
	username = session['name']
	user = users.find_one({ "correo": username })
	nombre = user["nombre"]
	apellido = user["apellido"]
	nombreCompleto = nombre+" "+apellido
	draftPosts = list(posts.find({"nombre": nombreCompleto, "publicado": 0}))
	return render_template('articulosPorPublicar.html', user = session['name'], draftPosts = json.dumps(draftPosts, default=json_util.default))

@app.route('/publish')
def publish():
	username = session['name']
	user = users.find_one({ "correo": username })
	nombre = user["nombre"]
	apellido = user["apellido"]
	nombreCompleto = nombre+" "+apellido
	posts.update_one({"_id": ObjectId(request.args.get('id'))}, {"$set": {"publicado": 1}}, upsert=False)
	postUpdateado = posts.find_one({ "_id": ObjectId(request.args.get('id'))})
	titulo = postUpdateado["titulo"]
	draftPosts = list(posts.find({"nombre": nombreCompleto, "publicado": 0}))
	return render_template('articulosPorPublicar.html', user = session['name'], published = "true", titulo = titulo, draftPosts = json.dumps(draftPosts, default=json_util.default))

@app.route('/delete')
def delete():
	username = session['name']
	user = users.find_one({ "correo": username })
	nombre = user["nombre"]
	apellido = user["apellido"]
	nombreCompleto = nombre+" "+apellido
	postEliminado = posts.find_one({ "_id": ObjectId(request.args.get('id'))})
	posts.remove({"_id": ObjectId(request.args.get('id'))})
	titulo = postEliminado["titulo"]
	draftPosts = list(posts.find({"nombre": nombreCompleto, "publicado": 0}))
	return render_template('articulosPorPublicar.html', user = session['name'], deleted = "true", titulo = titulo, draftPosts = json.dumps(draftPosts, default=json_util.default))

@app.route('/edit')
def edit():
	username = session['name']
	user = users.find_one({ "correo": username })
	nombre = user["nombre"]
	apellido = user["apellido"]
	nombreCompleto = nombre+" "+apellido
	post = posts.find_one({"_id": ObjectId(request.args.get('id'))})
	titulo = post["titulo"]
	resumen = post["resumen"]
	imagen = post["imagen"]
	clave = post["clave"]
	contenido = post["contenido"]
	return render_template('editarArticulo.html', user = session['name'], titulo = titulo, resumen = resumen, imagen = imagen, clave = clave, contenido = contenido)

@app.route('/editar', methods=['POST'])
def editar():
	username = session['name']
	user = users.find_one({ "correo": username })
	nombre = user["nombre"]
	apellido = user["apellido"]
	nombreCompleto = nombre+" "+apellido
	titulo = request.form.get('titulo')
	resumen = request.form.get('resumen')
	imagen = request.form.get('pic')
	clave = request.form.get('clave')
	contenido = request.form.get('contenido')
	posts.update_one({"_id": ObjectId(request.form.get('id_post'))}, {"$set": {"titulo": titulo, "resumen": resumen, "imagen": imagen, "clave": clave, "contenido": contenido}}, upsert=False)
	postUpdateado = posts.find_one({ "_id": ObjectId(request.form.get('id_post'))})
	titulo = postUpdateado["titulo"]
	draftPosts = list(posts.find({"nombre": nombreCompleto, "publicado": 0}))
	return render_template('articulosPorPublicar.html', user = session['name'], edited = "true", titulo = titulo, draftPosts = json.dumps(draftPosts, default=json_util.default))

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
	publicado = 0
	posts.insert_one({"titulo": titulo, "resumen": resumen, "imagen": imagen, "clave": clave, "contenido": contenido, "nombre": nombreCompleto, "fecha": fechaPublic, "publicado": publicado})
	draftPosts = list(posts.find({"nombre": nombreCompleto, "publicado": 0}))
	return render_template('articulosPorPublicar.html', user = session['name'], created = "true", draftPosts = json.dumps(draftPosts, default=json_util.default))

@app.route('/register', methods=['POST'])
def register():
	nombre = request.form.get('nombre')
	apellido  = request.form.get('apellido')
	correo = request.form.get('correo')
	fechaNac = request.form.get('fechaNac')
	file = request.files['avatar']
	if file:
		filename = secure_filename(file.filename)
		avatar = filename
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	pais = request.form.get('pais')
	tipo = request.form.get('tipo')
	descripcion = request.form.get('descripcion')
	password = request.form.get('password1')
	fechaPublic = time.strftime("%d/%m/%Y")
	todaysPosts = list(posts.find({"fecha": fechaPublic, "publicado": 1}))
	users.insert_one({"nombre": nombre, "apellido": apellido, "correo": correo, "fechaNac": fechaNac, "avatar": avatar, "pais": pais, "tipo": tipo, "descripcion": descripcion, "pass": password})
	return render_template('articulosDeHoyNoSesion.html', reg = "true", todaysPosts = json.dumps(todaysPosts, default=json_util.default))

@app.route('/articulo', methods=['GET'])
def article():
	username = session['name']
	articulo = posts.find_one({ "_id": ObjectId(request.args.get('id'))})
	titulo = articulo["titulo"]
	nombre = articulo["nombre"]
	editores = "Alvarez, Rodriguez"
	fechaPublic = articulo["fecha"]
	resumen = articulo["resumen"]
	contenido = articulo["contenido"]
	#Debo pasarle allComents solo del articulo en donde estoy
	allComents = list(comments.find({"id_article": articulo}))
	return render_template('articuloX.html', user = username, titulo = titulo, id_article = request.args.get('id'), nombre = nombre, editores = editores, fecha = fechaPublic, resumen = resumen, contenido = contenido, allComents = json.dumps(allComents, default=json_util.default))

@app.route('/articuloNS', methods=['GET'])
def articleNS():
	#Debo pasarle allComents y solo del articulo en donde estoy
	allComents = list(comments.find())
	articulo = posts.find_one({ "_id": ObjectId(request.args.get('id'))})
	titulo = articulo["titulo"]
	nombre = articulo["nombre"]
	editores = "Alvarez, Rodriguez"
	fechaPublic = articulo["fecha"]
	resumen = articulo["resumen"]
	contenido = articulo["contenido"]
	#Debo pasarle allComents solo del articulo en donde estoy
	allComents = list(comments.find())
	return render_template('articuloXNoSesion.html', user = "false", titulo = titulo, nombre = nombre, editores = editores, fecha = fechaPublic, resumen = resumen, contenido = contenido, allComents = json.dumps(allComents, default=json_util.default))

@app.route('/comment', methods=['POST'])
def comment():
	username = session['name']
	#Falta identificar el articulo en el que se comenta
	articulo = posts.find_one({ "_id": ObjectId(request.args.get('id'))})
	user = users.find_one({ "correo": username })
	nombre = user["nombre"]
	apellido = user["apellido"]
	nombreCompleto = nombre+" "+apellido
	fechaPublic = time.strftime("%d/%m/%Y")
	content = request.form.get('content')
	comments.insert_one({"id_article": articulo, "nombre": nombreCompleto, "fecha": fechaPublic, "contenido": content})
	#Debo pasarle allComents y solo del articulo en donde estoy
	allComents = list(comments.find({"id_article": articulo}))
	return render_template('articuloX.html', user = username, id_article = request.args.get('id'), allComents = json.dumps(allComents, default=json_util.default))

@app.route('/profile')
def profile():
	username = session['name']
	user = users.find_one({ "correo": username })
	nombre = user["nombre"]
	apellido = user["apellido"]
	correo = user['correo']
	fechaNac = user['fechaNac']
	avatar = user['avatar']
	pais = user['pais']
	tipo = user['tipo']
	descripcion = user['descripcion']
	password = user['pass']
	return render_template('editarPerfil.html', nombre = nombre, apellido = apellido, correo = correo, fechaNac = fechaNac, avatar = avatar, pais = pais, tipo = tipo, descripcion = descripcion, password = password)

@app.route('/updateProfile', methods=['POST'])
def updateProfile():
	username = session['name']
	nombre = request.form.get('nombre')
	apellido  = request.form.get('apellido')
	correo = request.form.get('correo')
	fechaNac = request.form.get('fechaNac')
	file = request.files['pic']
	if file:
		filename = secure_filename(file.filename)
		avatar = filename
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	pais = request.form.get('pais')
	descripcion = request.form.get('descripcion')
	password = request.form.get('password2')
	users.update_one({"correo": username}, {"$set": {"nombre": nombre, "apellido": apellido, "correo": correo, "fechaNac": fechaNac, "avatar": avatar, "pais": pais, "descripcion": descripcion, "pass": password}}, upsert=False)
	session['name'] = correo
	username = session['name']
	user = users.find_one({ "correo": username })
	nombre = user["nombre"]
	apellido = user["apellido"]
	correo = user['correo']
	fechaNac = user['fechaNac']
	avatar = user['avatar']
	pais = user['pais']
	tipo = user['tipo']
	descripcion = user['descripcion']
	password = user['pass']
	return render_template('editarPerfil.html', updated = "true", nombre = nombre, apellido = apellido, correo = correo, fechaNac = fechaNac, avatar = avatar, pais = pais, tipo = tipo, descripcion = descripcion, password = password)

if __name__ == '__main__':
	app.debug = True
	app.run()


