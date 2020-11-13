#!/usr/bin/env python
'''
Heart DB manager
---------------------------
Autor: Inove Coding School
Version: 1.1

Descripcion:
Programa creado para administrar la base de datos de registro de personas
'''

__author__ = "Johana Rangel"
__email__ = "johanarang@hotmail.com"
__version__ = "1.0"

import os
import sqlite3
import requests

db = {}


def create_schema():

    # Conectarnos a la base de datos
    # En caso de que no exista el archivo se genera
    # como una base de datos vacia
    conn = sqlite3.connect(db['database'])

    # Crear el cursor para poder ejecutar las querys
    c = conn.cursor()

    # Obtener el path real del archivo de schema
    script_path = os.path.dirname(os.path.realpath(__file__))
    schema_path_name = os.path.join(script_path, db['schema'])

    # Crar esquema desde archivo
    c.executescript(open(schema_path_name, "r").read())

    # Para salvar los cambios realizados en la DB debemos
    # ejecutar el commit, NO olvidarse de este paso!
    conn.commit()

    # Cerrar la conexión con la base de datos
    conn.close()


def insert(name, age, nationality):
    conn = sqlite3.connect(db['database'])
    c = conn.cursor()

    values = [name, age, nationality]

    c.execute("""
        INSERT INTO persona (name, age, nationality)
        VALUES (?,?,?);""", values)

    conn.commit()
    # Cerrar la conexión con la base de datos
    conn.close()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def report(limit=0, offset=0, dict_format=False):
    # Conectarse a la base de datos
    conn = sqlite3.connect(db['database'])
    c = conn.cursor()

    if dict_format is True:
        conn.row_factory = dict_factory

    query = 'SELECT name, age, nationality  \
            FROM persona'

    if limit > 0:
        query += ' LIMIT {}'.format(limit)
        if offset > 0:
            query += ' OFFSET {}'.format(offset)

    query += ';'

    c.execute(query)
    query_results = c.fetchall()

    # Cerrar la conexión con la base de datos
    conn.close()
    return query_results

def nationality_review():
    
    conn = sqlite3.connect(db['database'])
    c = conn.cursor()
    
    c.execute('''SELECT COUNT(name) AS cantidad_personas, nationality \
                FROM persona GROUP BY nationality;''')
        
    resultados = c.fetchall()
    
    if resultados is None:
        return []

    conn.close()

    # Extraigo la informacion en listas
    total_personas = [x[0] for x in resultados]
    nacionalidad =  [x[1] for x in resultados]

    return total_personas, nacionalidad
    