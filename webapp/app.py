# We need to import request to access the details of the POST request
# and render_template, to render our templates (form and response)
# we'll use url_for to get some URLs for the app on the templates

from flask import Flask, render_template, request, url_for
import datetime
import json
import pymongo
from pymongo import MongoClient


client = MongoClient()
db = client.IOT
collection = db.eventos

"""ev1 = {"Nombre": "Evento 1",
       "Descripcion": "Descripcion 1",
       "Fecha": datetime.datetime.utcnow(),
       "Repeticion": "Diariamente",
       "Topico": "T1",
       "Valor": "Este es el evento 1"}
post_id = db.eventos.insert_one(ev1).inserted_id
ev2 = {"Nombre": "Evento 2",
       "Descripcion": "Descripcion 2",
       "Fecha": datetime.datetime.utcnow() + datetime.timedelta(weeks=1),
       "Repeticion": "Semanalmente",
       "Topico": "T2",
       "Valor": "Este es el evento 2"}
post_id = db.eventos.insert_one(ev2).inserted_id
ev3 = {"Nombre": "Evento 3",
       "Descricion": "Descripcion 3",
       "Fecha": datetime.datetime.utcnow() + datetime.timedelta(weeks=2),
       "Repeticion": "Mensualmente",
       "Topico": "T3",
       "Valor": "Este es el evento 3"}
post_id = db.eventos.insert_one(ev3).inserted_id"""
# Initialize the Flask application
app = Flask(__name__)

# Define a route for the default URL, which loads the form
@app.route('/')
def form():
    return render_template('form_submit.html')

# Define a route for the action of the form, for example '/hello/'
# We are also defining which type of requests this route is
# accepting: POST requests in this case
@app.route('/hello/', methods=['POST'])
def hello():
    Evento=request.form['Evento']
    Descripcion=request.form['Descripcion']
    Fecha=request.form['fecha']
    Hora=request.form['hora']
    Repeticion=request.form['Repeticion']
    date = datetime.datetime.strptime(Fecha + ' ' + Hora, '%Y-%m-%d %H:%M')
    evn = {"Evento": Evento,
           "Description": Descripcion,
           "Fecha": date,
           "Repeticion": Repeticion,
           "Topico": "T1",
           "Valor": "Esta es una publicacion MQTT"}
    post_id = db.eventos.insert_one(evn).inserted_id
    prox_ev = {"ev_id": post_id,
               "Fecha": date,
               "Repeticion": Repeticion
               }
    post_id = db.proximos_eventos.insert_one(prox_ev).inserted_id
    # print(post_id)
    return render_template('form_action.html', name=Evento, email=Descripcion)


def create_prox_event_list():
    collection1 = db.Prox_evento
    for post in db.eventos.find():
        ID_Evento = post["_id"]
        Fecha = post["Fecha"]
        Hora = post["Hora"]
        Repeticion = post["Repeticion"]
        prox_ev = { "ID_Evento": ID_Evento,
                    "Fecha": Fecha,
                    "Hora": Hora,
                    "Repeticion":Repeticion
                   }
        post_id = db.Prox_evento.insert_one(prox_ev).inserted_id
    return 1

# Run the app :)
if __name__ == '__main__':
#  create_prox_event_list()
  app.run(
        host="0.0.0.0",
        port=int("80"),
  )

