import requests
import json
import time
import datetime
import random

TIME_INTERVAL = 60
EXPORT_FILENAME = "AIS_dump.json"

random.seed()

while (True):
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    url = "https://www.vesselfinder.com/vesselsonmap?bbox="
    # Four steps to be replaced with variables
    url += "-3.4730226713903742,"
    url += "26.839617694987496,"
    url += "37.132446078609625,"
    url += "48.55723841575042"

    url += "&zoom=5"
    url += "&mmsi=0&show_names=0&ref=66806.32884773801&pv=6"

    data = requests.get(url, headers=headers)

    # On actualise notre timestamp
    currentTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    d_list = str(data.content).split("\\n")
    d_list = [x.split("\\t") for x in d_list]
    cleand = list()
    for l in d_list:
        try:
            d = {
                'LONG': l[0],
                'LAT': l[1],
                'COG': l[2],
                'SOG': l[3],
                'HEADING': l[4],
                'MMSI': l[5],
                'PAC': l[6],
		'TIME': currentTime
            }
            cleand.append(d)
        except Exception as e:
            # print(str(e) + " --> with l : " + str(l))
            print("Exception occured : " + str(e))
    with open("./" + EXPORT_FILENAME, "a") as f:
        f.write(json.dumps(cleand))
        print("Ligne de data écrite dans le fichier : "+EXPORT_FILENAME)
    
    # On prépare le prochain ping sur le serveur, en ajoutant un peu d'aléatoire pour pas se faire cramer par le serveur si jamais...
    randNumber = random.randint(-17,11)
    sleepTime = randNumber + TIME_INTERVAL
    print("Prochain ping dans : {} secondes.".format(sleepTime))
    time.sleep(sleepTime)
exit()
