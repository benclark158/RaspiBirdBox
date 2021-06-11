import camera as c
import stream as s
import time
import _thread as th
import subprocess
import shlex
import datetime as dt
import sunset as sun
import os

def start_web_server():
    s.output = s.StreamingOutput()
    try:
        address = ('', 8000)
        server = s.StreamingServer(address, s.StreamingHandler)
        print("Birdbox Ready...")
        server.serve_forever()
    finally:
        print('Web Server Failure')

def ping():
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', '-c', '1', 'google.com']

    return subprocess.call(command, stdout=subprocess.PIPE) == 0

def looping(name, camera):
    i = 0
    sun.set_nightvision_setting(True)

    while True:
        #test

        if c.ffmpegProg != None:
            if (s.lastAccess + (60*1000)) < round(time.time() * 1000):
                c.stop_stream(camera)
                c.end_recording(camera)
                c.userSetNV = False
                sun.set_nightvision_setting(True)
        # Mainly for debugging
        #else:
        if i % (30*60) == 0:
            print("Valid Internet Connection: " + str(ping()))
            #s.PAGE=open("/home/pi/index.html", "r").read()

        nowHour = int(dt.datetime.now().strftime('%H'))
        #print('hour: ' + str(nowHour))

        if (nowHour >= 3 and nowHour < 5 and c.get_boot_duration() > (4*60*60) and c.ffmpegProg == None):
            print('Rebooting Pi')
            os.system('systemctl reboot -i')

        sun.set_nightvision_setting(False)

        time.sleep(60)
        i = i + 1


#limiter = subprocess.Popen(shlex.split("ffmpeg;"))
#limiter.wait()

print('Starting BirdBoxCamPi')
print("Birdbox located at: " + c.get_location().address)

camera = c.init()
s.camera = camera

th.start_new_thread(looping, ("Looper", camera))

start_web_server()