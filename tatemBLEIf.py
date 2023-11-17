import asyncio
from operator import index

import os
import threading
from socket import timeout
import sys
import argparse
import json
#from this import d
from tkinter import BOTTOM
from traceback import print_tb
from tracemalloc import start
from xml.dom.minidom import Element
import matplotlib.pyplot as plt
import numpy as np
import cmd2
import time
from datetime import datetime
from plotly.subplots import make_subplots
from pickle import TRUE
# import rws7class
from alive_progress import alive_bar
import cmd2
from cmd2 import (
    Bg,
    Fg,
    style,
    with_argparser
)
import asyncio
import sys

from bleak import BleakScanner, discover, BleakClient
from bleak.backends.scanner import AdvertisementData
from bleak.backends.device import BLEDevice

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"


UART_SAFE_SIZE = 20

# def match_tatem_device(device: BLEDevice, adv: AdvertisementData):
#     # This assumes that the device includes the UART service UUID in the
#     # advertising data. This test may need to be adjusted depending on the
#     # actual advertising data supplied by the device.
#     print('device: ',device)
#     print('adv: ', adv)

#     #return True
#     if UART_SERVICE_UUID.lower() in adv.service_uuids:
#         #print('UART_SERVICE_UUID match')
#         return True
#     else:
#         return False

# async def find_available_tatems():
#     device = await BleakScanner.find_device_by_filter(match_tatem_device)
#     # print ('1: ', device)
#     # print('2: ', type(device))
#     # print('3: ', device.address)
#     # print('4: ', type(device.address))
#     return device


# async def get_services(address: str):
#     async with BleakClient(address) as client:
#         svcs = await client.get_services()
#         print("Services:")
#         for service in svcs:
#             print(service)

# def handle_disconnect(_: BleakClient):
#     print("Device was disconnected, goodbye.")

# def handle_rx(_: int, data: bytearray):
#     print("received over BLE:", data)


# async def run_remote_cmd(cmd: str, address: str):
#     print("Start of run_remote_cmd")
#     dataReceived=bytearray()
#     cmdReceivedEvent = asyncio.Event()

#     def handle_disconnect(_: BleakClient):
#         print("Device was disconnected, goodbye.")
#         #cancelling all tasks effectively ends the program
#         # for task in asyncio.all_tasks():
#         #    task.cancel()

#     def handle_rx(_: int, data: bytearray):

#         print("received:", data)
#         dataReceived.extend(data)
#         if dataReceived[-2:] == b'$0' or  dataReceived[-2:] == b'$1': # This is to signal that we are done collecting the data
#             #print('Reply received FAIL')
#             print("End of data set")
#             cmdReceivedEvent.set()
            


#     # Questions:
#     # 1. What does the disconnected_callback do? Should we modify it?
#     # 2. How does the collecting work? There seems to be some looping in the handle_rx-part, but how does it work? When do we actually call on the handle_rx and how do we know it will continue to loop?
#     # 3. Where do we actually send the data? Does the arduino TRANSMIT the data to tatemCom or does tatemCom COLLECT the data from the Arduino? Which one is the "active" part
#     # 4. Does "bleSerial.availableLines" mean lines that has been written on the Arduino from here (i.e. "getrepport") and if nothing is written on it, then this will not happen?
#     # 5. Is the "data" in this function the same as the "data" that we have just above? Could that cause some errors if they are not the same?

#     # Improvements:
#     # BleakClient takes a long time - approximately 10 s
#     tgetData = time.time()
#     print("Start of bleak client connection")
#     async with BleakClient(address, disconnected_callback=handle_disconnect) as client:
#         print("1")
#         await client.start_notify(UART_TX_CHAR_UUID, handle_rx) # Think this is notifying what to do when the data from the Arduino starts coming in
#         print("2")
#         #print(f'Connected to {address}')
#         data = bytes(cmd+'\r\n',"utf8")
#         print("3")
#         await client.write_gatt_char(UART_RX_CHAR_UUID, data) # Sending the "getreport"-message to the Arduino, which will make it send the report. Once it has sent everything, it will end with a "$0", which indicates that it is done
#         print("4")
#         await cmdReceivedEvent.wait() # think this is waiting until all the data has been collected. When it has been collected, the .set()-function is started and that will trigger the next part - the stop notifying part
#         print("5")
#         await client.stop_notify(UART_TX_CHAR_UUID)
#         print("6")
#     #print(dataReceived.decode())
#     print(f'Time getting data: {time.time() - tgetData}')
#     print("7")
#     datadecoded = dataReceived.decode()
#     print("8")
#     return datadecoded

