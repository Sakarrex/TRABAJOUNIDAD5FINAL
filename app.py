
from flask import Flask, redirect,render_template,request, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, false, true
import hashlib
from Musuario import ClaseUsuario

__sesionactual = ClaseUsuario()
app = Flask(__name__)
app.config.from_pyfile('config.py')

from model import db
from model import Receta, Usuario, Ingrediente

@app.route('/')
def inicio():
    return render_template('Iniciar_Sesion.html')

@app.route('/validar',methods = ['POST','GET'])
def validar():
    if request.method=='POST':
        if request.form["email"] and request.form["password"]:
            UsuarioActual = Usuario.query.filter_by(correo = request.form["email"]).first()
            if UsuarioActual is None:
                return render_template('Iniciar_Sesion.html', usuario = False)
            else:
                clave_cifrada = hashlib.md5(bytes(request.form["password"],encoding = "utf-8"))
                if clave_cifrada.hexdigest()==UsuarioActual.clave:
                    __sesionactual.addusuario(UsuarioActual)
                    return render_template('Menu_Principal.html')
                else:
                    return render_template('Iniciar_Sesion.html', password = False)
        else:
            return render_template('Iniciar_Sesion.html')

@app.route('/menu')
def menu():
    return render_template('Menu_Principal.html')

@app.route('/compartir_receta',methods = ['GET','POST'])
def compartir_receta():
    if request.method == 'POST':
        nueva_receta = Receta(nombre=request.form['nombre'],tiempo=request.form['tiempo'] ,elaboracion=request.form['descripcion'],cantidadmegusta = 0,fecha = datetime.now(),usuarioid = __sesionactual.getUsuario().id)
        db.session.add(nueva_receta)
        db.session.commit()
        return render_template('ingresar_ingrediente.html',idreceta = nueva_receta.id,cantingredientes=0)
    else:
        return render_template('ingresar_receta.html')

@app.route('/ingresar_ingrediente/<int:idreceta>/<int:cant_ingredientes>',methods = ['GET','POST'])
def ingresar_ingrediente(idreceta, cant_ingredientes):
    if request.method=='POST':
        ingrediente = Ingrediente(nombre = request.form['Ingrediente'],cantidad=request.form['Cantidad'],unidad = request.form['Unidad'],recetaid = idreceta)
        db.session.add(ingrediente)
        db.session.commit()
        return render_template('ingresar_ingrediente.html',idreceta = idreceta,cantingredientes=cant_ingredientes+1)


@app.route('/guardar_receta/',methods = ['GET','POST']) 
def guardar_receta(idreceta,cant_ingredientes):
    if request.method == 'POST':
        if request.form['nombre'] and request.form['tiempo'] and request.form['descripcion']:
            i = 0
            bandera = true
            while bandera == true and i < cant_ingredientes:
                if request.form["Ingrediente"+str(i)] and request.form['Cantidad'+str(i)]:
                    ingrediente = Ingrediente(nombre = request.form['Ingrediente'+str(i)],cantidad = request.form['Cantidad'+str(i)], unidad = request.form['Unidad'+str(i)],recetaid = nueva_receta.id)
                    db.session.add(ingrediente)
                    db.session.commit()
                else:
                    bandera = false
                i+=1
            if bandera == false:
                return render_template('error.html',mensaje = 'Por favor ingresar todos los campos')
            else:
                return render_template('Menu_Principal.html')   





@app.route('/consultar_ranking',methods = ['GET','POST'])
def consultar():
    return render_template('ranking_recetas.html', recetas = Receta.query.order_by(desc(Receta.cantidadmegusta)).limit(5).all())

@app.route('/buscar_por_tiempo',methods = ['GET','POST'])
def buscar_por_tiempo():
    if request.method == 'POST':
        if request.form['tiempo']:
            return render_template('recetas_por_tiempo.html',tiempo = request.form['tiempo'], recetas = Receta.query.filter(Receta.tiempo < int(request.form['tiempo'])).all())
    else:
        return render_template('recetas_por_tiempo.html',tiempo = None,receta_seleccionada = None)

@app.route('/informacion_receta', methods=['POST','GET'])
def informacion_receta():
    if request.method == 'POST':
        return render_template('informacion_recetas.html',receta = Receta.query.get(request.form['recetas']),idusuario = __sesionactual.getUsuario().id)


@app.route('/megusta/<int:idreceta>',methods=['GET','POST'])
def megusta(idreceta):
    if request.method == 'POST':
        receta = Receta.query.get(idreceta)
        receta.cantidadmegusta += 1
        db.session.commit()
        return render_template('Menu_Principal.html') 

@app.route('/buscar_por_ingrediente',methods=['POST','GET'])
def buscar_por_ingrediente():
    if request.method == 'POST':
        if request.form['ingrediente']: 
            ingredientes = Ingrediente.query.filter(Ingrediente.nombre.like('%' + request.form['ingrediente'] + '%'))
            recetas = []
            for i in ingredientes:
                recetas.append(Receta.query.get(i.recetaid))
            return render_template('buscar_por_ingrediente.html',recetas = recetas,ingrediente = request.form['ingrediente'])
    else:
        return render_template('buscar_por_ingrediente.html',ingrediente = None)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)