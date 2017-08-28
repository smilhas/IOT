# PARA QUE EL SIGUIENTE PROGRAMA FUNCIONE, HACE FALTA UN SERVIDOR MQTT QUE ESTE CORRIENDO EN LA IP ESPECIFICADA EN EL
# ARCHIVO DE CONFIGURACION, EN EL PUERTO CORRESPONDIENTE Y UNA BASE DE DATOS DONDE SE GUARDARAN UNA SERIE DE EVENTOS
# QUE SE QUIERAN EJECUTAR.

# ESTE PROGRAMA ES UN SCHEDULER, SE ENCARGA DE LLEVAR A CABO LA EJECUCIÓN DE LOS EVENTOS QUE ESTAN GURADADOS EN LA
# BASE DE DATOS, LA BASE DE DATOS QUE SE UTILIZA PARA EL ALMACENAMIENTO DE LOS EVENTOS ES MONGODB, LA INTERACCIÓN
# QUE REALIZA CON LA MISMA SE EXPLICA JUNTO AL CÓDIGO. PARA EL ALMACENAMIENTO DE CADA EVENTO, UTILIZANDO LOS TERMINOS
# DE MONGODB, SE UTILIZA UN DOCUMENTO, LUEGO EL CONJUNTO DE DOCUMENTOS (CADA UNO HACIENDO REFERENCIA A UN EVENTO
# DISTINTO), FORMA LO QUE SE LLAMA UNA COLECCIÓN. CADA DOCUMETNO QUE REPRESENTE UN EVENTO TENDRA UNA ID, UN NOMBRE,
# UN HORARIO EN EL QUE DEBE SER EJECUTADO, UNA DESCRIPCIÓN, UN TÓPICO (HACIENDO REFERENCIA A EL PROTOCOLO MQTT),
# Y UN VALOR. LA EJECUCIÓN DE CADA UNO DE LOS EVENTOS CONSISTE EN UNA PUBLICACIÓN MQTT DEL VALOR QUE SE INDIQUE EN EL
# DOCUMENTO DEL EVENTO, AL TÓPICO DE ESTE  Y EN EL HORARIO QUE SE ESPECIFIQUE. EL SERVIDOR QUE SE UTILIZA PARA EL
# MANEJO DEL PROTOCOLO MQTT, ES MOSQUITTO.

#Para empezar se realiza un 'import' de las librerias que se van a utilizar.

# 'time' y 'datetime' se utilizan para manejar los horarios en los que se ejecutan los eventos
import time
import datetime
# 'configparser' se utiliza para la lectura del archivo de configuración
import configparser
# 'logging' es para el logeo del programa
import logging
# 'mqtt' es para conectarse al servidor mqtt y manejar las publicaciones del mismo
import paho.mqtt.client as mqtt
# 'pymongo' es para el manejo de la base de datos
from pymongo import MongoClient
import pymongo

#import mysql.connector
#vfrom mysql.connector import errorcode




