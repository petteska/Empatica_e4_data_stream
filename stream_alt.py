#!/usr/bin/env python3

from os import chdir, mkdir, stat
from pathlib import Path
import csv
import socket

import time
from typing import Sized, Text

from stream import CONNECTION_SERVER

HOST = '127.0.0.1'      # Localhost
PORT = 28000            # The port that E4 streaming server is sending to
BUFFER_SIZE = 4096      # Buffer size of messages

DEVICE_ID = '3BD111'    # Device A02DE7

# Select which data to stream
ACC = True              # 3-axis acceleration
BVP = True              # Blood volume pressure
GSR = True              # Galvanic skin response
IBI = True              # Interbeat interval, also includes heart rate
TMP = True              # Skin temperature

# Experiment meta data
SUBJECT_ID = "Experiment_" + str(1)

# Status variables
STATUS_CONNECTION_SERVER = False
STATUS_CONNECTION_DEVICE = False
STREAMING_INITIALIZED = False

STATUS_STREAMING = False


def connect_server(device_ID):
    # Create a TCP connection with HOST on PORT
    # Creates a global object s of type socket. 

    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    global STATUS_CONNECTION_SERVER 
    
    try:
        print("Connecting to server")
        s.connect((HOST,PORT))
        print("Connection to server established")
        CONNECTION_SERVER= True

        print("Devices available:")
        s.send("device_list\r\n".encode())
        response = s.recv(BUFFER_SIZE)
        print(response.decode("utf-8"))

        
        return True
    except:
        print("An error occured during connection")
        return False

def connect_device(device_ID):
    # Create a connection to specified device.
    # Connection to server needed to run.

    global STATUS_CONNECTION_DEVICE
    
    try:
        print("Connecting to device " + device_ID)
        s.send(("device_connect " + device_ID + "\r\n").encode())
        response = s.recv(BUFFER_SIZE)
        print(response.decode("utf-8"))

        s.send("pause ON \r\n".encode())
        response = s.recv(BUFFER_SIZE)
        print(response.decode("utf-8"))

        CONNECTION_DEVICE = True
    except:
        print("An error occured during connection to device.")
        return False

    

def disconnect():
    global CONNECTION_DEVICE
    try:
        print("Trying to disconnect")
        s.send(("device_disconnect" + "\r\n").encode())
        print("Now I am here!")
        response = s.recv(BUFFER_SIZE)
        print(response.decode("utf-8"))

        CONNECTION_DEVICE = False
    except:
        print("An error occured during disconnection")
    print(CONNECTION_DEVICE)


def setup_subscribers():
    # Create subscribers for the data to be streamed
    try:
        if ACC:
            print("Starting acc stream")
            s.send(("device_subscribe acc ON \r\n").encode())
            response = s.recv(BUFFER_SIZE)
            print(response.decode("utf-8"))

        if BVP:
            print("Starting bvp stream")
            s.send(("device_subscribe bvp ON \r\n").encode())
            response = s.recv(BUFFER_SIZE)
            print(response.decode("utf-8"))

        if GSR:
            print("Starting gsr stream")
            s.send(("device_subscribe gsr ON \r\n").encode())
            response = s.recv(BUFFER_SIZE)
            print(response.decode("utf-8"))

        if IBI:
            print("Starting ibi stream")
            s.send(("device_subscribe ibi ON \r\n").encode())
            response = s.recv(BUFFER_SIZE)
            print(response.decode("utf-8"))

        if TMP:
            print("Starting tmp stream")
            s.send(("device_subscribe tmp ON \r\n").encode())
            response = s.recv(BUFFER_SIZE)
            print(response.decode("utf-8"))

        return True
    except:

        return False



# def reconnect():
#     connect()
#     setup_subscribers()



