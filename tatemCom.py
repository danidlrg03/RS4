import asyncio
from operator import index

import os
from socket import timeout
import sys
import argparse
import json
from tkinter import BOTTOM
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

import TatemRapidIf
import TatemArduinoIf
import tatemTest

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"


UART_SAFE_SIZE = 20


def PlotTrigDataHist( plotFile ):
    data=[]
    with open( plotFile, 'r') as f:
        lines= f.readlines()

    errorTrigs=0
    startTime = json.loads(lines[0])['time']
    endTime = json.loads(lines[-1])['time']
    for line in lines:
        v=json.loads(line)
        #print(v)
        if v['valid']:
            data.append( float(v['trigtime']))
        else:
            errorTrigs+=1

    data=np.array(data)

    data= (data - np.mean(data))*1000

    fig, (ax1,ax2) = plt.subplots(2,1)

    ax1.boxplot(data)
    ax1.set( ylabel='Jitter in ms', title='File:{} \nStart: {} End: {}\nTrigg-jitter of {} samples, {} error-triggs'.format(plotFile,startTime, endTime,len(data), errorTrigs) )
    ax1.grid()


    q25, q75 = np.percentile(data, [25, 75])
    bin_width = 2 * (q75 - q25) * len(data) ** (-1/3)
    bins = round((data.max() - data.min()) / bin_width)

    ax2.hist(data, bins=bins)
    ax2.set( ylabel='Number of triggs')
    ax2.set( xlabel='Trigg-error in ms')
    ax2.grid()


    fig.savefig( plotFile+'.png')
    plt.show()

# Lists available BLE devices
def choices_provider(self):
    filesInDir=os.listdir()
    jsonFiles=[]
    for item in filesInDir:
        if item.endswith('.json'):
            jsonFiles.append(item)
    return jsonFiles

# Lists available TATEM devices
def tatem_provider(self):
    devs = asyncio.run( discover() )
    devAddrList = []
    for dev in devs:
        devAddrList.append(dev.address)
    return devAddrList
    #return['1C:F3:A4:84:91:47', '24:4C:64:C5:D5:9D']

# Help for connecting to robot with 
def robot_provider(self):
    return['192.168.125.1']

def match_tatem_device(device: BLEDevice, adv: AdvertisementData):
    # This assumes that the device includes the UART service UUID in the
    # advertising data. This test may need to be adjusted depending on the
    # actual advertising data supplied by the device.
    print('device: ',device)
    print('adv: ', adv)

    if UART_SERVICE_UUID.lower() in adv.service_uuids:
        #print('UART_SERVICE_UUID match')
        return True
    else:
        return False

async def find_available_tatems():
    device = await BleakScanner.find_device_by_filter(match_tatem_device)
    return device


async def get_services(address: str):
    async with BleakClient(address) as client:
        svcs = await client.get_services()
        print("Services:")
        for service in svcs:
            print(service)


