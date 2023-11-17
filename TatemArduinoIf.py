from datetime import datetime
from http import client
from pickle import TRUE
import threading
import asyncio
import sys
import time
import json
import os

from bleak import BleakScanner, discover, BleakClient, BleakError
from bleak.backends.scanner import AdvertisementData
from bleak.backends.device import BLEDevice

# All necessary bluetooth communication with the Arduino is handled from here. 
class TatemArduinoIf(threading.Thread):
    # Creating the BLE-object representing the Arduino
    def __init__(self, ip):
        self.ip = ip
        self.tA = "10"
        self.tO = "10"
        self.tR = "10"
        self.client = None
        self.keepConnection = True
        self.UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
        self.UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
        self.UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
        
        threading.Thread.__init__(self)
        self.start()

    # Setting up the BLE-connection with the Arduino. Will be up and running until it is prompted to disconnect using the "Disconnect"-function.
    async def ConnectingBLE(self, ble_address: str):
        device = await BleakScanner.find_device_by_address(ble_address, timeout=20.0)
        if not device:
            raise BleakError(f"A device with address {ble_address} could not be found.")
        async with BleakClient(device) as self.client:
            print("Connection successful")
            while self.keepConnection:
                await asyncio.sleep(1)
            # Do we need to add something here to make sure the connection is broken
    
    # Starts up a BLE-connection with the Arduino. This function overrides the "run"-function in the thread class. 
    def run(self):
        asyncio.run(self.ConnectingBLE(self.ip))

    # Disconnecting the BLE-connection with the Arduino
    def Disconnect(self):
        self.keepConnection = False
    
    # Checking if the BLE-connection with the Arduino is present
    def IsConnected(self):
        if self.client != None:
            status = self.client.is_connected
        else:
            status = False
        return status
    
    # Handling the BLE-communication with the Arduino
    async def run_remote_cmd(self, cmd: str):
        print("Start of run_remote_cmd")
        dataReceived=bytearray()
        cmdReceivedEvent = asyncio.Event()

        def handle_rx(_: int, data: bytearray):
            print("received:", data)
            dataReceived.extend(data)
            # Maybe have a time-out here - if it takes more than maybe 20 s, then we are timing out
            if dataReceived[-2:] == b'$0' or  dataReceived[-2:] == b'$1': # This is to signal that we are done collecting the data
                print("End of data set")
                cmdReceivedEvent.set()

        tgetData = time.time()
        print("1")
        await self.client.start_notify(self.UART_TX_CHAR_UUID, handle_rx) # Think this is notifying what to do when the data from the Arduino starts coming in
        print("2")
        data = bytes(cmd+'\r\n',"utf8")
        print("3")
        await self.client.write_gatt_char(self.UART_RX_CHAR_UUID, data) # Sending the "getreport"-message to the Arduino, which will make it send the report. Once it has sent everything, it will end with a "$0", which indicates that it is done
        print("4")
        await cmdReceivedEvent.wait() # think this is waiting until all the data has been collected. When it has been collected, the .set()-function is started and that will trigger the next part - the stop notifying part
        print("5")
        await self.client.stop_notify(self.UART_TX_CHAR_UUID)
        print("6")
        print(f'Time getting data: {time.time() - tgetData}')
        print("7")
        datadecoded = dataReceived.decode()
        print("8")
        return datadecoded

    # Converting the collected Arduino data to a json-file
    def writeFile(self, data, filedir):
        e = datetime.now()
        filename = e.strftime("%Y-%m-%d_%H-%M-%S")+'.json'
        isDir = os.path.exists(filedir)
        if not isDir: os.makedirs(filedir)
        with open(filedir+filename, 'a', encoding='utf-8') as f:
            json.dump(data, f, indent=1, separators=(',', ': '))
            f.close()

    # Collecting the data from the connected Arduino
    def GetReport(self):
        collectedReport = False
        if self.IsConnected():
            print(f'get report from TATEM')
            report = asyncio.run( self.run_remote_cmd( 'getreport' ) ) # Sending the "getreport"-command to the Arduino, which will instruct it to start sending the stored data
            if report[-2:]=='$0':
                repDict = json.loads(report[:-2])
                filedir = 'C:/TFS/TATEM/datasets/'
                self.writeFile(repDict, filedir)
                collectedReport = True
            else:
                print( 'Not able to convert report from json to dict:', report )
                repDict = None
        else:
            print("There is no Arduino connected")
        print("done with getting report function!")
        return collectedReport

    # Resetting the connected Arduino
    def Reset(self):
        message = "reset"
        if self.IsConnected():
            print('resetting the Arduino...')
            resetDone = asyncio.run( self.run_remote_cmd( message ) )
            if resetDone[-2:]=='$0':
                print("reset has been successful")
            else:
                print( 'Something went wrong' )
        else:
            print("There is no Arduino connected")

    # Setting the tA value on the Arduino to the tA-value in the rapid code
    def SetTa(self, tA_new: str):
        message = "SetTa " + tA_new
        if self.IsConnected():
            print(f'setting Ta-value on Arduino...')
            tA = asyncio.run( self.run_remote_cmd( message ) )
            if tA[-2:]=='$0':
                self.tA =tA[:-2]
                print(f"tA value has been set to: {self.tA}")
            else:
                print( 'Something went wrong' )
        else:
            print("There is no Arduino connected")
    
    # Setting the tO value on the Arduino to the tO-value in the rapid code
    def SetTo(self, tO_new: str):
        message = "SetTo " + tO_new
        if self.IsConnected():
            print(f'setting To-value on Arduino...')
            tO = asyncio.run( self.run_remote_cmd( message ) )
            if tO[-2:]=='$0':
                self.tO = tO[:-2]
                print(f"tO value has been set to: {self.tO}")
            else:
                print( 'Something went wrong' )
        else:
            print("There is no Arduino connected")
    
    # Setting the tO value on the Arduino to the tR-value in the rapid code
    def SetTr(self, tR_new: str):
        message = "SetTr " + tR_new
        if self.IsConnected():
            print(f'setting Tr-value on Arduino...')
            tR = asyncio.run( self.run_remote_cmd( message ) )
            if tR[-2:]=='$0':
                self.tR = tR[:-2]
                print(f"tR value has been set to: {self.tR}")
            else:
                print( 'Something went wrong' )
        else:
            print("There is no Arduino connected")

def main():
    tatemArduinoIf = TatemArduinoIf('10.47.89.50')

if __name__ == "__main__":
    main()
    
        # Does not work
    # # Not sure these need to be async-functions (since we are starting these in a new thread anyways)
    # async def ConnectingBLE(self, ble_address: str):
    #     self.client = BleakClient(ble_address)
    #     try:
    #         await self.client.connect()
    #         print("Arduino has been connected")
    #         print(self.client.is_connected)
    #         print("it doesn't reach here")
    #     except Exception as e:
    #         print(e)
    #         print("Not able to connect")
    #         self.client = None
    #     # finally:
    #     #     await self.client.disconnect()
    
    # # Does not work
    # async def DisconnectingBLE(self):
    #     if self.client != None:
    #         print("There is definately a connection")
    #         print(self.client.is_connected)
    #     await self.client.disconnect()
    #     self.client = None
    #     print(self.client)