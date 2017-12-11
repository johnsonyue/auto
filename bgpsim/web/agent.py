import getopt
import time
import datetime
import subprocess
import threading
import sys
import json
import functools

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

def ping(cid,tgt,ll):
	h=subprocess.Popen("docker exec " + str(cid) + " ping -n " + str(tgt), shell=True, stdout=subprocess.PIPE)
	while True:
		l=h.stdout.readline().strip()
		if not l:
			h.stdout.close()
			break
		ll.append(l)

class WSApplication(tornado.web.Application):
	def __init__(self, handlers):
		tornado.web.Application.__init__(self, handlers)
		self.ps = {}
		self.ping = ping

class WSHandler(tornado.websocket.WebSocketHandler):
	def open(self): return
	  
	def on_message(self, message):
		obj=json.loads(message)
		a=obj["action"]
		if a == "start":
			if not obj.has_key("target"):
				return
			tgt = obj["target"]
			cl=map( lambda x:x.strip(), subprocess.Popen("docker ps | tail -n +2 | awk '{print $NF}'", shell=True, stdout=subprocess.PIPE).stdout.readlines() )
			for c in cl:
				self.application.ps[c]=[]
				t=threading.Thread( target=self.application.ping, args=[c, tgt, self.application.ps[c]] )
				t.start()
			self.scheduled( cl, {cl[i]:-1 for i in range(len(cl))} )
		elif a == "stop":
			subprocess.Popen("./clear.sh ping", shell=True)
 
	def on_close(self): return
 
	def check_origin(self, origin):
		return True

	def scheduled(self, cl, pl):
		rl = []
		for c in cl:
			ll=self.application.ps[c]
			p=pl[c]
			if p == len(ll)-1:
				rl.append(c+"#HALT")
			for l in ll[p+1:]:
				rl.append(c+"#"+l)
		ret={}
		ret["action"]="reply"
		ret["data"]=rl
		self.write_message(json.dumps(ret))

		pl = { x:len(self.application.ps[x])-1 for x in self.application.ps.keys() }
		tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=1), functools.partial(self.scheduled, cl, pl)) 

def usage():
	print "agent [-p <$wsport>]"

if __name__ == '__main__':
	HOST_NAME="localhost"
	WSPORT_NUMBER=8887
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
	ws_server = tornado.httpserver.HTTPServer(application)
	ws_server.listen(WSPORT_NUMBER)

	print time.asctime(), "WS Server Starts - %s:%s" % (HOST_NAME, WSPORT_NUMBER)
	try:
		tornado.ioloop.IOLoop.instance().start()
	except KeyboardInterrupt:
		pass
	print time.asctime(), "WS Server Stops - %s:%s" % (HOST_NAME, WSPORT_NUMBER)
