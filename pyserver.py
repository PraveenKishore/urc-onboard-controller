# Python server that runs on Rover
# Specifications: Runs on Colibri T30
# Last Revision: 20 July 2016, 11:35 AM

# TODO:
# Logging?
# Remote Commands?
# Security?

import socket
import threading
import time
import random
import os
import serial

# Constants
FORWARD = 1
BACKWARD = 2
LEFT = 3
RIGHT = 4
FORWARD_LEFT = 5
FORWARD_RIGHT = 6
THROTTLE = 7
SENDING_PORT = 9876
RECEIVING_PORT = 9877

GPIO1 = 198
GPIO2 = 199
GPIO3 = 196

my_host = "192.168.1.5"   # local loopback is 127.0.0.1 or just say 
'localhost'
remote_host = "192.168.1.6"
USB_GPS_DEV = '/dev/ttyACM0'

# The variable which is used to halt the code in case of keyboard interrupt
globalKeepAlive = True

gpsSerial = serial.Serial()
gpsLatitude = ""
gpsLongitude = ""

# To update GPIO periodically, store the last direction update time
lastUpdateTime = time.time()

def setupGPIO():
    print("Acquiring GPIOs")
    os.system("echo " + str(GPIO1) + " > //sys//class//gpio//export")
    os.system("echo " + str(GPIO2) + " > //sys//class//gpio//export")
    os.system("echo " + str(GPIO3) + " > //sys//class//gpio//export")
    
    os.system("echo \"out\" > //sys//class//gpio//gpio" + str(GPIO1) + "//direction")
    os.system("echo \"out\" > //sys//class//gpio//gpio" + str(GPIO2) + "//direction")
    os.system("echo \"out\" > //sys//class//gpio//gpio" + str(GPIO3) + "//direction")

def writeGPIO(pin, value):
    global lastUpdateTime
    lastUpdateTime = time.time()
    # print(str(pin) + " >> " + str(value))
    os.system("echo " + str(value) + " > //sys//class//gpio//gpio" + str(pin) + "//value")

def freeGPIO():
    print("Releasing GPIOs")
    os.system("echo " + str(GPIO1) + " > //sys//class//gpio//unexport")
    os.system("echo " + str(GPIO2) + " > //sys//class//gpio//unexport")
    os.system("echo " + str(GPIO3) + " > //sys//class//gpio//unexport")

def updateGPIO():
    global globalKeepAlive
    global lastUpdateTime

    while globalKeepAlive:
        timeNow = time.time()
        if (timeNow - lastUpdateTime) > 0.2:
        	writeGPIO(GPIO1, 0)
        	writeGPIO(GPIO2, 0)
        	writeGPIO(GPIO3, 0)
        time.sleep(0.1)

def setupGPSUpdate():
    global gpsSerial

    gpsSerial = serial.Serial(USB_GPS_DEV, timeout=None, baudrate=9600)
    gpsSerial.flushInput()
    gpsSerial.flushOutput()

def updateGPS():
    global gpsSerial
    global gpsLatitute
    global gpsLongitude
    global globalKeepAlive
    
    while globalKeepAlive:
        data = str(gpsSerial.readline())
        print(data)

def releaseGPS():
    gpsSerial.close()

class Rover:
    def __init__(self):
        self.direction = 0  # For controller the direction of movement

    # To move the rover in the given direction. The directions are defined by integers
    # FORWARD = 1, BACKWARD = 2, LEFT = 3, RIGHT = 4
    def move(self, direction):
        # TODO: Implement the code!
	global ser
        if direction == FORWARD:
            print("FORWARD")
            writeGPIO(GPIO1, 0)
            writeGPIO(GPIO2, 0)
            writeGPIO(GPIO3, 1)
        elif direction == BACKWARD:
            print("BACKWARD")
            writeGPIO(GPIO1, 0)
            writeGPIO(GPIO2, 1)
            writeGPIO(GPIO3, 0)
        elif direction == LEFT:
            print("LEFT")
            writeGPIO(GPIO1, 0)
            writeGPIO(GPIO2, 1)
            writeGPIO(GPIO3, 1)
        elif direction == RIGHT:
            print("RIGHT")
            writeGPIO(GPIO1, 1)
            writeGPIO(GPIO2, 0)
            writeGPIO(GPIO3, 0)
        elif direction == FORWARD_LEFT:
            print("FORWARD LEFT")
            writeGPIO(GPIO1, 1)
            writeGPIO(GPIO2, 0)
            writeGPIO(GPIO3, 1)
        elif direction == FORWARD_RIGHT:
            print("FORWARD RIGHT")
            writeGPIO(GPIO1, 1)
            writeGPIO(GPIO2, 1)
            writeGPIO(GPIO3, 0)
        elif direction == THROTTLE:
            print("THROTTLE")
            writeGPIO(GPIO1, 1)
            writeGPIO(GPIO2, 1)
            writeGPIO(GPIO3, 1)
        return
    # end of move()

    # Stops the movement of the rover, i.e., halts the rover
    def halt(self):
        # TODO: Implement halting function!
        return
    # end of halt()

