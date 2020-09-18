import json
import pymongo
import sys



if len(sys.argv) == 1:
	env_var = input('Please enter database password \n')
else:
	env_var = sys.argv[1]

client = pymongo.MongoClient(
    "mongodb+srv://tsonyo:"+env_var+"@cluster0.7rz1o.mongodb.net/<dbname>?retryWrites=true&w=majority")
client.drop_database('cachimbas')
databasecachimbas = client['cachimbas']
minadasCol = databasecachimbas["minadas"]

listaFicheros = ['bengalas.json', 'hispacachimba.json',
                 'medusa.json', 'tgs.json', 'zuloshisha.json']


for nombreFichero in listaFicheros:
    with open(nombreFichero, 'r') as ficheroJson:
        nombrePagina = nombreFichero.split(".")[0]
        data = ficheroJson.read()
        objJSON = json.loads(data)
        infoPagina = objJSON[0]  # logo y nombre
        objJSON.pop(0)
        jsonGuardadoMongo = {
            'name': infoPagina['name'],
            'logo': infoPagina['logo'],
            'data': objJSON
        }
        minadasCol.insert_one(jsonGuardadoMongo)


print("[INFO] Exito insertando")
