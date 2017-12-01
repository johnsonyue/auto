import datetime
import time
import json
import os
import subprocess
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from functools import partial
import threading

class WSApplication(tornado.web.Application):
	def __init__(self, handlers):
		tornado.web.Application.__init__(self, handlers)
		self.ps = {}
		self.ping = ping
		self.callback = callback

def ping(cid,ll):
	f=cid.split('-')
	p=os.popen("./remote "+f[0]+" \"docker exec "+f[0]+" ping "+f[1]+"\"")
	while True:
		l=p.readline().strip()
		if not l:
			break
		ll.append(l)

def callback():
	return

class WSHandler(tornado.websocket.WebSocketHandler):
	def open(self): return
	  
	def on_message(self, message):
		obj=json.loads(message)
		self.application.ps[obj["id"]]=[]
		t=threading.Thread(target=self.application.ping, args=[obj["id"],self.application.ps[obj["id"]]])
		t.start()
		self.scheduled(obj["id"],-1)

		return
 
	def on_close(self):
		return
 
	def check_origin(self, origin):
		return True

	def scheduled(self, cid, pl):
		ll=self.application.ps[cid]
		if pl == len(ll):
			self.write_message("HALT")
		for l in ll[pl+1:]:
			self.write_message(l)

		tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=1), partial(self.scheduled, cid, len(ll)-1)) 

if __name__ == '__main__':
	HOST_NAME=1
	WSPORT_NUMBER=8881
	application = WSApplication([(r'/ws', WSHandler),])
	ws_server = tornado.httpserver.HTTPServer(application)
	ws_server.listen(WSPORT_NUMBER)

	print time.asctime(), "WS Server Starts - %s:%s" % (HOST_NAME, WSPORT_NUMBER)
	try:
		tornado.ioloop.IOLoop.instance().start()
	except KeyboardInterrupt:
		pass
	print time.asctime(), "WS Server Stops - %s:%s" % (HOST_NAME, WSPORT_NUMBER)
