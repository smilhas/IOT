# We need to import request to access the details of the POST request
# and render_template, to render our templates (form and response)
# we'll use url_for to get some URLs for the app on the templates
from flask import Flask, render_template, request, url_for

from datetime import datetime, date, time

import json
import pymongo
from pymongo import MongoClient

"""
ev1 = {"Evento": "Evento 1",
       "Description": "Descripcion 1",
       "Fecha" : "2017-07-10",
       "Hora" : "12:30:00",
       "Repeticion": "Diariamente",
       "Topico": "T1"}
post_id = db.eventos.insert_one(ev1).inserted_id
ev2 = {"Evento": "Evento 2",
       "Description": "Descripcion 2",
       "Fecha" : "2017-07-10",
       "Hora" : "13:30:00",
       "Repeticion": "Semanalmente",
       "Topico": "T2"}
post_id = db.eventos.insert_one(ev2).inserted_id
ev3 = {"Evento": "Evento 3",
       "Description": "Descripcion 3",
       "Fecha" : "2017-07-10",
       "Hora" : "14:30:00",
       "Repeticion": "Mensualmente",
       "Topico": "T3"}
post_id = db.eventos.insert_one(ev3).inserted_id
"""

client = MongoClient()
db = client.IOT
collection = db.eventos

# Initialize the Flask application
app = Flask(__name__)


def create_data_array():
    index = 0
    for post in db.eventos.find():
        index = index + 1;
    arr = [[0 for j in range(7)] for i in range(index)]
    index = 0
    for post in db.eventos.find():
        arr[index][0] = post["Evento"]
        arr[index][1] = post["Description"]
        arr[index][2] = post["Fecha"]
        arr[index][3] = post["Hora"]
        arr[index][4] = post["Repeticion"]
        arr[index][5] = post["Topico"]
        arr[index][6] = post["Valor"]
        index = index + 1
    return arr;

def create_data_array_3():
    index = 0
    for post in db.eventos.find():
        index = index + 1;
    arr = [[0 for j in range(6)] for i in range(index)]
    index = 0
    for post in db.eventos.find():
        arr[index][0] = post["Evento"]
        arr[index][1] = post["Fecha"]
        arr[index][2] = post["Hora"]
        arr[index][3] = post["Repeticion"]
        arr[index][4] = post["Topico"]
        arr[index][5] = post["Valor"]
        index = index + 1
    return arr;

def create_data_array_2():
    arr = []
    for post in db.eventos.find():
        arr.append(post["Evento"])
    return arr;
# Define a route for the default URL, which loads the form

def delete_from_db(id_2_delete):
    db.eventos.remove({"Evento" : id_2_delete})
    db.Prox_evento.remove(({"Evento" : id_2_delete}))




@app.route('/')
def form():
    return render_template('Pag Principal.html', input=create_data_array(), input_ev=create_data_array_2(),
                           input_pe=create_data_array_3())


@app.route('/agregar_evento', methods = ['GET','POST'])
def add_ev():
    if request.method == 'GET':
        return render_template('Agregar evento.html')
    if request.method == 'POST':
        Evento = request.form['Evento']
        Descripcion = request.form['Descripcion']
        Fecha = request.form['fecha']
        Hora = request.form['hora']
        Repeticion = request.form['Repeticion']
        Topico = request.form['Topico']
        Valor = request.form['Valor']
        evn = {"Evento": Evento,
               "Description": Descripcion,
               "Fecha": Fecha,
               "Hora": Hora,
               "Repeticion": Repeticion,
               "Topico": Topico,
               "Valor" : Valor
               }

        post_id = db.eventos.insert_one(evn).inserted_id
        prox_ev = {"Evento": Evento,
                   "ID_Evento": post_id,
                   "Fecha": Fecha,
                   "Hora": Hora,
                   "Repeticion": Repeticion,
                   "Topico": Topico,
                   "Valor": Valor
                   }
        post_id = db.Prox_evento.insert_one(prox_ev).inserted_id
        print(post_id)
        return render_template('Pag Principal.html', input=create_data_array(), input_ev=create_data_array_2(), input_pe=create_data_array_3())

