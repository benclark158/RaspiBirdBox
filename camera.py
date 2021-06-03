from picamera import PiCamera, Color
import RPi.GPIO as GPIO
from time import sleep
import datetime as dt
import subprocess
import shlex
import re
import json
import stream as s
import glob

video_resolution = (1280, 720)
photo_resolution = (2592, 1944)

#this command below works for streaming to nginx
streamingCommand = "nice -n 18 ffmpeg -threads 1 -f s16le -ac 2 -i /dev/zero -i - -preset ultrafast -c:v h264 -preset:v ultrafast -b:v 500K -bf 0 -b:a 192k -g 60 -vcodec copy -acodec aac -f flv rtmp://birdbox:1935/live/birdbox"

#test stream to try and do all in one with ffmpeg
#streamingCommand = "ffmpeg -f s16le -ac 2 -i /dev/zero -i - -c:v libx264 -framerate 30 -maxrate 1M -preset ultrafast -g 60 -c:a aac -b:a 128k -ac 2 -f hls -hls_time 4 -hls_playlist_type vod stream.m3u8"


saveLocation = "/home/pi/nginx/"
ffmpegProg = None
ffmpegProgRec = None
currentMode = "day"
recording = False

def init(display = True):

    #preps output pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(21,GPIO.OUT)

    set_mode(currentMode)

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

    #start_stream_inactive(camera)

    #outputs to displau
    if(display):
        camera.start_preview()

    return camera

def start_stream(camera):
    #starts stream
    cvlc = subprocess.Popen(shlex.split(streamingCommand), stdin=subprocess.PIPE)
    camera.start_recording(cvlc.stdin, 'h264', splitter_port=2, bitrate=10000000)

    return cvlc

def stop_stream(camera):
    global ffmpegProg
    try:
        camera.stop_recording(splitter_port=2)
    finally:
        ffmpegProg.terminate()
        ffmpegProg.wait()
    
    print("Terminate Stream")
    ffmpegProg = None  

def close(camera):
    global recording
    if recording:
        camera.stop_recording()
    recording = False
    camera.stop_preview()
    camera.close()

def start_stream_inactive(camera):
    global ffmpegProg
    if ffmpegProg == None:
        ffmpegProg = start_stream(camera)

def get_current_timestamp():
    return dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def toggle_mode():
    if(currentMode == 'day'):
        set_mode('night')
    else:
        set_mode('day')

def set_mode(mode):
    global currentMode
    currentMode = mode
    if(mode == 'day'):
        GPIO.output(21,GPIO.HIGH)
    elif (mode == 'night'):
        GPIO.output(21,GPIO.LOW)

def take_photo(camera, isLarge = False):
    if isLarge:
        stop_stream(camera)
        end_recording(camera)
        sleep(0.01)
        camera.resolution = photo_resolution
        camera.framerate = 15
        sleep(0.01)

    camera.capture(saveLocation + "images/" + get_current_timestamp() + ".jpg", use_video_port=True)

    if isLarge:
        camera.resolution = video_resolution
        camera.framerate = 30
        sleep(0.01)
        start_stream(camera)

def start_recording(camera):
    global recording
    if recording == False:
        print("Start recording: " + get_current_timestamp())
        recording = True
        #camera.resolution = video_resolution
        #camera.framerate = 30
        camera.start_recording(saveLocation + "videos/" + get_current_timestamp() + ".h264")
    
    #global ffmpegProgRec

    #ffmpegProgRec = subprocess.Popen(shlex.split(savingCommand), stdin=subprocess.PIPE)
    #camera.start_recording(ffmpegProgRec.stdin, 'h264', bitrate=10000000)

def end_recording(camera):
    global recording
    
    if recording:
        camera.stop_recording()

        recording = False
        sleep(0.3)

        files = glob.glob("nginx/videos/*.h264")
        for f in files:
            convert = "nice -n 19 ffmpeg -framerate 30 -i \"" + f + "\" -c copy \"" + f.replace(".h264", ".mp4") + "\""
            #print(convert)
            convProc = subprocess.Popen(shlex.split(convert))
            convProc.wait()
            delProc = subprocess.Popen(shlex.split("rm \"" + f + "\""))
            delProc.wait()

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

def build_json():
    currentTemp, _ = check_CPU_temp()
    global recording

    x = {
        "stats": [
            {"id": "current-temperature", "value": str(currentTemp)},
            {"id": "recording", "value": recording}
        ],
        "images": sorted([w.replace('nginx/', '') for w in glob.glob("nginx/images/*.jpg")])[::-1],
        "videos": sorted([w.replace('nginx/', '') for w in glob.glob("nginx/videos/*.mp4")])[::-1]
    }
    return json.dumps(x)

#GPIO.output(21,GPIO.LOW)
#GPIO.output(21,GPIO.HIGH)

#camera.start_preview()
#sleep(5)

#camera.capture('image.jpg')

#camera.stop_preview()