class TatemCLI(cmd2.Cmd):
    """cmd2 application."""


    def __init__(self, devid):
        super().__init__()
        self.arduinoIP = None
        self.robotIP = None
        self.Arduino = None
        self.Robot = None
        #self.TestCycle = None
        self.prompt = 'tatem>'
         #Remove the quit command. We will use our own exit command
        del cmd2.Cmd.do_quit
        #self.intro = cmd2.style('Welcome to the trigger application', fg=cmd2.fg.red, bg=cmd2.bg.white, bold=True)
        self.intro = style('Welcome to the TATEM application!', fg=Fg.RED, bg=Bg.WHITE, bold=True)


    def PrintDebug(self, msg):
        if self.debug:
            self.poutput(msg)

    # Finding all available BLE-units
    def do_discover(self, args):
        """list available by use of discover"""
        self.poutput('list available by use of discover' )
        devs = asyncio.run( discover() )
        for dev in devs:
            #print('* ',dev)
            print('*', dev.address, dev.name)
            #print(type(dev))
            #asyncio.run( service_explorer(dev.address) )

    # Finding available TATEMS
    def do_who(self, args):
        """list available TATEM's"""
        self.poutput('Searching for TATEMS' )
        dev = asyncio.run( find_available_tatems() )
        print('* ',dev)

    # Start up connection to robot by creating an rws-object.
    tatem_parser = cmd2.Cmd2ArgumentParser()
    tatem_parser.add_argument('address', type=str, nargs='?', choices_provider=robot_provider, help='the robot address' )
    @with_argparser(tatem_parser)
    def do_connectRobot(self, args):
        """Connecting the Robot"""
        IP = args.address
        if IP == None:
            print("Choose robot address.")
            self.Robot = None
            self.robotIP = None
        else:
            self.robotIP = IP
            self.Robot = TatemRapidIf.TatemRapidIf(self.robotIP)
            self.Robot.Connect() # Creating the rws-object. Not sure if this will work though - will need to test this out
            if self.Robot.CheckConnection():
                print(f"Connected to Robot with IP: {self.robotIP}")
            else:
                print(f"Could not connect to Robot with IP: {self.robotIP}.")
                self.Robot = None
                self.robotIP = None

    # Start up connection with the Arduino by creating a BLE-object.
    tatem_parser = cmd2.Cmd2ArgumentParser()
    tatem_parser.add_argument('address', type=str, nargs='?', choices_provider=tatem_provider, help='the tatem address' )
    @with_argparser(tatem_parser)
    def do_connectArduino(self, args):
        """Connecting the Arduino"""
        IP = args.address
        if IP == None:
            print("Choose IP address.")
        else:
            self.arduinoIP = IP
            self.Arduino = TatemArduinoIf.TatemArduinoIf(self.arduinoIP) # Will start the bluetooth connection
            maxtime = 0
            while not self.Arduino.IsConnected() and maxtime < 40: # Not sure this will work - think I need to have some other save in case it doesn't
                print(f"Connecting to the Arduino with IP: {self.arduinoIP}...")
                time.sleep(1)
                maxtime = maxtime + 1
            if maxtime == 40:
                self.Arduino.Disconnect()
                print("Timeout error: The arduino is not connected.")
                self.Arduino = None
                self.arduinoIP = None
            else:
                print(f"Connected to Arduino with IP: {self.arduinoIP}")

    # Checking if the robot is connected
    def do_checkRobotConnection(self, args):
        if self.Robot == None:
            print("No robot is connected")
        elif self.Robot.CheckConnection():
            print(f"Connected to robot with IP: {self.robotIP}")
        else:
            print(f"A robot object with IP {self.robotIP} has been created, but is not connected")

    # Checking if the Arduino is connected
    def do_checkArduinoConnection(self, args):
        if self.Arduino == None:
            print("No Arduino is connected")
        elif self.Arduino.IsConnected():
            print(f"Connected to Arduino with IP: {self.arduinoIP}")
        else:
            print(f"An Arduino object with IP {self.arduinoIP} has been created, but is not connected")

    # Disconnect the robot
    def do_disconnectRobot(self, args):
        if self.Robot != None:
            self.Robot.Disconnect()
        self.Robot = None
        self.robotIP = None

    # Disconnect the Arduino
    def do_disconnectArduino(self, args):
        if self.Arduino != None:
            print("Disconnecting Arduino...")
            self.Arduino.Disconnect()
            while self.Arduino.IsConnected():
                print("Disconnecting Arduino...")
                time.sleep(1)
            print("Arduino is disconnected")
        self.Arduino = None
        self.arduinoIP = None

    # Retrieving the t-values from the rapid code. By using the "setTvalues"-function, these can then be set on the Arduino.
    def do_getTvalues(self, args):
        if self.Robot == None:
            print("No robot is connected")
        else:
            tA_s = self.Robot.GettA()
            tO_s = self.Robot.GettO()
            tR_s = self.Robot.GettR()
            print("Current t-values are:" + "\ntA = " + str(tA_s) + "\ntO = " + str(tO_s) + "\ntR = " + str(tR_s))

    # Setting the t-values on the Arduino to the same values as in the rapid-code.
    def do_setTvalues(self, args):
        if self.Robot == None:
            print("No robot is connected")
        elif self.Arduino == None:
            print("No arduino is connected")
        else:
            if self.Robot.RobotState() == "stopped":
                tA_s = float(self.Robot.GettA())
                tO_s = float(self.Robot.GettO())
                tR_s = float(self.Robot.GettR())
                tA_us = str(tA_s*1000000)
                tO_us = str(tO_s*1000000)
                tR_us = str(tR_s*1000000)
                self.Arduino.SetTa(tA_us)
                self.Arduino.SetTo(tO_us)
                self.Arduino.SetTr(tR_us)
                print("Current t-values are:" + "\ntA = " + str(tA_s) + "\ntO = " + str(tO_s) + "\ntR = " + str(tR_s))
            else:
                print("Test is in progress.")

    # Running the TATEM-test
    def do_runTest(self, args):
        if self.Robot == None:
            print("No robot is connected")
        elif self.Arduino == None:
            print("No arduino is connected")
        else:
            self.TestCycle = tatemTest.runTatemTest(self.Arduino, self.Robot) # This will start the test through the "run"-function in tatemTest

    # Stopping the TATEM-test
    def do_endTest(self, args):
        self.TestCycle.stopTest()
        self.TestCycle = None # Not sure this is how to do this

    # Collecting the data from the Arduino
    def do_getReport(self, args):
        if self.Arduino == None:
            print("No Arduino is connected")
        else:
            reportCollected = self.Arduino.GetReport()
            print(reportCollected)

    # Resetting the Arduino.
    def do_resetArduino(self, args):
        if self.Arduino == None:
            print("No Arduino is connected")
        else:
            self.Arduino.Reset()


    # Retrieving info (not finished)
    def do_info(self, args):
        """help on info"""
        self.poutput('Info:')

    # Plotting the collected data
    name_parser = cmd2.Cmd2ArgumentParser()
    name_parser.add_argument('logfile', type=str, nargs='?', choices_provider=choices_provider, help='the logfile to use' )
    @with_argparser(name_parser)
    def do_plot(self, args):
        """Plot a logfile"""
        self.poutput('Plot {}'.format(args.logfile))
        PlotTrigDataHist( args.logfile )

    # Loading log-files
    name_parser = cmd2.Cmd2ArgumentParser()
    name_parser.add_argument('logfile', type=str, nargs='?', choices_provider=choices_provider, help='the logfile to use' )
    @with_argparser(name_parser)
    def do_load(self, args):
        """load a logfile"""
        self.poutput('Plot {}'.format(args.logfile))
        with open( args.logfile, 'r') as f:
            data = json.load( f )
        self.poutput(f'Information about {args.logfile}:')
        self.poutput('{} events'.format( len(args.logfile)))
        for idx, evt  in enumerate(data):
            self.poutput('event {} start: {} end: {} doOff: {} tA: {} tO: {} tR: {}, eventResult: {}'.format(idx, evt['eventStart'], evt['eventEnd'],  evt['doOff'], evt['tA'], evt['tO'], evt['tR'], evt['eventResult']))

    # Exit the application
    def do_exit(self, args):
        """help on exit"""
        if self.Arduino != None:
            print("Disconnecting Arduino...")
            self.Arduino.Disconnect()
            while self.Arduino.IsConnected():
                print("Disconnecting Arduino...")
                time.sleep(1)
            print("Arduino is disconnected")
        self.Arduino = None
        self.arduinoIP = None
        self.Robot = None
        self.robotIP = None
        self.poutput('exit')
        return True

