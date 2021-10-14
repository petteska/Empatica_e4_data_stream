#!/usr/bin/env python3

from os import chdir, mkdir, stat
from pathlib import Path
import csv
import socket
import tkinter as tk
from tkinter import ttk
from guiLoop import guiLoop
import time
from tkinter import font
from tkinter.constants import BOTTOM, DISABLED, END, INSERT, LAST, LEFT, NORMAL, SEPARATOR, TOP, W
from typing import Sized, Text

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
CONNECTION_SERVER = False
CONNECTION_DEVICE = False
STREAMING_INITIALIZED = False

STREAMING = False


def connect():
    # Create a TCP connection with HOST on PORT
    # Creates a global object s of type socket. 

    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    global CONNECTION_SERVER 
    global CONNECTION_DEVICE
    
    try:
        print("Connecting to server")
        s.connect((HOST,PORT))
        print("Connection to server established")
        CONNECTION_SERVER= True

        print("Devices available:")
        s.send("device_list\r\n".encode())
        response = s.recv(BUFFER_SIZE)
        print(response.decode("utf-8"))

        print("Connecting to device " + DEVICE_ID)
        s.send(("device_connect " + DEVICE_ID + "\r\n").encode())
        response = s.recv(BUFFER_SIZE)
        print(response.decode("utf-8"))

        s.send("pause ON \r\n".encode())
        response = s.recv(BUFFER_SIZE)
        print(response.decode("utf-8"))

        CONNECTION_DEVICE = True
        return True
    except:
        print("An error occured during connection")
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



def reconnect():
    connect()
    setup_subscribers()



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


# @guiLoop
def stream(root):
    print("Starting streaming")
    # Starts the stream and saves the incomming data in the correct .csv files.
    s.send("pause OFF \r\n".encode())
    try:
        print()
        # while(True):
        try:
            try:
                # print("Trying to get response")
                response = s.recv(BUFFER_SIZE).decode("utf-8")
                # print("Got response")
                if "connection lost to device" in response:
                    reconnect()
                    # break

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
                reconnect()
                # break
            root.after(100, stream(root))
        except:
            print("Something failed")
        
    # root.after(100,stream(root))
    except KeyboardInterrupt:
        print("Disconnecting from device")
        s.send("device_disconnect\r\n".encode())
        s.close()