# def writeFile(data, filedir):
#     e = datetime.now()
#     filename = e.strftime("%Y-%m-%d_%H-%M-%S")+'.json'
#     #filename = 'newestFile.json'
#     #filedir = 'C:\Temp\TATEMFILES\\' # TO_DO: Need to change this location to something more permanent
#     #filedir = 'C:\TFS\TATEM\datasets\\' # TO_DO: Need to change this location to something more permanent
#     foldername = e.strftime("%Y-%m-%d\\")
#     isDir = os.path.exists(filedir)
#     isFolder = os.path.exists(filedir+foldername)
#     if not isDir: os.makedirs(filedir)
#     #if not isFolder: os.makedirs(filedir+foldername)
    
#     with open(filedir+filename, 'a', encoding='utf-8') as f:
#         json.dump(data, f, indent=1, separators=(',', ': '))
#         f.close()


class TatemBLEIf():

    def __init__(self):
        self.devid = None
        self.connected= False
        self.client = None
        self.dataReceived=bytearray()
        self.cmdReceivedEvent = asyncio.Event()

        #threading.Thread.__init__(self)
    
    def SyncReport(self):
        pass


    def UseAddress(self, devid):
        self.devid = devid

    def handle_disconnect(self, _: BleakClient):
        print("Device was disconnected, goodbye.")
        #cancelling all tasks effectively ends the program
        # for task in asyncio.all_tasks():
        #    task.cancel()

    def handle_rx(self,_: int, data: bytearray):
        print("received:", data)
        self.dataReceived.extend(data)
        if self.dataReceived[-2:] == b'$0' or  self.dataReceived[-2:] == b'$1': # This is to signal that we are done collecting the data
            #print('Reply received FAIL')
            print("End of data set")
            self.cmdReceivedEvent.set()

    def ConnectBLE(self):
        if self.devid:
            self.client = BleakClient(self.devid, disconnected_callback=self.handle_disconnect) 
            asyncio.run( self.client.connect() )
            self.connected = True
        else:
           raise Exception("devid not assigend when trying to connect") 

    def DisConnectBLE(self):
        pass

    def IsConnected(self):
        return self.client.is_connected

    async def _RunCommand(self, cmd):

        if self.connected:
            print('Start notify')
            self.cmdReceivedEvent = asyncio.Event()

            await self.client.start_notify(UART_TX_CHAR_UUID, self.handle_rx) # Think this is notifying what to do when the data from the Arduino starts coming in
            data = bytes(cmd+'\r\n',"utf8")
            print('Send cmd')
            await self.client.write_gatt_char(UART_RX_CHAR_UUID, data) # Sending the "getreport"-message to the Arduino, which will make it send the report. Once it has sent everything, it will end with a "$0", which indicates that it is done
            print('Wait for completion')
            await self.cmdReceivedEvent.wait() # think this is waiting until all the data has been collected. When it has been collected, the .set()-function is started and that will trigger the next part - the stop notifying part
            print('Stop notify')
            await self.client.stop_notify(UART_TX_CHAR_UUID)
        else:
           raise Exception("Need to be connected before running commands") 
            
    def RunCommand(self, cmd):
        self.dataReceived=bytearray()
        report = asyncio.run( self._RunCommand(cmd) )

    def CmdReply(self):
        return self.dataReceived.decode() 



def main():
    bleIf = TatemBLEIf()
    #bleIf.SyncReport()

    # print("**")
    # bleIf.start()
    # print("**")
    # time.sleep(5)
    # print("**")
    bleIf.UseAddress('78:E9:64:B0:78:AA')
    print('Connect')
    bleIf.ConnectBLE()
    print('Connected')
    while not bleIf.IsConnected():
        print('Not Connected')
        time.sleep(1)

    #time.sleep(10)
     
    # print('Get info3')
    # thread = threading.Thread(target=bleIf.RunCommand('info') )
    # thread.start()
    # print('Result: {}'.format( bleIf.CmdReply()) )


    # print('Get info2')


    for i in range(100):
        thread = threading.Thread(target=bleIf.RunCommand('info') )
        thread.start()

        print('Result: {}'.format( bleIf.CmdReply()) )

    # print('Result form info: {}'.format(result))
    #time.sleep(10)
    print('Done')


    print(bleIf.CmdReply())



if __name__ == "__main__":
    sys.exit( main()  )



