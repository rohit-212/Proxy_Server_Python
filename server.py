#!/usr/bin/env python
import socket, sys
from thread import *

try:
    listening_port = int(raw_input("[*] Enter Listening Port Number: "))
except KeyboardInterrupt:
    print "\n[*] User Requested An Interrupt"
    print "[*] Application Exiting ..."
    sys.exit()

max_conn = 20 #Max Connections in Queue
buffer_size = 262144 # Max socket Buffer size



def start():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initiates socket
        s.bind(('', listening_port)) # Bind socket for listen
        s.listen(max_conn) # start listening for incoming connections
        print "[*] Initializing Sockets ... Done"
        print "[*] Sockets Binded succesfully ..."
        print("[*] Server started succesfully [ %d ]\n" % (listening_port))
    except Exception, e:
        print "[*] Unable to initialize socket", e
        sys.exit(2)

    while 1:
        try:
            conn, addr = s.accept() # Accept connection From client browser
            print "Connection accepted from browser"
            data = conn.recv(buffer_size) # Receive CLient Data
            print "Received request from browser"
            start_new_thread(conn_string, (conn, data, addr)) # start a thread
        except KeyboardInterrupt:
            print "\n[*] Proxy Server Shutting down ..."
            sys.exit(1)
    s.close()

def conn_string(conn, data, addr):
    # Client Browser Request Appears Here
    try:
        first_line = data.split('\n')[0]

        url = first_line.split(' ')[1]


        print "URL ", url

        http_pos = url.find("://") # find the position of ://
        if (http_pos == -1):
            temp = url
        else:
            temp = url[(http_pos+3):] # get the rest of the URL

        print "http pos, Temp", http_pos,  temp

        port_pos = temp.find(":") # Find the postion of port (if any)

        webserver_pos = temp.find("/") # Find the end of the web server

        if webserver_pos == -1:
            webserver_pos = len(temp)
        webserver = ""
        port = -1

        #print "Port pos, webserver_pos", port_pos, webserver_pos

        if (port_pos == -1 or webserver_pos < port_pos):  # default port
            port = 80
            webserver = temp[:webserver_pos]
        else:
            # Specific port
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]

        # print "WEB server", webserver
        print "Data extracted from request Request"


        proxy_server(webserver, port, conn, addr, data)
    except Exception, e:
        pass


def proxy_server(webserver, port, conn, addr, data):
    try:

        print "starting connection towebserver"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #print "connecing host", webserver, port

        s.connect((webserver, port))
        print "connected"
        #print "data", data
        s.send(data)
        print "Request sent"
        while 1:
            # Read reply or data to from end web server
            reply = s.recv(buffer_size)
            print "Reply Received ", reply
            if (len(reply) > 0):
                conn.send(reply) # send reply back to client
                # Send notification to proxy Server [script itself]

                dar = float(len(reply))
                dar = float(dar / 1024)
                dar = "%.3s" % (str(dar))
                dar = "%s KB" % (dar)
                print "[*] Request Done: %s => %s <=" % (str(addr[0]), str(dar))
            else:
                break
        s.close()
        conn.close()
        print "Conn CLosed ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    except socket.error, (value, message):
        print "Error", message
        s.close()
        conn.close()
        sys.exit(1)



start()
