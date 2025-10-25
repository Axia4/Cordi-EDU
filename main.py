from flask import Flask, render_template, request, g, redirect, url_for, session, flash
from helpers import DATA_DIR
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-for-dev')

# Data storage tree example. use only for reference.
_DATA_PATH_TEMPLATE = {
    'Centros': {
        '<IREF_CENTRO>': {
            '_data.json': "file",
            'Documentos': "uploads",
            'Aulas': {
                '<IREF_AULA>': {
                    '_data.json': "file",
                    'Documentos': "uploads"
                }
            },
            'ExistenciasMateriales': {
                '<ID>': {
                    '_data.json': "file",
                    'Documentos': "uploads"
                }
            }
        }
    },
    'Actividades': {
        '<ID>.ics': "file"
    },
    'Alumnxs': {
        '<ID>': {
            '_data.json': "file",
            'Documentos': "uploads"
        }
    },
    'Materiales': {
        '<ID>': {
            '_data.json': { #DATA STRUCTURE
                "Nombre": "string",
                "Descripción": "string",
                "Documentos": "list<uploads<Documentos>>",
                "Foto_Principal": "reference<Documentos>",
                "Codigos de barras": [
                    {"Tipo": "string", "Valor": "string", "Cantidad": "float", "Unidad": "string"}
                ],
                "URLs de compra": [
                    {"URL": "string", "Tienda": "string", "Nombre": "string", "Prioridad": "int", "Interno": "bool"}
                ],
                "Unidades": [
                    {"Unidad": "string", "Por defecto": "bool"}
                ]
            },
            'Documentos': "uploads"
        }
    },
    'Pedido': {
        '<ID>': {
            '_data.json': {
                "Materiales": [
                    {"Material_ID": "string", "Cantidad": "float", "Unidad": "string"}
                ],
                "Fecha_Pedido": "date",
                "Fecha_Recepcion_Estimada": "date",
                "Fecha_Recepcion_Real": "date",
                "Proveedor": "string",
                "Estado": [
                    {"Estado": "string", "Fecha": "date", "Notas": "string", "Final": "bool", "Incidencia": "bool"}
                ],
                "Documentos": "list<uploads<Documentos>>"
            },
            'Documentos': "uploads"
        }
    }
}
@app.before_request
def before_request():
    g.NAV_ENDPOINT = request.endpoint
    g.CentroActual = session.get('CentroActual', '') != ''
    g.CentroActualName = session.get('CentroActualName', 'Ninguno')
    # ensure cart exists in session
    session.setdefault('cart', [])


# --- routes ------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')


# --- blueprints -------------------------------------------------------------
from centros import centros
app.register_blueprint(centros)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3129, debug=True)
