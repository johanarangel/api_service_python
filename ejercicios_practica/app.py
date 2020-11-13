#!/usr/bin/env python
'''
API Personas
---------------------------
Autor: Inove Coding School
Version: 1.0
 
Descripcion:
Se utiliza Flask para crear un WebServer que levanta los datos de
las personas registradas.

Ejecución: Lanzar el programa y abrir en un navegador la siguiente dirección URL
NOTA: Si es la primera vez que se lanza este programa crear la base de datos
entrando a la siguiente URL
http://127.0.0.1:5000/reset

Ingresar a la siguiente URL para ver los endpoints disponibles
http://127.0.0.1:5000/
'''

__author__ = "Johana Rangel"
__email__ = "johanarang@hotmail.com"
__version__ = "1.0"

# Realizar HTTP POST --> post.py

import traceback
import io
import sys
import os
import base64
import json
import sqlite3
from datetime import datetime, timedelta

import numpy as np
from flask import Flask, request, jsonify, render_template, Response, redirect
import matplotlib
matplotlib.use('Agg')   # For multi thread, non-interactive backend (avoid run in main loop)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.image as mpimg

import persona
from config import config


app = Flask(__name__)

# Obtener la path de ejecución actual del script
script_path = os.path.dirname(os.path.realpath(__file__))

# Obtener los parámetros del archivo de configuración
config_path_name = os.path.join(script_path, 'config.ini')
db = config('db', config_path_name)
server = config('server', config_path_name)

persona.db = db


@app.route("/")
def index():
    try:
        # Imprimir los distintos endopoints disponibles
        result = "<h1>Bienvenido!!</h1>"
        result += "<h2>Endpoints disponibles:</h2>"
        result += "<h3>[GET] /reset --> borrar y crear la base de datos</h3>"
        result += "<h3>[GET] /personas?limit=[]&offset=[] --> mostrar el listado de personas (limite and offset are optional)</h3>"
        result += "<h3>[POST] /registro --> ingresar nuevo registro de pulsaciones por JSON</h3>"
        result += "<h3>[GET] /comparativa --> mostrar un gráfico que compare cuantas personas hay de cada nacionalidad"
        
        return(result)
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/reset")
def reset():
    try:
        # Borrar y crear la base de datos
        persona.create_schema()
        result = "<h3>Base de datos re-generada!</h3>"
        return (result)
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/personas")
def personas():
        
    try:
        # Mostrar todas las personas
        result = show()
        return (result)
    except:
        return jsonify({'trace': traceback.format_exc()})
        

@app.route("/comparativa")
def comparativa():
   
    try: 
        
        total_personas, nacionalidad = persona.nationality_review()
        
        # Crear el grafico que se desea mostrar
        fig, ax = plt.subplots(figsize=(16, 9))
        ax.bar(nacionalidad, total_personas)
        ax.get_xaxis().set_visible(False)

        # Convertir ese grafico en una imagen para enviar por HTTP
        # y mostrar en el HTML
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        plt.close(fig)  # Cerramos la imagen para que no consuma memoria del sistema
        return Response(output.getvalue(), mimetype='image/png')

    except:
        return jsonify({'trace': traceback.format_exc()})

    
@app.route("/registro", methods=['POST'])
def registro():
    if request.method == 'POST':
        # Obtener del HTTP POST JSON el nombre y los pulsos
        name = str(request.form.get('name'))
        age = str(request.form.get('age'))
        nationality = str(request.form.get('nationality'))
        
        if (name is None or age is None or age.isdigit() is False or nationality is None):
            return Response (status=400)
        
        persona.insert(name, int(age), nationality)
        return Response(status=200)

def show(show_type='json'):

    # SE PIDEN LOS DATOS DE LA URL
    limit_str = str(request.args.get('limit'))
    offset_str = str(request.args.get('offset'))

    limit = 0
    offset = 0

    if(limit_str is not None) and (limit_str.isdigit()):
        limit = int(limit_str)

    if(offset_str is not None) and (offset_str.isdigit()):
        offset = int(offset_str)

    if show_type == 'json':
        data = persona.report(limit=limit, offset=offset, dict_format=True)
        return jsonify(data)
    
    elif show_type == 'table':
        data = persona.report(limit=limit, offset=offset, dict_format=True)
        return html_table(data)

    else:
        data = persona.report(limit=limit, offset=offset, dict_format=True)
        return jsonify(data)

def html_table(data):

    # Tabla HTML, header y formato
    result = '<table border="1">'
    result += '<thead cellpadding="1.0" cellspacing="1.0">'
    result += '<tr>'
    result += '<th>Nro personas</th>'
    result += '<th>Nacionalidad</th>'
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
    print('Servidor arriba!')

    app.run(host=server['host'],            
            port=server['port'],
            debug=True)

