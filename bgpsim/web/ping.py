import getopt
import time
import subprocess
import sys
import json

import tornado.httpserver
import tornado.websocket
import tornado.httpclient
import tornado.httputil
import tornado.ioloop
import tornado.web
import tornado.gen

DEFAULT_CONNECT_TIMEOUT = 60
DEFAULT_REQUEST_TIMEOUT = 60
 
class WebSocketClient():
	def __init__(self, connect_timeout=DEFAULT_CONNECT_TIMEOUT, request_timeout=DEFAULT_REQUEST_TIMEOUT):
		self.connect_timeout = connect_timeout
		self.request_timeout = request_timeout

	def connect(self, url):
		headers = tornado.httputil.HTTPHeaders({'Content-Type': 'application/text'})
		request = tornado.httpclient.HTTPRequest(url=url,connect_timeout=self.connect_timeout,request_timeout=self.request_timeout,headers=headers)
		ws_conn = tornado.websocket.WebSocketClientConnection(tornado.ioloop.IOLoop.current(),request)
		ws_conn.connect_future.add_done_callback(self._connect_callback)

	def send(self, data):
		if not self._ws_connection:
			raise RuntimeError('Web socket connection is closed.')
		self._ws_connection.write_message(data)

	def close(self):
		if not self._ws_connection:
			raise RuntimeError('Web socket connection is already closed.')
		self._ws_connection.close()

	def _connect_callback(self, future):
		if future.exception() is None:
			self._ws_connection = future.result()
			self._on_connection_success()
			self._read_messages()
		else:
			self._on_connection_error(future.exception())

	@tornado.gen.coroutine
	def _read_messages(self):
		while True:
			msg = yield self._ws_connection.read_message()
			if msg is None:
				self._on_connection_close()
				break
			self._on_message(msg)

	def _on_message(self, msg):
		pass

	def _on_connection_success(self):
		pass

	def _on_connection_close(self):
		pass

	def _on_connection_error(self, exception):
		pass

class PingWSClient(WebSocketClient):
	def __init__(self, ping_app):
		WebSocketClient.__init__(self)
		self.ping_app = ping_app

	def _on_message(self, msg):
		obj = json.loads(msg)
		self.ping_app.handler.write_message(json.dumps(obj["data"]))

	def _on_connection_success(self):
		pass

	def _on_connection_error(self, exception):
		sys.stderr.write(str(exception)+"\n")
		exit()

class WSApplication(tornado.web.Application):
	def __init__(self, handlers):
		tornado.web.Application.__init__(self, handlers)
		self.cl = []
		self.ul = ["ws://47.90.99.168:8887/ws"]
		self.handler = None

class WSHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		self.application.handler = self
		return
	  
	def on_message(self, message):
		obj=json.loads(message)
		a=obj["action"]
		if a == "start":
			data={}
			data["action"]="start"
			if not obj.has_key("target"):
				return
			tgt = obj["target"]
			data["target"]=tgt

			for c in self.application.cl:
				c.send(json.dumps(data))
		elif a == "stop":
			data={}
			data["action"]="stop"
			for c in self.application.cl:
				c.send(json.dumps(data))
	
	def on_close(self):
		data={}
		data["action"]="stop"
		for c in self.application.cl:
			c.send(json.dumps(data))
 
	def check_origin(self, origin):
		return True

def usage():
	print "ping -w <$wsip:$wsport>"

if __name__ == '__main__':
	HOST_NAME="localhost"
	WSPORT_NUMBER=8886
	try:
		opts, args = getopt.getopt(sys.argv[1:], "p:")
	except getopt.GetoptError as err:
		print str(err)
		usage()
		exit()

	wsport=""
	for o,a in opts:
		if o == "-p":
			WSPORT_NUMBER=a

	application = WSApplication([(r'/ws', WSHandler),])
	for u in application.ul:
		c = PingWSClient(application)
		c.connect(u)
		application.cl.append(c)
	ws_server = tornado.httpserver.HTTPServer(application)
	ws_server.listen(WSPORT_NUMBER)

	print time.asctime(), "WS Server Starts - %s:%s" % (HOST_NAME, WSPORT_NUMBER)
	try:
		tornado.ioloop.IOLoop.instance().start()
	except KeyboardInterrupt:
		pass
	print time.asctime(), "WS Server Stops - %s:%s" % (HOST_NAME, WSPORT_NUMBER)
