import camera as c
import stream as s
import time
import _thread as th
import subprocess
import shlex

def start_stream():
    s.output = s.StreamingOutput()
    try:
        address = ('', 8000)
        server = s.StreamingServer(address, s.StreamingHandler)
        server.serve_forever()
    finally:
        print('ended')

def looping(name, camera):
    i = 0

    while True:
        #test

        if c.ffmpegProg != None:
            if (s.lastAccess + (60*1000)) < round(time.time() * 1000):
                c.stop_stream(camera)
                c.end_recording(camera)
        # Mainly for debugging
        #else:
        #    if i % 1000 == 0:
        #        s.PAGE=open("/home/pi/index.html", "r").read()

        time.sleep(60)
        i = i + 1


#limiter = subprocess.Popen(shlex.split("ffmpeg;"))
#limiter.wait()


camera = c.init()
s.camera = camera

th.start_new_thread(looping, ("Looper", camera))

start_stream()