def setup_files():
    # Create folders and files for saving the streamed data.
    # Data will be saved in .csv files by the use of csv.writer()
    # Creates the following global objects:
    # - acc_data_writer - type csv.writer
    # - bvp_data_writer - type csv.writer
    # - gsr_data_writer - type csv.writer
    # - ibi_data_writer - type csv.writer
    # - tmp_data_writer - type csv.writer

    parent_dir = Path("./" + "data/" + SUBJECT_ID + "/")

    parent_dir.mkdir(parents=True, exist_ok=True)

    print("Directory " + "\"" + "./" + SUBJECT_ID + "/" + "Data/" + "\"" + " created")


    if ACC:
        global acc_data 
        acc_data = open(parent_dir.joinpath("acc_data.csv"), "w")
        global acc_data_writer 
        acc_data_writer = csv.writer(acc_data)
        acc_header = ["timestamp","x","y","z"]
        acc_data_writer.writerow(acc_header)

    if BVP:
        global bvp_data 
        bvp_data = open(parent_dir.joinpath("bvp_data.csv"), "w")
        global bvp_data_writer 
        bvp_data_writer = csv.writer(bvp_data)
        bvp_header = ["timestamp","BVP"]
        bvp_data_writer.writerow(bvp_header)

    if GSR:
        global gsr_data 
        gsr_data = open(parent_dir.joinpath("gsr_data.csv"), "w")
        global gsr_data_writer 
        gsr_data_writer = csv.writer(gsr_data)
        gsr_header = ["timestamp","GSR"]
        gsr_data_writer.writerow(gsr_header)

    if IBI:
        global ibi_data 
        ibi_data = open(parent_dir.joinpath("ibi_data.csv"), "w")
        global ibi_data_writer 
        ibi_data_writer = csv.writer(ibi_data)
        ibi_header = ["timestamp","IBI"]
        ibi_data_writer.writerow(ibi_header)

        global hr_data 
        hr_data = open(parent_dir.joinpath("hr_data.csv"), "w")
        global hr_data_writer 
        hr_data_writer = csv.writer(hr_data)
        hr_header = ["timestamp","HR"]
        hr_data_writer.writerow(hr_header)

    if TMP:
        global tmp_data 
        tmp_data = open(parent_dir.joinpath("tmp_data.csv"), "w")
        global tmp_data_writer 
        tmp_data_writer = csv.writer(tmp_data)
        tmp_header = ["timestamp","Tmp"]
        tmp_data_writer.writerow(tmp_header)
    
    print("File setup complete")
    return True



def stream(root):
    print("Starting streaming")
    # Starts the stream and saves the incomming data in the correct .csv files.
    s.send("pause OFF \r\n".encode())
    try:
        print()
        while(True):
            try:
                # print("Trying to get response")
                response = s.recv(BUFFER_SIZE).decode("utf-8")
                # print("Got response")
                if "connection lost to device" in response:
                    # reconnect()
                    break

                samples = response.split("\n")
                for i in range(len(samples)-1):
                    stream_type = samples[i].split()[0]
                    if stream_type == "E4_Acc":
                        timestamp = float(samples[i].split()[1].replace(',','.'))
                        data = [int(samples[i].split()[2].replace(',','.')), int(samples[i].split()[3].replace(',','.')), int(samples[i].split()[4].replace(',','.'))]
                        acc_data_writer.writerow([timestamp] + data)

                    if stream_type == "E4_Bvp":
                        timestamp = float(samples[i].split()[1].replace(',','.'))
                        data = float(samples[i].split()[2].replace(',','.'))
                        bvp_data_writer.writerow([timestamp,data])

                    if stream_type == "E4_Ibi":
                        timestamp = float(samples[i].split()[1].replace(',','.'))
                        data = float(samples[i].split()[2].replace(',','.'))
                        ibi_data_writer.writerow([timestamp,data])
                        print("IBI")

                    if stream_type == "E4_Hr":
                        timestamp = float(samples[i].split()[1].replace(',','.'))
                        data = float(samples[i].split()[2].replace(',','.'))
                        hr_data_writer.writerow([timestamp,data])
                        print("HR")

                    if stream_type == "E4_Gsr":
                        timestamp = float(samples[i].split()[1].replace(',','.'))
                        data = float(samples[i].split()[2].replace(',','.'))
                        gsr_data_writer.writerow([timestamp,data])

                    if stream_type == "E4_Temperature":
                        timestamp = float(samples[i].split()[1].replace(',','.'))
                        data = float(samples[i].split()[2].replace(',','.'))
                        tmp_data_writer.writerow([timestamp,data])
                print("Data registered")
            except socket.timeout:
                print("Socket timeout")
                # reconnect()
                # break
            root.after(100, stream(root))
        
    # root.after(100,stream(root))
    except KeyboardInterrupt:
        print("Disconnecting from device")
        s.send("device_disconnect\r\n".encode())
        s.close()



def main():
   print("Welcome to this connection interface.")
   connection = input("Type 'connect' when you are ready to connect to the server")
   while(connection.lower() != "connect"):
       connection = input("Type 'connect' when you are ready to connect to the server")
       
   while(not CONNECTION_SERVER):
       connect_server()

main()

