#  coding: utf-8 
import socketserver
from os import path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

	def serve_content(self, path, headers):
		with open(path, 'r') as f:
			lines_list = f.readlines()
			content = "\n".join(lines_list)
			response = headers + content
			self.request.sendall(response.encode())

	def handle(self):
		self.data = self.request.recv(1024).strip()
		print ("\nGot a request of: %s" % self.data)
		request_list = self.data.decode().split()
		request_method = request_list[0] # want to response 405 if this is not GET
		if request_method != "GET":
			self.request.send("HTTP/1.0 405 Method Not Allowed\r\n\r\n".encode())
		address = request_list[1]
		file_name = address[1:] # get rid of the "/"
		if '../' in file_name: # if tries to access any thing above www/
			self.request.send("HTTP/1.0 404 Not Found\r\n\r\n".encode())
		file_path = "./www/" + file_name
		if path.isdir(file_path) and path.exists(file_path):
			if file_path[-1] != '/': # 301 redirect to a correct url
				location = 'http//:localhost:8080/www/' + file_path + "/"
				headers = "HTTP/1.0 301 Moved Permanently Location: " + location + "\r\nContent-Type: text/html\r\n\r\n"
				self.serve_content("./www/index.html", headers)
			headers = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"
			self.serve_content("./www/index.html", headers)
		elif path.isfile(file_path) and path.exists(file_path):
			text_type = file_name.split('.')[-1].strip()
			headers = "HTTP/1.0 200 OK\r\nContent-Type: text/" + text_type + "\r\n\r\n"
			self.serve_content(file_path, headers)
		else:
			self.request.send("HTTP/1.0 404 Not Found\r\n\r\n".encode())

if __name__ == "__main__":
	HOST, PORT = "localhost", 8080

	socketserver.TCPServer.allow_reuse_address = True
	# Create the server, binding to localhost on port 8080
	server = socketserver.TCPServer((HOST, PORT), MyWebServer)

	# Activate the server; this will keep running until you
	# interrupt the program with Ctrl-C
	server.serve_forever()
