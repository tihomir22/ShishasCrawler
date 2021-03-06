import json
import pymongo
import sys
from datetime import datetime
import random
from os.path import expanduser

if len(sys.argv) == 1:
    env_var = input('Please enter database password \n')
else:
    env_var = sys.argv[1]

client = pymongo.MongoClient(
    "mongodb+srv://tsonyo:"+env_var+"@cluster0.7rz1o.mongodb.net/<dbname>?retryWrites=true&w=majority")
# client.drop_database('chollohooka')
databaseChollohooka = client['chollohooka']
databaseChollohookaPROD = client['chollohooka-PROD']
home = expanduser("~")
basePath = home + '/data/'
listaFicheros = ['medusa.json', 'tgs.json', "bengalas.json",
                 'hispacachimba.json', 'zuloshisha.json', "bakkali.json"]

keysPermitidasParaSerNulas = ["preciorebajado", "cantidad", "shortdesc"]

basesDeDatos = ["chollohooka"]


def isAllowedToBeNull(key):
    return key.lower() in keysPermitidasParaSerNulas


def comprobarValidezaMetadatos(metadataObj, nameSite):
    if metadataObj is not None:
        for key, value in metadataObj.items():
            if isAllowedToBeNull(key) == False:
                if metadataObj[key] is None:
                    addError(nameSite, "La propiedad " +
                             key+" está nulificada", "ERROR")
                    return False
                elif isinstance(metadataObj[key], list) and len(metadataObj[key]) == 0:
                    addError(nameSite, "La propiedad " +
                             key+" está vacia", "WARNING")
                elif isinstance(metadataObj[key], str) and len(metadataObj[key]) == 0:
                    addError(nameSite, "El texto "+key +
                             " está vacio", "WARNING")
        return True
    else:
        addError("No existe alguna pagina...", metadataObj, "ERROR")
        return False


def addError(nombrePagina, mensajeError, tipo):
    for database in basesDeDatos:
        client[database]["errores"].insert_one(
            {'pagina': nombrePagina, 'mensajeError': mensajeError, "tipo": tipo, 'date': datetime.now(), 'estado': 'NON_PROCESSED'})
        print("["+database+"]["+tipo+"] - "+nombrePagina+" -"+mensajeError)


block = {"dateBlock": datetime.now(), "statuses": {}}
objetoIds = {"chollohooka": ""}

for database in basesDeDatos:
    objetoIds[database] = client[database]["bloques"].insert(block)

for nombreFichero in listaFicheros:
    try:
        with open((basePath + nombreFichero), 'r') as ficheroJson:
            nombrePagina = nombreFichero.split(".")[0]
            data = ficheroJson.read()
            objJSON = json.loads(data)

            infoPagina = objJSON[0]  # logo y nombre
            print(infoPagina)
            nombrePag = infoPagina['name']
            muestraRandomDeDatos = objJSON[random.randint(1, len(objJSON)-1)]
            validezaMetadatos = comprobarValidezaMetadatos(
                infoPagina, nombrePag)
            validezaDatos = comprobarValidezaMetadatos(
                muestraRandomDeDatos, nombrePag)
            objJSON.pop(0)
            if validezaDatos == True and validezaMetadatos == True:
                for database in basesDeDatos:
                    site = {
                        'lastUpdate': infoPagina['lastUpdate'],
                        'lastUpdateMongo': datetime.now(),
                        'name': infoPagina['name'],
                        'logo': infoPagina['logo'],
                        'blockId': objetoIds[database]
                    }
                    _id = client[database]["paginas"].insert(site)
                    for cachimba in objJSON:
                        cachimba['siteId'] = _id
                    client[database]["items"].insert_many(objJSON)
                    block['statuses'].update(
                        {infoPagina['name'].lower(): True})
                    client[database]["bloques"].update(
                        {"_id": objetoIds[database]}, block)
            else:
                block['statuses'].update({infoPagina['name'].lower(): False})
                client[database]["bloques"].update(
                    {"_id": objetoIds[database]}, block)

    except Exception as e:
        print(e)


print("[INFO] Exito insertando")
