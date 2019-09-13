from bs4 import BeautifulSoup
import requests
import json
import re
import argparse
import os

ap = argparse.ArgumentParser()
ap.add_argument("--lat", type=float, required=True, help="Latitude 64.123...")
ap.add_argument("--long", type=float, required=True, help="Longitude 22.4324...")
args = vars(ap.parse_args())

OPEN_CAGE_API_KEY = os.environ['OPEN_CAGE_API_KEY']

LATLONG_URL = "https://www.latlong.net/Show-Latitude-Longitude.html"


def specify_url(where):
    return "https://www.merinfo.se/search?d=p&where=%s" % where


def assemble_where(adr):
    out = [adr['road'], "%2C+", adr['postcode']]
    return ''.join(out)


def gps_to_adress(pos):
    r = requests.get('https://api.opencagedata.com/geocode/v1/json?q=%s+%s&key=%s' % (pos[0], pos[1], OPEN_CAGE_API_KEY))
    if r.status_code == 200:
        data = r.json()
    return(data['results'][0]['components'])


def get_people(url):
    people_out = []
    r = requests.get(url)
    if r.status_code == 200:
        data = BeautifulSoup(r.content, 'html.parser')
        pages_raw = data.find_all('div', 'col-xs-6 text-left')
        if 0 < len(pages_raw):
            pages_string = pages_raw[0].find_all('p')[0].string
        else:
            return {"length" : 0, "people": []}

        pages = int(round(int(re.findall("(?<=av )\d*", pages_string)[0])/20, 0))

    for i in range(pages):
        r = requests.get("%s&page=%s" % (url, i+1))
        if r.status_code == 200:
            data = BeautifulSoup(r.content, 'html.parser')
            people_raw = data.find_all('div', 'result-private')
            for p in people_raw:
                try:
                    name = p.find_all('h2', 'name')[0].a.text.strip()
                    ssn = p.find_all('p', 'ssn')[0].text.strip()[:-5]
                    adress = p.find_all('p', 'address')[0].text.strip()
                except:
                    print(("%s&page=%s" % (url, i+1)), p)

                people_out.append([name, ssn, adress])


    return {"length": len(people_out), "people": people_out}

adress_clean = assemble_where(gps_to_adress((args['lat'], args['long'])))
print(adress_clean)
print(get_people(specify_url(adress_clean)))
