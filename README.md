# Empatica_e4_data_stream
This is a streaming tool for connecting and saving data streamed from the Empatica E4 streaming server. To use this script, you have to have the E4 streaming server installed on your computer. More info can be found here: https://developer.empatica.com/windows-streaming-server.html.

## Using the script
To start the program run the executable file `dist/stream.exe`.

This will open a text base interface giving you instructions on how to connect and start streaming from the E4 streaming server.

All recorded data will be saved under `./data/{unique_ID}` in the same folder as the executable. You will be asked to provide the unique ID in the beginning of the script. Make sure the ID is truly unique. Otherwise, all files previously created under the same ID will be deleted.