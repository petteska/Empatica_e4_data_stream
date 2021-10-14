#!/usr/bin/env python3

from os import chdir, mkdir, stat
from pathlib import Path
import csv
import socket

import threading

import time
from typing import Sized, Text


HOST = '127.0.0.1'      # Localhost
PORT = 28000            # The port that E4 streaming server is sending to
BUFFER_SIZE = 4096      # Buffer size of messages

# DEVICE_ID = '3BD111'    # Device A02DE7

# Devices
DEVICE_LIST = []

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


def connect_server():
    # Create a TCP connection with HOST on PORT
    # Creates a global object s of type socket. 

    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        s.connect((HOST,PORT))
        return True
    except:
        return False

def update_device_list():
    global DEVICE_LIST
    try:
        s.send("device_list\r\n".encode())
        response = s.recv(BUFFER_SIZE).decode("utf-8")
        device_list = response.split("|")
        if (len(device_list)>1):
            device_list = device_list[1:]
            for i in range(len(device_list)):
                device_list[i] = device_list[i].split(" ")[1]
        else:
            device_list = []

        DEVICE_LIST = device_list
        return True
    except:
        return False

def check_streaming_server_response(response):
    # checks if the streaming server response ends with "OK".
    # Args:
    #   response: string
    try:
        if(response.split(" ")[-1][0:2] == "OK"):
            return True
        else:
            return False
    except TypeError:
        print("\tSYSTEM_ERROR: got wrong type!")


def connect_device(device_ID):
    # Create a connection to specified device.
    # Connection to server needed to run.
    
    try:
        s.send(("device_connect " + device_ID + "\r\n").encode())
        response = s.recv(BUFFER_SIZE).decode("utf-8")
        if(not check_streaming_server_response(response)):
            print("\tFailed to connect to device!")
            return False

        s.send("pause ON \r\n".encode())
        response = s.recv(BUFFER_SIZE)
        return True
    except TypeError:
        print("\tSYSTEM_ERROR: got wrong type!")
    except:
        return False

    

def disconnect():
    try:
        print("Trying to disconnect")
        s.send(("device_disconnect" + "\r\n").encode())
        print("Now I am here!")
        response = s.recv(BUFFER_SIZE)

        return True
    except:
        return False

def setup_subscribers():
    # Create subscribers for the data to be streamed
    global ACC, BVP, GSR, IBI, TMP
    try:
        if ACC:
            s.send(("device_subscribe acc ON \r\n").encode())
            response = s.recv(BUFFER_SIZE).decode("utf-8")
            if(not check_streaming_server_response(response)):
                print("\tFailed to subscribe to ACC\n")
                print("response\n" + response)

        if BVP:
            s.send(("device_subscribe bvp ON \r\n").encode())
            response = s.recv(BUFFER_SIZE).decode("utf-8")
            if(not check_streaming_server_response(response)):
                print("\tFailed to subscribe to BVP\n")
                print("\tresponse\n" + response)


        if GSR:
            s.send(("device_subscribe gsr ON \r\n").encode())
            response = s.recv(BUFFER_SIZE).decode("utf-8")
            if(not check_streaming_server_response(response)):
                print("\tFailed to subscribe to GSR\n")

        if IBI:
            s.send(("device_subscribe ibi ON \r\n").encode())
            response = s.recv(BUFFER_SIZE).decode("utf-8")
            if(not check_streaming_server_response(response)):
                print("\tFailed to subscribe to IBI\n")

        if TMP:
            s.send(("device_subscribe tmp ON \r\n").encode())
            response = s.recv(BUFFER_SIZE).decode("utf-8")
            if(not check_streaming_server_response(response)):
                print("\tFailed to subscribe to TMP\n")
        return True
    except:

        return False



def reconnect():
    connect_server()
    connect_device(DEVICE_ID)
    setup_subscribers()



def setup_files():
    # Create folders and files for saving the streamed data.
    # Data will be saved in .csv files by the use of global objects of type csv.writer()
    # Creates the following global objects:
    # - acc_data_writer - type csv.writer
    # - bvp_data_writer - type csv.writer
    # - gsr_data_writer - type csv.writer
    # - ibi_data_writer - type csv.writer
    # - tmp_data_writer - type csv.writer
    try:
        parent_dir = Path("./" + "data/" + SUBJECT_ID + "/")

        parent_dir.mkdir(parents=True, exist_ok=True)

        # print("Directory " + "\"" + "./" + SUBJECT_ID + "/" + "Data/" + "\"" + " created")


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
        
        return True
    except:
        return False

        

    

def stream():
    # print("Starting streaming")
    # Starts the stream and saves the incomming data in the correct .csv files.
    global STREAMING
    STREAMING = True
    s.send("pause OFF \r\n".encode())
    try:
        while(STREAMING):
            try:
                # print("Trying to get response")
                response = s.recv(BUFFER_SIZE).decode("utf-8")
                # print("Got response")
                if "connection lost to device" in response:
                    reconnect()
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
                        # print("IBI")

                    if stream_type == "E4_Hr":
                        timestamp = float(samples[i].split()[1].replace(',','.'))
                        data = float(samples[i].split()[2].replace(',','.'))
                        hr_data_writer.writerow([timestamp,data])
                        # print("HR")

                    if stream_type == "E4_Gsr":
                        timestamp = float(samples[i].split()[1].replace(',','.'))
                        data = float(samples[i].split()[2].replace(',','.'))
                        gsr_data_writer.writerow([timestamp,data])

                    if stream_type == "E4_Temperature":
                        timestamp = float(samples[i].split()[1].replace(',','.'))
                        data = float(samples[i].split()[2].replace(',','.'))
                        tmp_data_writer.writerow([timestamp,data])
                # print("Data registered")
            except socket.timeout:
                print("Socket timeout")
                reconnect()
                break
        else:
            print("\tDisconnecting from device\n")
            s.send("device_disconnect\r\n".encode())
            s.close()
    except KeyboardInterrupt:
        print("\tDisconnecting from device\n")
        s.send("device_disconnect\r\n".encode())
        s.close()




