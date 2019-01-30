#!/usr/bin/python
# pip install -r requirements.txt
# conda install --yes --file requirements.txt
import os
USERNAME = 'xxxx'
PASSWORD = 'xxxx'
# BASE_DOWNLOAD_PATH = 'out2'  # use "/" as separators
BASE_DOWNLOAD_PATH = os.path.join(os.path.dirname(__file__), "Cursos")

COURSES = [
    # 'power-bi-avanzado',
    'excel-2019-obtener-y-transformar-datos-power-query'
    # 'machine-learning-and-ai-foundations-value-estimations'
    # 'power-bi-esencial'
    # 'django-desarrollo-web'
    # 'python-avanzado'--charmap
    # 'learning-hadoop'
    # 'project-2016-avanzado'
    # 'excel-2016-practico-25-aplicaciones-basicas-con-tablas-dinamicas'
    # 'fred-kofman-on-managing-conflict',
    # 'reid-hoffman-and-chris-yeh-on-creating-an-alliance-with-employees',
    # 'bill-george-on-self-awareness-authenticity-and-leadership',
]