@app.route('/borrar_ev', methods=['GET', 'POST'])
def del_ev():
    if request.method == 'GET':
        id_2_delete = request.args['id']
        delete_from_db(id_2_delete);
        return render_template('Pag Principal.html', input=create_data_array(), input_ev=create_data_array_2(), input_pe=create_data_array_3())

@app.route('/mod_ev', methods=['GET', 'POST'])
def mod_ev():
    id_2_mod = request.args['id']
    if request.method == 'GET':
        for post in db.eventos.find():
            if post["Evento"] == id_2_mod:
                Evento = post["Evento"]
                Descripcion = post["Description"]
                Fecha = post["Fecha"]
                Hora = post["Hora"]
                Repeticion = post["Repeticion"]
                Topico = post["Topico"]
                Valor = post["Valor"]
        return render_template('Modificar evento.html', nombre_ev=Evento, desc=Descripcion, fecha=Fecha, hora=Hora, repe=Repeticion, topico=Topico, valor=Valor)
    if request.method == 'POST':
        db.eventos.update_one({"Evento" : id_2_mod},{"$set" : {
            "Evento": request.form['Evento'],
            "Description": request.form['Descripcion'],
            "Fecha": request.form['fecha'],
            "Hora": request.form['hora'],
            "Repeticion": request.form['Repeticion'],
            "Topico": request.form['Topico'],
            "Valor": request.form['Valor']}})
        db.Prox_evento.insert_one({
            "Evento": request.form['Evento'],
            "Fecha": request.form['fecha'],
            "Hora": request.form['hora'],
            "Repeticion": request.form['Repeticion'],
            "Topico": request.form['Topico'],
            "Valor": request.form['Valor']
        })
        db.Prox_evento.remove(({"Evento": id_2_mod}))

    return render_template('Pag Principal.html', input=create_data_array(), input_ev=create_data_array_2(),
                           input_pe=create_data_array_3())


#@app.route('/enviar_evento', methods = ['GET','POST'])
#def enviar_ev():
# Define a route for the action of the form, for example '/hello/'
# We are also defining which type of requests this route is
# accepting: POST requests in this case
@app.route('/hello/', methods=['GET','POST'])
def hello():
    return render_template('Agregar evento.html')


def create_prox_event_list():
    db.Prox_evento.remove({})
    for post in db.eventos.find():
        Evento = post["Evento"]
        Fecha = post["Fecha"]
        Hora = post["Hora"]
        Repeticion = post["Repeticion"]
        Topico = post["Topico"]
        Valor = post["Valor"]

        prox_ev = {
                    "Evento" : Evento,
                    "Fecha": Fecha,
                    "Hora": Hora,
                    "Repeticion":Repeticion,
                    "Topico" : Topico,
                    "Valor" : Valor
                   }
        post_id = db.Prox_evento.insert_one(prox_ev).inserted_id
    return 1
    #    post_id = db.eventos.insert_one(ev3).inserted_id

    return 1

# Run the app :)
if __name__ == '__main__':
    create_prox_event_list()
    app.run(
    host="0.0.0.0",
    port=int("80"),
    )











"""
    Evento=request.form['Evento']
    Descripcion=request.form['Descripcion']
    Fecha=request.form['fecha']
    Hora=request.form['hora']
    Repeticion=request.form['Repeticion']
    evn = {"Evento": Evento,
           "Description": Descripcion,
           "Fecha": Fecha,
           "Hora" : Hora,
           "Repeticion": Repeticion,
           "Topico": "T1"}
    post_id = db.eventos.insert_one(evn).inserted_id
    prox_ev = {"ID_Evento": post_id,
               "Fecha": Fecha,
               "Hora": Hora,
               "Repeticion": Repeticion
               }
    post_id = db.Prox_evento.insert_one(prox_ev).inserted_id
    print(post_id)
"""