## Helper functions
def print_list(list_to_print, pre = "", post = ""):
    # Print each element in a list with pre before each element and post after
    # Args:
    #   list_to_print: list of strings
    #   pre: string
    #   post: string


    for element in list_to_print:
        print(pre + str(element) + post)

def print_subscribers(pre = "", post = ""):
    if(ACC):
        print(pre + "ACC" + post)
    if(BVP):
        print(pre + "BVP" + post)
    if(GSR):
        print(pre + "GSR" + post)
    if(IBI):
        print(pre + "IBI" + post)
    if(TMP):
        print(pre + "TMP" + post)

def divider():
    print("\n==============================================================================================================\n")


def get_specific_input(text, possible_answers):
    # Will ask for an input until one of possible answers are given
    # Args:
    #   text: string
    #   possible_answers: list of strings

    possible_answers = [elt.lower() for elt in possible_answers]
    answer = input(text)
    while(answer.lower() not in possible_answers):
        answer = input(text)
    return answer


def get_streaming_input():
    global STREAMING
    streaming_input = input("Enter 'stopp' if you want to stopp the recording. Note that this will end the script, terminating the program: ")
    while(streaming_input.lower() !="stopp"):
        streaming_input = input("Enter 'stopp' if you want to stopp the recording. Note that this will end the script, terminating the program: ")
    else:
        print("\tStopping stream!\n")
        STREAMING = False
    time.sleep(0.5)
    get_specific_input("The program is now finished. Enter 'close' to close the window: ",["close"])


def main():
    global STATUS_CONNECTION_SERVER, STATUS_CONNECTION_DEVICE, STATUS_STREAMING, DEVICE_LIST, SUBJECT_ID
    
    divider()
    
    print("Welcome to this connection interface for the Empatica E4 with the E4 Live server.")
    
    divider()
    print("First, we want you to enter a unique ID for this session.")
    print("All data collected during this experiment will be saved under './data/{ID}'\n")
    SUBJECT_ID = input("Please enter the unique ID: ")

    divider()

    print("You should now open the Empatica E4 streaming server. If you do not have it installed already, you can find a link with more information in the Readme.md file.\n")
    
    while(True):
        get_specific_input("Type 'connect' when you are ready to connect to the server: ", ["connect"])

        print("\n\tConnecting to server")
        if(connect_server()):
            STATUS_CONNECTION_SERVER = True
            print("\tConnection to server successfull!\n")
            
            break
        else:
            STATUS_CONNECTION_SERVER = False
            print("\tERROR: Something went wrong when trying to connect to the server. Make sure you have opened the E4 streaming server.\n")
        
    divider()

    print("Next, you should connect the Empatica E4 to the streaming server using the BTLE dongle.")
    print("Remember that you need to have the device turned on to be able to connect to the streaming server.\n")

    get_specific_input("Enter 'update' when the device is connected to show an uppdated list of devices: ",["update"])

    print("\tUpdating device list\n")

    if(not update_device_list()):
        print("\n\tSomething went wrong when updating device list!\n")
    else:
        print("\n\tAvailable devices:")
        print_list(DEVICE_LIST, pre = "\t - ")
    
    print("\n")    
    
    device = input("Specify which device you wish to connect to: ").upper()
    
    while(device.upper() not in DEVICE_LIST):
        print(f"\tWARNING: Device {device} is not available. Choose one of the devices from the following list:\n")
        print("\tAvailable devices")
        print_list(DEVICE_LIST, pre = "\t - ")
        print("\n")
        device = input("Specify which device you wish to connect to: ").upper()
    
    print(f"\n\tDevice {device} selected. Trying to connect.")
    while(not connect_device(device)):
        print("\tERROR: Something went wrong when connecting to device!\n")
        answer = get_specific_input("Would you try to connect again? [y/n] ",["y","n"])
        if(answer == "y"):
            continue
        else:
            return


    
    print(f"\tConnection to {device} successfull!\n")
            
    print("\tSetting up subscribers and files\n")
    if (not setup_subscribers()):
        print("\tERROR: Something went wrong when setting up the subscribers.\n")
        return
    
    if (not setup_files()):
        print("\tERROR: Something went wrong when setting up files\n")
        return

    print("\tSubscribers and files are ready. The system is now subscribing to:")
    print_subscribers(pre="\t - ")

    divider()
    
    print("You are now ready to start streaming.\n")

    get_specific_input("Enter 'start' to start streaming: ", ["start"])

    print("\n\tStreaming is starting.\n")
    stream_thread = threading.Thread(target=stream, args=())
    stream_thread.start()

    print("\tStreaming started.\n")

    input_thread = threading.Thread(target=get_streaming_input, args=())

    input_thread.start()

            

main()

