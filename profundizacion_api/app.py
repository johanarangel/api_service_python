#!/usr/bin/env python


__author__ = "Inove Coding School"
__email__ = "INFO@INOVE.COM.AR"
__version__ = "1.1"

# Realizar HTTP POST --> post.py

import traceback
import io
import sys
import os
import base64
import json
import sqlite3
from datetime import datetime, timedelta
import requests

import numpy as np
from flask import Flask, request, jsonify, render_template, Response, redirect
import matplotlib
matplotlib.use('Agg')   # Para multi-thread, non-interactive backend (avoid run in main loop)
import matplotlib.pyplot as plt
# Para convertir matplotlib a imagen y luego a datos binarios
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.image as mpimg

import title
from config import config


# Crear el server Flask
app = Flask(__name__)

# Obtener la path de ejecución actual del script
script_path = os.path.dirname(os.path.realpath(__file__))

# Obtener los parámetros del archivo de configuración
config_path_name = os.path.join(script_path, 'config.ini')
db = config('db', config_path_name)
server = config('server', config_path_name)

# Enviar los datos de config de la DB
title.db = db

@app.route("/")
def index():
    try:
        # Imprimir los distintos endopoints disponibles
        result = "<h1>Bienvenido!!</h1>"
        result += "<h2>Endpoints disponibles:</h2>"
        result += "<h3>[GET] /reset --> borrar y crear la base de datos</h3>"
        result += "<h3>[POST] /registro --> se completa la base de datos con el json request proveniente de la URL</h3>"
        result += "<h3>[GET] /user?limit=[]&offset=[] --> mostrar la informaciónregistradas</h3>"
        result += "<h3>[GET] /user/{id}/titles--> muestra cuántos titulos completó el usuario cuyo id es el pasado como parámetro</h3>"
        result += "<h3>[GET] /user/graph --> comparativa de cuántos títulos completó cada usuario en un gráfico</h3>"
        result += "<h3>[GET] /user/table --> mostrar cuántos títulos completó cada usuario en una tabla HTML</h3>"
        return(result)
    except:
        return jsonify({'trace': traceback.format_exc()})

@app.route("/reset")
def reset():
    try:
        # Borrar y crear la base de datos
        title.create_schema()
        result = "<h3>Base de datos re-generada!</h3>"
        return (result)
    except:
        return jsonify({'trace': traceback.format_exc()})

@app.route("/registro", methods=['POST'])
def registro():
    if request.method == 'POST':
        # Obtener del HTTP POST JSON el nombre y los pulsos
        
        usuario_userId = str(request.form.get('userId')) #Acá los datos deben entrar en str para poder llenar de lo contrario no me funciona.
        usuario_title = str(request.form.get('title'))
        completado = str(request.form.get('completed'))

        if(usuario_title is None or usuario_userId is None or completado is None):
            # Datos ingresados incorrectos
            return Response(status=400)
        else:
            title.fill(usuario_userId, usuario_title, completado)
            return Response(status=200)

@app.route("/user")
def user():
    try:
        # Mostrar todos los registros en formato JSON
        result = show()
        return (result)
    except:
        return jsonify({'trace': traceback.format_exc()})

@app.route("/user/<id>/titles")
def user_titles(id):
    try:
        result = "<h1>Títulos completados por el usuario!!</h1>"
        total_completed, usuario = title.title_completed_count(id)
        result += "<h2>Usuario consultado por id N°:" + str(usuario) + "</h2>" 
        result += "<h2>Cantidad de titulos completados:" + str(total_completed) + "</h2>"      
        return (result)

    except:
        return jsonify({'trace': traceback.format_exc()})

@app.route("/user/graph")
def comparativa():
    
    try:
        title_completed, user_id = title.comparacion_user()
      
        fig, ax = plt.subplots(figsize=(16, 9))
        fig.suptitle('"Gráfico comparativo: titulos completados por usuario"', fontsize=18)
    
        ax.bar(user_id, title_completed, color='darkcyan')
        ax.set_facecolor('mintcream')
        ax.set_xlabel('Usuarios', fontsize=15)
        ax.set_ylabel('Cantidad de titulos completados', fontsize=15)
        ax.get_xaxis().set_visible(True)

    # Convertir ese grafico en una imagen para enviar por HTTP
        # y mostrar en el HTML
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        plt.close(fig)  # Cerramos la imagen para que no consuma memoria del sistema
        return Response(output.getvalue(), mimetype='image/png')
    except:
        return jsonify({'trace': traceback.format_exc()})

@app.route("/user/table")
def tabla_comparativa():

    try:
        #result = "<h1>Tabla comparativa sobre cantidad de títulos completados por usuario!</h1>"
        #data_completed, data_id = title.comparacion()
        data = title.comparacion()
        return html_table(data)
       
    except:
        return jsonify({'trace': traceback.format_exc()})


def show(show_type='json'):

    # Obtener de la query string los valores de limit y offset
    limit_str = str(request.args.get('limit'))
    offset_str = str(request.args.get('offset'))

    limit = 0
    offset = 0

    if(limit_str is not None) and (limit_str.isdigit()):
        limit = int(limit_str)

    if(offset_str is not None) and (offset_str.isdigit()):
        offset = int(offset_str)

    if show_type == 'json':
        data = title.report(limit=limit, offset=offset, dict_format=True)
        return jsonify(data)

def html_table(data):

    # Tabla HTML, header y formato
    result = '<table border="1">'
    result += '<thead cellpadding="1.0" cellspacing="1.0">'
    result += '<tr>'
    result += '<th>Cantidad de titulos completados</th>'
    result += '<th>Usuario</th>'
    result += '</tr>'

    for row in data:
        # Fila de una tabla HTML
        result += '<tr>'
        result += '<td>' + str(row[0]) + '</td>'
        result += '<td>' + str(row[1]) + '</td>'
        result += '</tr>'

    # Fin de la tabla HTML
    result += '</thead cellpadding="0" cellspacing="0" >'
    result += '</table>'

    return result

if __name__ == '__main__':
    print('Subiendo el primer programa desde la nube!')

    # Lanzar server
    app.run(host=server['host'],
            port=server['port'],
            debug=True)