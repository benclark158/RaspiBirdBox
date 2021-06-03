import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import json
import time
import camera as c

global PAGE
PAGE=open("/home/pi/index.html", "r").read()

output = None
camera = None
lastAccess = None

class StreamingOutput(object):
	def __init__(self):
		self.frame = None
		self.buffer = io.BytesIO()
		self.condition = Condition()

	def write(self, buf):
		if buf.startswith(b'\xff\xd8'):
			# New frame, copy the existing buffer's content and notify all
			# clients it's available
			self.buffer.truncate()
			with self.condition:
				self.frame = self.buffer.getvalue()
				self.condition.notify_all()
			self.buffer.seek(0)
		return self.buffer.write(buf)

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
	allow_reuse_address = True
	daemon_threads = True

class StreamingHandler(server.BaseHTTPRequestHandler):

	def write_success(self):
		content = str.encode("Success")
		self.send_response(200)
		self.send_header('Content-Type', 'text/json')
		self.send_header('Content-Length', len(content))
		self.end_headers()
		self.wfile.write(content)

	def do_GET(self):

		global lastAccess
		global camera
		global PAGE
		lastAccess = round(time.time() * 1000)

		if self.path == '/':
			self.send_response(301)
			self.send_header('Location', '/index.html')
			self.end_headers()
		elif self.path == '/index.html':
			currentTemp, _ = c.check_CPU_temp()

			if currentTemp < 80.0:
				c.start_stream_inactive(camera)

			content = PAGE.encode('utf-8')
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.send_header('Content-Length', len(content))
			self.end_headers()
			self.wfile.write(content)
		elif self.path == "/data":

			content = str.encode(c.build_json())

			self.send_response(200)
			self.send_header('Content-Type', 'text/json')
			self.send_header('Content-Length', len(content))
			self.end_headers()
			self.wfile.write(content)
		elif self.path.startswith("/api/"):
			if self.path == "/api/nightvision":
				c.toggle_mode()
				self.write_success()
			elif self.path == "/api/photo":
				c.take_photo(camera, False)
				self.write_success()
			elif self.path == "/api/hqphoto":
				c.take_photo(camera, True)
				self.write_success()
			elif self.path == "/api/startvideo":
				c.start_recording(camera)
				self.write_success()
			elif self.path == "/api/endvideo":
				c.end_recording(camera)
				self.write_success()
			elif self.path == "/api/reload":
				PAGE=open("/home/pi/index.html", "r").read()
				self.write_success()
			else:
				self.send_error(404)
				self.end_headers()
		else:
			self.send_error(404)
			self.end_headers()