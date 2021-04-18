with picamera.PiCamera(resolution='1280x720', framerate=30) as camera:
	camera.rotation = 180
	output = StreamingOutput()
	camera.start_recording(output, format='mjpeg')
	try:
		address = ('', 8000)
		server = StreamingServer(address, StreamingHandler)
		server.serve_forever()
	finally:
			camera.stop_recording()