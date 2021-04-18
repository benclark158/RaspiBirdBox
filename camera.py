from picamera import PiCamera, Color
import RPi.GPIO as GPIO
from time import sleep
import datetime as dt
import subprocess
import shlex
import re
import stream as s

video_resolution = (1280, 720)
photo_resolution = (2592, 1944)

vlcCommand = "cvlc -vvv stream:///dev/stdin --sout '#transcode{vcodec=h264,vb=1024,channels=1,ab=128,samplerate=44100,width=320}:http{mux=ts,dst=:8080/webcam.mp4}' :demux=h264"

def init(display = True):

    #preps output pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(21,GPIO.OUT)

    set_mode('day')

    #loads camera
    camera = PiCamera()
    camera.rotation = 180

    #prep resolution
    camera.resolution = video_resolution
    camera.framerate = 30

    #preps exposure
    camera.meter_mode = 'matrix'
    camera.exposure_mode = 'auto'
    #camera.shutter_speed = 16666
    #camera.iso = 800

    #starts stream
    #cvlc = subprocess.Popen(shlex.split(vlcCommand), stdin=subprocess.PIPE)
    #camera.start_recording(cvlc.stdin, 'h264')

    #outputs to displau
    if(display):
        camera.start_preview()

    return camera

def close(camera, cvlc):
    camera.stop_recording()
    cvlc.terminate()
    camera.stop_preview()
    camera.close()

def get_current_timestamp():
    return dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def start_stream(camera):
    output = s.StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = s.StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()

def set_mode(mode):
    if(mode == 'day'):
        GPIO.output(21,GPIO.HIGH)
    elif (mode == 'night'):
        GPIO.output(21,GPIO.LOW)

def take_photo(camera):
    camera.resolution = photo_resolution
    camera.framerate = 15
    sleep(0.01)

    camera.capture(get_current_timestamp() + ".jpg")

    camera.resolution = video_resolution
    camera.framerate = 30
    sleep(0.01)

def start_recording(camera):
    camera.resolution = video_resolution
    camera.framerate = 30
    camera.start_recording(get_current_timestamp() + ".h264")

def end_recording(camera):
    camera.stop_recording()


def check_CPU_temp():
    temp = None
    err, msg = subprocess.getstatusoutput('vcgencmd measure_temp')
    if not err:
        m = re.search(r'-?\d\.?\d*', msg)   # https://stackoverflow.com/a/49563120/3904031
        try:
            temp = float(m.group())
        except:
            pass
    return temp, msg

#GPIO.output(21,GPIO.LOW)
#GPIO.output(21,GPIO.HIGH)

#camera.start_preview()
#sleep(5)

#camera.capture('image.jpg')

#camera.stop_preview()