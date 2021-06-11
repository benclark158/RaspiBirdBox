import requests
import datetime as dt
import json
import camera as c

def get_sun_times():
    today = dt.datetime.today().strftime('%Y-%m-%d')
    latlong = c.get_location().latlng

    url = "https://api.sunrise-sunset.org/json?lat=" + str(latlong[0]) + "&lng=" + str(latlong[1]) + "&formatted=0&date=" + today

    f = requests.get(url)
    contents = f.text

    jsonData = json.loads(contents)

    dtSunrise = dt.datetime.strptime(jsonData["results"]["sunrise"], "%Y-%m-%dT%H:%M:%S+00:00")
    dtSunset = dt.datetime.strptime(jsonData["results"]["sunset"], "%Y-%m-%dT%H:%M:%S+00:00")
    
    sunrise = dt.datetime.timestamp(dtSunrise)
    sunset = dt.datetime.timestamp(dtSunset)
    return [sunrise, sunset]

def set_nightvision_setting(force = False):
    sunrise, sunset = get_sun_times()

    now = int(dt.datetime.now().timestamp())

    #print([sunrise, sunset, now])

    if force:
        if int(sunrise) <= now and int(sunset) > now:
            c.set_mode('day')
        else:
            c.set_mode('night')
    else:
        if abs(now - int(sunrise)) <= 30 and c.userSetNV == False:
            #sunrise in change over
            c.set_mode('day')
        elif abs(now - int(sunset)) <= 30 and c.userSetNV == False:
            #sunset in progress
            c.set_mode('night')