def main():
    root = tk.Tk()
    root.title("Empatica E4 connect")

    # H1
    header_frame = tk.Frame(root)
    header_frame.grid(row=0, sticky=tk.N)
    label_H1 = tk.Label(header_frame, text="Welcome to the connection GUI for the Empatica E4", font="Helvetica 18 bold")
    label_H1.grid(column=0, row=0, ipadx=5,  pady=10, padx=10, sticky=tk.W + tk.N)


    # # Select measurements:
    # ## Header
    # select_measurements_frame = tk.Frame(root)
    # select_measurements_frame.grid(column=0, row=1, ipadx=5, pady=10, padx=10, sticky=tk.W + tk.N)

    # label_select_measurements = tk.Label(select_measurements_frame, text="Select which measurements to use:", font="Helvetica 12 bold")
    # label_select_measurements.grid(column=0, row=0, ipadx=5, pady=5, sticky=tk.W)

    # ## Select
    # option_acc = tk.IntVar()
    # option_bvp = tk.IntVar()
    # option_gsr = tk.IntVar()
    # option_ibi = tk.IntVar()
    # option_tmp = tk.IntVar()
    # chk_acc = tk.Checkbutton(select_measurements_frame, text="ACC", variable=option_acc, onvalue=True, offvalue=False)
    # chk_bvp = tk.Checkbutton(select_measurements_frame, text="BVP", variable=option_bvp, onvalue=True, offvalue=False)
    # chk_gsr = tk.Checkbutton(select_measurements_frame, text="GSR", variable=option_gsr, onvalue=True, offvalue=False)
    # chk_ibi = tk.Checkbutton(select_measurements_frame, text="IBI", variable=option_ibi, onvalue=True, offvalue=False)
    # chk_tmp = tk.Checkbutton(select_measurements_frame, text="TMP", variable=option_tmp, onvalue=True, offvalue=False)
    # chk_acc.grid(column=0,row=1, sticky=tk.W)
    # chk_bvp.grid(column=0,row=2, sticky=tk.W)
    # chk_gsr.grid(column=0,row=3, sticky=tk.W)
    # chk_ibi.grid(column=0,row=4, sticky=tk.W)
    # chk_tmp.grid(column=0,row=5, sticky=tk.W)

    # ## Check_all button
    # def check_all():
    #     chk_acc.select()
    #     chk_bvp.select()
    #     chk_gsr.select()
    #     chk_ibi.select()
    #     chk_tmp.select()

    # button_check_all = tk.Button(select_measurements_frame, text="Check all", command=check_all)
    # button_check_all.grid(column=0, row=6, ipadx=5, pady=5, sticky=tk.W)


    # def choose_selected():
    #     global ACC, BVP, GSR, IBI, TMP

    #     ACC = option_acc.get()
    #     BVP = option_bvp.get()
    #     GSR = option_gsr.get()
    #     IBI = option_ibi.get()
    #     TMP = option_tmp.get()

    #     unlock_task_info()
    #     task_info.insert('1.0',"Sucessfully set the chosen measurements. Currently the settings are (True = Chosen, False = not chosen):\n")
    #     task_info.insert('2.0', "ACC: " + str(bool(ACC)) + "\n")
    #     task_info.insert('3.0', "BVP: " + str(bool(BVP)) + "\n")
    #     task_info.insert('4.0', "GSR: " + str(bool(GSR)) + "\n")
    #     task_info.insert('5.0', "IBI: " + str(bool(IBI)) + "\n")
    #     task_info.insert('6.0', "TMP: " + str(bool(TMP)) + "\n\n")
    #     lock_task_info()

    # button_choose_selection = tk.Button(select_measurements_frame, text="Choose selected", command=choose_selected)
    # button_choose_selection.grid(column=0, row=7, ipadx=5, pady=5, sticky=tk.W)



    # Connection buttons
    connection_button_frame = tk.Frame(root)
    connection_button_frame.grid(row=3, padx=10, pady=10, sticky=tk.W)
   
    ## Header
    label_connection_button = tk.Label(connection_button_frame,text="Press the button below to connect to or disconnect from the Empatica E4." , font="Helvetica 12 bold")
    label_connection_button.grid(row=0, columnspan=4)
   
    ## Disconnect button
    def disconnect_button_handler():
        if(disconnect()):
            unlock_task_info()
            task_info.insert('1.0',"Successfully disconnected from device\n\n")
            lock_task_info()
        else:
            unlock_task_info()
            task_info.insert('1.0',"Disconnection to device failed. Make sure the device is turned on and connected to the E4 Live Server.\n\n")
            lock_task_info()

    button_disconnect = tk.Button(connection_button_frame,text="Disconnect", command=disconnect_button_handler)
    button_disconnect.grid(column=0, row=1, ipadx=5, pady=5, sticky=tk.W)


    ## Connect button
    def connect_button_handler():
        if(connect()):
            unlock_task_info()
            task_info.insert('1.0',"Successfully connected to device\n\n")
            lock_task_info()
        else:
            unlock_task_info()
            task_info.insert('1.0',"Connection to device failed. Make sure the device is turned on and connected to the E4 Live Server.\n\n")
            lock_task_info()

    button_connect = tk.Button(connection_button_frame,text="Connect", command=connect_button_handler)
    button_connect.grid(column=1, row=1, ipadx=5, pady=5, sticky=tk.W)

    # Prepare for streaming
    streaming_init_frame = tk.Frame(root)
    streaming_init_frame.grid(row=4, padx=10, pady=10, sticky=tk.W)
   
    ## Header
    label_streaming_init_button = tk.Label(streaming_init_frame,text="Press the button below to initialize the streaming." , font="Helvetica 12 bold")
    label_streaming_init_button.grid(row=0, columnspan=4)

    def streaming_init_handler():
        global STREAMING_INITIALIZED
        if(setup_subscribers()):
            setup_files()
            unlock_task_info()
            task_info.insert('1.0', "Preparation successfull. You are now ready to stream the data.\n\n")
            lock_task_info()
            STREAMING_INITIALIZED = True
        else:
            unlock_task_info()
            task_info.insert('1.0', "Something went wrong when preparing the data. Make sure you have connected to the device.\n\n")
            lock_task_info()
            STREAMING_INITIALIZED = False
    
    button_streaming_init = tk.Button(streaming_init_frame,text="Initialize streaming", command=streaming_init_handler)
    button_streaming_init.grid(column=0, row=1, ipadx=5, pady=5, sticky=tk.W)

    # Status:
    status_frame = tk.Frame(root)
    status_frame.grid(row=5, padx=10, pady=10, sticky=tk.W)

    status_label = tk.Label(status_frame, text="Status:", font="Helvetica 12 bold")
    status_label.grid(row=0,sticky=tk.W)

    ## Connection status
    connection_status_label = tk.Label(status_frame, text="Connection:", font="Helvetica 10 bold")
    connection_status_label.grid(row=0,sticky=tk.W)
    
    ### Server
    connection_status_server = tk.Label(status_frame, text="Server:", font="Helvetica 10 bold")
    connection_status_server.grid(column=0, row=1, ipadx=5, pady=5, sticky=tk.W)

    ### Device
    connection_status_device = tk.Label(status_frame, text="Device: ", font="Helvetica 10 bold")
    connection_status_device.grid(column=0, row=2, ipadx=5, pady=5, sticky=tk.W)

    ### Streaming Initialized
    streaming_initialized_status = tk.Label(status_frame, text="Streaming initialized: ", font="Helvetica 10 bold")
    streaming_initialized_status.grid(column=0, row=3, ipadx=5, pady=5, sticky=tk.W)

    def update_status():
        # Server
        if(CONNECTION_SERVER):
            connection_status_server["bg"] = 'green'
            connection_status_server["text"] = "Server: CONNECTED"
        else:
            connection_status_server["bg"] = 'red'
            connection_status_server["text"] = "Server: NOT CONNECTED"
        
        # Device
        if(CONNECTION_DEVICE):
            connection_status_device["bg"] = 'green'
            connection_status_device["text"] = "Device: CONNECTED to " + str(DEVICE_ID)
        else:
            connection_status_device["bg"] = 'red'
            connection_status_device["text"] = "Device: NOT CONNECTED"

        if(STREAMING_INITIALIZED):
            streaming_initialized_status["bg"] = 'green'
            streaming_initialized_status["text"] = "Streaming initialized"
        else:
            streaming_initialized_status["bg"] = 'red'
            streaming_initialized_status["text"] = "Streaming NOT initialized"

        root.after(1000, update_status)

    root.after(1, update_status)


    # Start streaming
    streaming_start_frame = tk.Frame(root)
    streaming_start_frame.grid(row=6, padx=10, pady=10, sticky=tk.W)
   
    ## Header
    label_streaming_start_button = tk.Label(streaming_start_frame,text="Press the button below to start streaming" , font="Helvetica 12 bold")
    label_streaming_start_button.grid(row=0, columnspan=4)

    def streaming_start_handler():
        global STREAMING
        if(not CONNECTION_SERVER):
            unlock_task_info()
            task_info.insert('1.0',"You are not connected to the connection Server. Make sure you have setup the E4 connection server correctly and press the button 'Connect'\n\n")
            lock_task_info()

        elif(not CONNECTION_DEVICE):
            unlock_task_info()
            task_info.insert('1.0',"You are not connected to the connection Server. Make sure you have setup the E4 connection server correctly and press the button 'Connect'\n\n")
            lock_task_info()

        elif(not STREAMING_INITIALIZED):
            unlock_task_info()
            task_info.insert('1.0', "Streaming has not been initialized. Press the button 'Initialize streaming' and try again.\n\n")
            lock_task_info()
        else:
            STREAMING = True
            unlock_task_info()
            task_info.insert('1.0', "Streaming started\n\n")
            lock_task_info()

            root.after(100,stream(root))

    
    def streaming_stop_handler():
        global STREAMING
        STREAMING = False
        unlock_task_info()
        task_info.insert('1.0', "Streaming stopped\n\n")
        lock_task_info()
    
    
    button_streaming_start = tk.Button(streaming_start_frame,text="Start streaming", command=streaming_start_handler)
    button_streaming_start.grid(row=1,column=0, ipadx=5, pady=5, sticky=tk.N)

    button_streaming_stop = tk.Button(streaming_start_frame,text="Stop streaming", command=streaming_stop_handler)
    button_streaming_stop.grid(row=1,column=1, ipadx=5, pady=5, sticky=tk.N)

    # Task information:
    task_info_frame = tk.Frame(root)
    task_info_frame.grid(row=10)

    task_info = tk.Text(task_info_frame, state=DISABLED)
    task_info.grid(row=0)

    def unlock_task_info():
        task_info["state"] = NORMAL

    def lock_task_info():
        task_info["state"] = DISABLED


    root.mainloop()


def main2():
    connect()
    setup_subscribers()
    setup_files()
    stream()
main()