class Scheduler:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('scheduler.conf')
        self.poolTime = self.config['Parameters'].getint('pool time')
        self.MQTTpoolTime = 0
        self.loglevel = self.config['Log']['log level']
        self.numericLevel = getattr(logging, self.loglevel.upper(), None)
        logging.basicConfig(filename='sceduler.log',
                            level=self.numericLevel,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('scheduler_logger')
        self.logger.info('Initializing...')
        self.MQTTev = False
        self.topicos = []
        self.valores = []
        self.mqttc = mqtt.Client()
        self.__update()

    def update(self):
        self.logger.info('Synchronizing with MongoDB...')
        client = MongoClient()

        db = client.IOT
        eventos = db.eventos
        proximos_eventos = db.proximos_eventos
        # try:
        #     cnx = mysql.connector.connect(user=self.config['MySQL']['login user'],
        #                                   password=self.config['MySQL']['password'],
        #                                   database='magia')
        #
        # except mysql.connector.Error as err:
        #     if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        #         self.logger.error('Something is wrong with your user name or password')
        #     elif err.errno == errorcode.ER_BAD_DB_ERROR:
        #         self.logger.error('Database does not exist')
        #     else:
        #         self.logger.error(err)

        # else:

        self.logger.info('Connection established with Mongo server, DB successfully reached')
        min_date = proximos_eventos.find_one(sort=[("Fecha", 1)])["Fecha"]

        try:
            min_date = proximos_eventos.find_one(sort=[("Fecha", 1)])["Fecha"]
            if datetime.datetime.today() >= min_date:
                self.MQTTev = True
                for prox_ev_docs in proximos_eventos.find({"Fecha": {"$lte": datetime.datetime.today()}}):
                    try:
                        ev_doc = eventos.find_one({"_id": prox_ev_docs['ev_id']})
                        self.topicos.append(ev_doc['Topico'])
                        self.valores.append(ev_doc['Valor'])
                        if ev_doc['Repeticion'] == "Diariamente":
                            date = prox_ev_docs['Fecha'] + datetime.timedelta(days=1)
                            proximos_eventos.update_one({"ev_id": prox_ev_docs['ev_id']}, {"$set": {"Fecha": date}})
                        elif ev_doc['Repeticion'] == "Semanalmente":
                            date = prox_ev_docs['Fecha'] + datetime.timedelta(weeks=1)
                            proximos_eventos.update_one({"ev_id": prox_ev_docs['ev_id']}, {"$set": {"Fecha": date}})
                        elif ev_doc['Repeticion'] == "Mensualmente":
                            date = prox_ev_docs['Fecha'] + datetime.timedelta(months=1)
                            proximos_eventos.update_one({"ev_id": prox_ev_docs['ev_id']}, {"$set": {"Fecha": date}})
                        elif ev_doc['Repeticion'] == "Nunca":
                            proximos_eventos.remove({"ev_id": prox_ev_docs['ev_id']})
                        else:
                            self.logger.error('Event format in MONGODB is not correct')
                    except:
                        self.logger.error('Hay un problema con la coleccion eventos en la base de datos IOT')

                    min_date = proximos_eventos.find_one(sort=[("Fecha", 1)])["Fecha"]
                    if (min_date - datetime.datetime.today()) < datetime.timedelta(second=self.poolTime):
                        timedif = min_date - datetime.datetime.today()
                        self.MQTTpoolTime = timedif.seconds
            elif (min_date - datetime.datetime.today()) < datetime.timedelta(second=self.poolTime):
                timedif = min_date - datetime.datetime.today()
                self.MQTTpoolTime = timedif.seconds
            else:
                self.logger.info('El proximo evento se ejecutara en un tiempo mayor al pooTime determinado')

        except:
            self.logger.error('Hay un problema con la coleccion proximos_eventos en la base de datos IOT')

        # Creo un buffered cursor debido a que no me permitia no especificar el tipo, ademas este es el que mejor
        # se ajusta a mis necesidades
        # cursor = cnx.cursor(buffered=True)
        # query = "SELECT GRIFINDOR, HUFELPAFF FROM hogwartz"
        # cursor.execute(query)

        # ACA TENGO QUE LEER LAS TABLAS Y ACTUALIZAR SELF.POOLTIME Y MQTTEV

        self.logger.info('Tables correctly read and events successfully updated')
        client.close()
        # cursor.close()
        # cnx.close()

    def scheduler_loop(self):
        while True:
            if self.MQTTev:
                self.logger.info('There are MQTT events to run')
                self.mqttc.connect('sebasmilhas')
                for index in range(len(self.topicos)):
                    self.mqttc.publish(topic=self.topicos[index], payload=self.valores[index])
                self.topicos.clear()
                self.valores.clear()
                self.mqttc.disconnect()
                self.MQTTev = False
                self.logger.info('MQTT events successfully executed')
            elif self.MQTTpoolTime > 0:
                self.logger.info('No MQTT to run, next run it will publish')
                time.sleep(self.MQTTpoolTime)
                self.MQTTpoolTime = 0
            else:
                self.logger.info('No MQTT to run')
                time.sleep(self.poolTime)
            self.update()



    __update = update

walter = Scheduler()
walter.scheduler_loop()
