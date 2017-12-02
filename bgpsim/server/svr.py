import SocketServer
import random
import json
import subprocess

err={
-1:"format error",
0:"success",
1:"action not provided",
2:"target not specified",
3:"duration not specified",
4:"invalid action",
5:"server error"
}

class MyTCPHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		# self.request is the TCP socket connected to the client
		self.data = self.request.recv(1024).strip()
		#print "{} wrote:".format(self.client_address[0])
		#print self.data
		
		ret={}
		try:
			obj=json.loads(self.data)
		except:
			ret["status"]=-1
			ret["msg"]=err[-1]
			self.request.sendall(json.dumps(ret))
			return
			
		if not obj.has_key("action"):
			ret["status"]=1
			ret["msg"]=err[1]
			self.request.sendall(json.dumps(ret))
			return
		
		action = obj["action"]
		if action == "fetch_bot_list":
			if not obj.has_key("target"):
				ret["status"]=2
				ret["msg"]=err[2]
				self.request.sendall(json.dumps(ret))
				return
			target=obj["target"]

			result={}
			result["length"]=random.randint(400,501)
			result["bot_list"]=[]
			ret["result"]=result

			ret["status"]=0
			ret["msg"]=err[0]
			self.request.sendall(json.dumps(ret))
		elif action == "begin_attack":
			if not obj.has_key("duration"):
				ret["status"]=3
				ret["msg"]=err[3]
				self.request.sendall(json.dumps(ret))
				return
			target=obj["duration"]

			result={}
			h = subprocess.Popen("echo hello", shell=True, stdout=subprocess.PIPE)
			r=h.stdout.read()
			result["output"]=r
			ret["result"]=result

			ret["status"]=0
			ret["msg"]=err[0]
			self.request.sendall(json.dumps(ret))
		else:
			ret["status"]=4
			ret["msg"]=err[4]
			self.request.sendall(json.dumps(ret))

if __name__ == "__main__":
	HOST, PORT = "10.11.118.68", 9999

	server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

	server.serve_forever()
