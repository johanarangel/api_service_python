#!/usr/bin/env python
'''
API Monitor cardíaco
---------------------------
Autor: Inove Coding School
Version: 1.0
 
Descripcion:
Se utiliza request para generar un HTTP post al servidor Flask
'''

__author__ = "Inove Coding School"
__email__ = "INFO@INOVE.COM.AR"
__version__ = "1.0"

import os
import requests
import json

from config import config

# Obtener la path de ejecución actual del script
script_path = os.path.dirname(os.path.realpath(__file__))

# Obtener los parámetros del archivo de configuración
config_path_name = os.path.join(script_path, 'config.ini')
server = config('server', config_path_name)

ip = server['host']
port = server['port']
endpoint = 'registro'

url = f'http://{ip}:{port}/{endpoint}'

if __name__ == "__main__":

    try:
        response = requests.get("https://jsonplaceholder.typicode.com/todos")
        response_data = response.json()
        
        for row in response_data:
            x = requests.post(url, data = row)
            print('POST enviado a:',url)
            print('Datos:')
            print(row)
    except:
        print('Error, POST no efectuado')