# end of class Rover

# Establishes and manages the connections between the devices, i.e., the on-board server and base station
class CommunicationServer:
    def __init__(self):
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # The variable which is used to halt the code in case of keyboard interrupt
        self.keepAlive = True
        global my_host
        global remote_host
        self.myHost = my_host
        self.remoteHost = remote_host
        self.sendFailCount = 0
        self.rover = Rover()

    # Handles incoming connection. All received data is processed here
    def handleClient(self, client, address):

        while self.keepAlive:
            try:
                data = client.recv(1024)
                if not data:    # If data is None, connection has ended
                    break   # breaks out of while loop
                message = str(data.decode()).strip()
                # The data should be enclosed within {}
                if message.startswith('{') and message.endswith('}'): # Check integrity of the data received
                    message = message.strip('}')  # Discard { }
                    message = message.strip('{')
                    message = message.strip()
                    # print("Received from client(" + address[0] + "): " + message)
                    if message.startswith("CONTROL-"):
                        controlStrings = message.split('CONTROL-')
                        # print("MOVE: " + controlStrings[1]) # controlStrings[0] is 'CONTROL-' << This is for debugging
                        if controlStrings[1] == "UP":
                            self.rover.move(FORWARD)
                        elif controlStrings[1] == "DO":
                            self.rover.move(BACKWARD)
                        elif controlStrings[1] == "LE":
                            self.rover.move(LEFT)
                        elif controlStrings[1] == "RI":
                            self.rover.move(RIGHT)
                        elif controlStrings[1] == "UR":
                            self.rover.move(FORWARD_RIGHT)
                        elif controlStrings[1] == "UL":
                            self.rover.move(FORWARD_LEFT)
                        elif controlStrings[1] == "CE":
                            self.rover.move(THROTTLE)
                else:
                    print("Invalid data received from client(" + address[0] + "): " + message)
            except Exception as e:
                client.close()
                print("Error while receiving: " + str(e))
                break   # breaks out of while loop. If this is not written, while loop continues even after exception

        print("Disconnected from " + address[0])
    # end of handleClient()

    # Used to accept connections from the base station. Usually started as a thread.
    def startListening(self):
        global RECEIVING_PORT
        print("Started Listening at " + self.myHost)
        self.serverSock.bind((self.myHost, RECEIVING_PORT))
        self.serverSock.listen(5)  # Handles utmost 5 clients simultaneously
        self.serverSock.settimeout(2)
        while self.keepAlive:    # When this flag is false, while breaks. keepAlive is global
            try:
                (client, address) = self.serverSock.accept()
                print("Accepted connection from: " + address[0])
                threading.Thread(target=self.handleClient, args=(client, address)).start()
            except socket.timeout as t: # Ignore timeouts
                pass
        # while ended, time to cleanup and shutdown the listening socket
        self.serverSock.shutdown(socket.SHUT_RDWR)
        self.serverSock.close()

    # Sends the string over the specified socket. Returns 0 if successful, else 1
    # If the send fails more than 3 times, the socket tries to reinitialize itself
    def send(self, string):
        global SENDING_PORT
        try:
            self.clientSock.connect((self.remoteHost, SENDING_PORT))   # Attempt to connect, if its already connected an exception is thrown
            print("Connected to: " + self.remoteHost)
        except Exception as e:      # Ignore the exception thrown if the socket is already connected
            pass
        try:
            self.clientSock.send(str(string).encode())
            self.sendFailCount = 0  # Sent successfully, reset the counter
            return 0
        except Exception as e:  # If send failed
            print("Could not send data: " + str(e))
            self.sendFailCount += 1       # Send failed, increment the counter

            if(self.sendFailCount > 3):  # Enough, sending failed for 3 times, try reinitializing the socket
                self.sendFailCount = 0
                self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # print("Socket reinitialized since it failed too many times")
            return 1
    # end of send()
    
    # Stops listening to the clients by turning off keepAlive
    def stop(self):
        self.keepAlive = False
        self.clientSock.shutdown(socket.SHUT_RDWR)
        self.clientSock.close()
    # serverSock will be shutdown automatically in startListening()

# end of class CommunicationServer

if __name__ == "__main__":

    comm = CommunicationServer();
    setupGPIO();
    # setupGPSUpdate();

    threading.Thread(target=updateGPIO, args=()).start()
    # threading.Thread(target=updateGPS, args()).start()    
    # Update GPIOs to 0 continuously
    try:
        threading.Thread(target=comm.startListening, args=()).start() # Receiver thread

        # Code to continuously send data
        while globalKeepAlive:
            comm.send("{SENSOR-" + str(10) + ":" + str(20) + ":" + str(30) + ":" + str(40) + "}")
            time.sleep(1)
        # while ended, time to cleanup
    except KeyboardInterrupt as e:  # Oh, the user wants to stop the program! Pressed Ctrl+C
        print("Shutting down Base station server....")
        freeGPIO();
        globalKeepAlive = False
        comm.stop()
