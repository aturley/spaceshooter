from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse, parse_qs
from subprocess import call
import SocketServer
import osc
import random
import json
import socket
import sys

class Drummers(object):
    def __init__(self):
        self.drummer_map = {}
        self.num_pads = 16
        self.drum_width = 400
        self.drum_height = 200
        self.drum_layout = (8, 2) #8 wide, two high
    def add_touches(self, ip_address, coords):
        self.drummer_map[ip_address] = coords
    def get_total_hits(self):
        hits = [0] * self.num_pads
        for coords in self.drummer_map.values():
            for c in coords:
                p = self.coord_to_pad(c)
                if (p >= 0 and p < (self.drum_layout[0] * self.drum_layout[1])):
                    hits[self.coord_to_pad(c)] += 1
        return hits
    def coord_to_pad(self, c):
        pix_per_pad_w = self.drum_width / self.drum_layout[0]
        pix_per_pad_h = self.drum_height / self.drum_layout[1]
        column = c[0] // pix_per_pad_w
        row = c[1] // pix_per_pad_h
        pad = row * self.drum_layout[0] + column
        return pad

drummers = Drummers()

def handle_input(input, ipAddress):
    for evt in input:
        if evt['elementId'] == "touchmove":
            if evt['action'] == "MultitouchTouchList":
                osc.sendMsg("/movestart", [ipAddress, evt['coords'][0][0], evt['coords'][0][1]] , "127.0.0.1", 9002)
            if evt['action'] == "MultitouchTouchListEnd":
                osc.sendMsg("/moveend", [ipAddress, evt['coords'][0][0], evt['coords'][0][1]] , "127.0.0.1", 9002)
        if evt['elementId'] == "touchshoot":
            if evt['action'] == "MultitouchTouchList":
                osc.sendMsg("/shootstart", [ipAddress, evt['coords'][0][0], evt['coords'][0][1]] , "127.0.0.1", 9002)
            if evt['action'] == "MultitouchTouchListEnd":
                osc.sendMsg("/shootend", [ipAddress, evt['coords'][0][0], evt['coords'][0][1]] , "127.0.0.1", 9002)
        if evt['elementId'] == "drumpad":
            if evt['action'] == "MultitouchTouchList":
                drummers.add_touches(ipAddress, evt['coords'])
                hits = drummers.get_total_hits()
                print "hits =", hits, len(hits)
                osc.sendMsg("/drumhitlist", [int(h) for h in hits], "127.0.0.1", 6767)
                osc.sendMsg("/drumhitlist", [int(h) for h in hits], "127.0.0.1", 6768)
            if evt['action'] == "MultitouchTouchNone":
                print "got none!"
                drummers.add_touches(ipAddress, [])
                hits = drummers.get_total_hits()
                print "hits =", hits, len(hits)
                osc.sendMsg("/drumhitlist", [int(h) for h in hits], "127.0.0.1", 6767)
                osc.sendMsg("/drumhitlist", [int(h) for h in hits], "127.0.0.1", 6768)
        if evt['elementId'] == "drumpadc":
            print "touish:", evt

class ThreadedHTTPServer(SocketServer.ThreadingMixIn, HTTPServer):
    daemon_threads = True
    pass

move_id = 0
PORT = 8080

if len(sys.argv) == 2:
    PORT = int(sys.argv[1])

class MyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if (True):
            try:
                clen = int(self.headers.getheader('content-length'))
                incoming = self.rfile.read(clen)
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write("ok")
                incoming_parsed = json.loads(incoming)
                handle_input(incoming_parsed, self.address_string())
            except IOError:
                self.send_error(404,'File Not Found: %s' % self.path)

    def do_GET(self):
        # print "got a request from", self.address_string()
        if (self.path in ["/demo-game.html", "/demo-drum.html", "/touchlib.js", "/"]):
            try:
                if (self.path == "/"):
                    self.path = "/demo-game.html"
                f = open(curdir + sep + self.path) #self.path has /test.html
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
            except IOError:
                self.send_error(404,'File Not Found: %s' % self.path)
        else:
            self.send_error(404,'File Not Found: %s' % self.path)

def main():
    try:
        # server = HTTPServer(('', PORT), MyHandler)
        server = ThreadedHTTPServer(('', PORT), MyHandler)
        print 'Welcome to the machine...(%s:%d)'%(socket.gethostbyname(socket.gethostname()), PORT)
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    osc.init()
    main()
