#!/usr/bin/env python 

import SimpleHTTPServer
import SocketServer
import logging
import json
import sqlite3
import time

conn = sqlite3.connect("termite.sqlite")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS states(timestamp INTEGER, state TEXT, version INTEGER)""")
conn.commit()

insert_query = "INSERT INTO states VALUES (?,?,?)";
fetch_query = "SELECT state FROM states WHERE version = (SELECT MAX(version) FROM states)";
PORT = 8888

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        logging.error(self.headers)
        if self.path == '/state':
            print "THIS IS THE STATE REQ!\n"
            self.send_response(200)
            self.end_headers()

            # query for the latest saved state
            cursor.execute(fetch_query)
            response_string = cursor.fetchone();
            
            # if there's no saved state, return empty obj. Else, return the fetched info
            if response_string is None:
            	response_string = {};
            else:
                response_string = json.loads(response_string[0]);
            
            self.wfile.write(json.dumps(response_string))
        else:
	        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
    	print "THIS IS THE POST REQ!\n"
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(200)
        self.end_headers()
        
        # get received data and current timestamp
        data2 = json.loads(self.data_string)
        currentTime = int(round(time.time() * 1000));
		
		# insert new row into states db
        cursor.execute(insert_query, [(currentTime), (self.data_string), (data2["version"])])
        conn.commit();
        
        # return saved timestamp and version no.
        self.wfile.write(json.dumps("currentTime = " + str(currentTime) + ", version number = " + str(data2["version"])))
        
Handler = ServerHandler
httpd = SocketServer.TCPServer(("", PORT), Handler)
print "serving at port", PORT
httpd.serve_forever()
