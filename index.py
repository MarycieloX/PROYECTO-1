from calendar import c
from re import A
from flask import Flask, render_template, request,flash,redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,DateField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
 
#Add Database local
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqldb://root@127.0.0.1:3308/proyectos"

#Database concectado a Amazon WS
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://Alex:Admin1234@44.202.81.95/examen"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['SECRET_KEY']='My super secret that no one is supposed to know'

#Initialize the Database
db =SQLAlchemy(app)

#Create Model LIBROS
class Autor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False) 
    regionNacimiento = db.Column(db.String(100))
    ranking= db.relationship('Ranking', backref='autor', lazy=True)
    def __init__(self,nombre,apellido,regionNacimiento):
        self.nombre = nombre
        self.apellido = apellido 
        self.regionNacimiento = regionNacimiento

class Libros(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genero = db.Column(db.String(100))
    titulo = db.Column(db.String(100))
    ranking= db.relationship('Ranking', backref='libros', lazy=True)
    def __init__(self, genero, titulo):
        self.genero = genero
        self.titulo = titulo

class Condulta1 (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    autor_c = db.Column(db.String(100))
    libro_c = db.Column(db.String(100))
    def __init__(self, autor_c, libro_c):
        self.autor_c = autor_c
        self.libro_c = libro_c

class Ranking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    autor_id=db.Column(db.Integer,db.ForeignKey('autor.id'),nullable=False)
    libros_id=db.Column(db.Integer,db.ForeignKey('libros.id'),nullable=False)

    def __init__(self,score, autor_id, libros_id):
        self.score = score
        self.autor_id = autor_id
        self.libros_id = libros_id

@app.route('/',methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/Autor',methods=['GET','POST'])
def AutorRegistro():
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    region = request.form["region"]
    autor = Autor(nombre, apellido, region)    
    db.session.add(autor)
    db.session.commit()
    return render_template('libros.html')
    
@app.route('/Auto')
def lib():
    return render_template('autor.html')

@app.route('/Libros', methods=['GET','POST'])
def LibrosRegistro():
    lista = Autor.query.all()
    consultas = Condulta1.query.all()
    if request.method == 'POST':
        genero = request.form["genero"]
        titulo = request.form["titulo"]
        libro = Libros(genero, titulo)   
        db.session.add(libro)
        db.session.commit()
        
        autor_id = request.form["autor_id"] 
        libros = Libros.query.all()
        for lib in libros:
            if lib.titulo == titulo:
                libros_id = lib.id

        print(libros)
        rank = Ranking(score=0, autor_id = autor_id, libros_id=libros_id)   
        db.session.add(rank)
        db.session.commit()

        autor2 = Autor.query.get(autor_id)
        autorn = autor2.nombre
        consulta1 = Condulta1(autorn, titulo)
        db.session.add(consulta1)
        db.session.commit()
        return render_template('ranking.html',consultas=consultas)
    return render_template('libros.html',lista=lista)

@app.route('/ranking')
def ranking():
    consultas=Condulta1.query.all()
    return render_template('ranking.html',consultas=consultas)

@app.route('/Votar/<titulo>', methods=['POST'])
def Votar(titulo):
    libro = Libros.query.filter_by(titulo=titulo).first()
    ranking = Ranking.query.filter_by(libros_id=libro.id).first()
    ranking.score += 1
    db.session.commit()
    return redirect(url_for('Votados'))

@app.route('/Votados')
def Votados():
    consultas=Condulta1.query.all()
    votados = Ranking.query.order_by(Ranking.score.desc()).all()
    lista = []
    for votos in votados:
        autor = Autor.query.filter_by(id=votos.autor_id ).first()
        lista.append({
            'score':votos.score,
            'autor':autor.nombre
        })
    return render_template('votados.html', consultas=lista)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)