def main():
    arg_parser = argparse.ArgumentParser(description='Process commandline arguments...') # selection of robot
    arg_parser.add_argument('--devid', type=str,default='192.168.126.150' )

    startupargs = arg_parser.parse_args()


    c = TatemCLI( startupargs.devid )
    sys.exit( c.cmdloop() )


if __name__ == "__main__":
    sys.exit( main()  )





async def async_main():
    print('Hello ...')
    await asyncio.sleep(1)
    print('... World!')


def main():
    print('before')
    asyncio.run(async_main())
    print('after')

if __name__ == "__main__":
    main()

#asyncio.run(main())

    # tatem_parser = cmd2.Cmd2ArgumentParser()
    # tatem_parser.add_argument('address', type=str, nargs='?', choices_provider=tatem_provider, help='the tatem address' )
    # @with_argparser(tatem_parser)
    # def do_report(self, args):
    #     """get report from TATEM"""
    #     self.poutput(f'get report from TATEM on address {args.address}' )
    #     tstart = time.time()
    #     report = asyncio.run( run_remote_cmd( 'getreport', args.address ) )
    #     print(f'Time getting the report: {time.time() - tstart}')
    #     if report[-2:]=='$0':
    #         #self.poutput('Report received:')
    #         repDict = json.loads(report[:-2])
    #     else:
    #         print(report)
    #         self.poutput('Not able to convert report from json to dict:', report)
    #         repDict = None
    #     #print( repDict )
    #     #print( report )
    #     filedir = 'C:\TFS\TATEM\datasets\\'
    #     writeFile(repDict, filedir)
    #     return repDict


    # def writeFile(data, filedir):
    #     e = datetime.now()
    #     filename = e.strftime("%Y-%m-%d_%H-%M-%S")+'.json'
    #     foldername = e.strftime("%Y-%m-%d\\")
    #     isDir = os.path.exists(filedir)
    #     isFolder = os.path.exists(filedir+foldername)
    #     if not isDir: os.makedirs(filedir)

    #     with open(filedir+filename, 'a', encoding='utf-8') as f:
    #         json.dump(data, f, indent=1, separators=(',', ': '))
    #         f.close()


    # # Run cmd
    # cmdtatem_parser = cmd2.Cmd2ArgumentParser()
    # cmdtatem_parser.add_argument('command', type=str, help='the command to execute' )
    # cmdtatem_parser.add_argument('address', type=str, nargs='?', choices_provider=tatem_provider, help='the tatem address' )
    # @with_argparser(cmdtatem_parser)
    # def do_cmd(self, args):
    #     """run command on TATEM"""
    #     self.poutput(f'run \'{args.command}\' on TATEM on address {args.address}' )
    #     report = asyncio.run( run_remote_cmd( args.command, args.address ) )

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