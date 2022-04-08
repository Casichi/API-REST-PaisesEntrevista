import http.server
import socketserver
import json
import pandas
import sqlite3
import time
import random
import os
import hashlib
import requests


class ServiceHandler(http.server.SimpleHTTPRequestHandler):
    # Get mothod
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text-json")
            self.end_headers()

            #Get all countries
            url = "https://rapidapi.com/apilayernet/api/rest-countries-v1"



class ReuseAddrTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


PORT = 9000
myserver = ReuseAddrTCPServer(("", PORT), ServiceHandler)
myserver.daemon_threads = True
print(f'Server started at http://127.0.0.1:{PORT}/')
try:
    myserver.serve_forever()
except:
    print("Closing the server")
    myserver.server_close()

