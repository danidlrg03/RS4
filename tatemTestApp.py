from asyncio.windows_events import NULL
#from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import *
from tkinter import filedialog, messagebox, ttk, simpledialog
import os
import tatemCom
# import rws7class
# import rws7class_vir
from rwsuis import RWS
import threading
import time
import timeit


# TO_DO:
# Errors to fix:
# 1. Get_report: does not always work and can block the entire program. Need to end in task manager when that happens. Possible solution: set up bluetooth connection once - not all the time.

# Possible functions to add:
# 1. "Reset"-function: will need to do modifications to the rapid code if I do that
# 2. Two "test connection"-functions: to see that there is a connection between 1) the Arduino and the computer and 2) between the robot and the computer

# Changed ipArduino and ipRobot to UiS ips

class TestApp:
    def __init__(self, root):
        self.ipArduino = "A1:F8:14:CE:BA:AC"
        self.ipRobot = '152.94.0.39'
        #self.filepath = 'C:\TFS\TATEM\datasets\\' # Default value for the file path
        self.filepath = 'C:/TFS/TATEM/datasets/' # Default value for the file path
        #self.mu = rws7class_vir.rws7('127.0.0.1')
        self.mu = RWS.RWS('152.94.0.39')
        self.threadTatem = NULL
        self.threadCheck = NULL
        self.threadStarted = False
        self.testStopped = True
        self.testRunning = False
        self.fileDirectoryLabel = NULL
        self.testStatusLabel = ""
        self.root = root
        self.eventText = ""
        self.ipArduinoLabel = NULL
        self.ipRobotLabel = NULL
        
    def get_report(self):
        print(f'get report from TATEM on address {self.ipArduino}')
        #report = tatemCom.asyncio.run( tatemCom.run_remote_cmd( 'getreport', self.ipArduino ) )
        report = tatemCom.asyncio.new_event_loop().run_until_complete( tatemCom.run_remote_cmd( 'getreport', self.ipArduino ) )
        
        if report[-2:]=='$0':
            #self.poutput('Report received:')
            repDict = tatemCom.json.loads(report[:-2])
            tatemCom.writeFile(repDict, self.filepath) # ADDED - used to be outside the if-statement
        else:
            print( 'Not able to convert report from json to dict:', report )
            repDict = None
        #print( report )
        #tatemCom.writeFile(repDict, self.filepath)
        return repDict

    def tatemTest(self):
        failedReports = 0
        cyclesRun = 0
        while self.testRunning:
            self.eventText.delete("1.0", "end")
            self.testStopped = False
            self.eventText.insert(tk.END, str(self.mu.getexecstat()) + "...\n")
            self.eventText.insert(tk.END, "Total number of cycles run: " + str(cyclesRun) + "\n")
            self.eventText.insert(tk.END, "Total number of failed data collections: " + str(failedReports) + "\n")
            if self.mu.getexecstat() == "stopped" or self.testRunning == False:
                # Change this when have time - there are different scenarios for these stops (if it is stopped it could mean that it is not possible to start the robot from the GUI)
                self.eventText.insert(tk.END, "The test has been stopped. \nYou might need to restart the robot manually on \nthe teach pendant before running the program\n") 
                break
            if self.mu.getsymval('T_ROB1','TrigTest','finished') == "TRUE":
                self.mu.stop()
                self.eventText.insert(tk.END, "Robot is stopped for data collection \nand resetting the Arduino.\n")
                self.eventText.insert(tk.END, "Collecting data...\n")
                try:
                    report = self.get_report()
                except:
                    failedReports = failedReports + 1
                    self.eventText.insert(tk.END, "Something went wrong when collecting the data\n")
                else:
                    if report == None:
                        self.eventText.insert(tk.END, "No data has been collected\n")
                    else:
                        self.eventText.insert(tk.END, "Data collected successfully\n")
                if self.testRunning == False:
                    self.eventText.insert(tk.END, "Test was stopped during data collection. Reset the Arduino manually before restarting the program.\n")
                    break
                self.mu.reqmast()
                self.mu.setsymval('T_ROB1','TrigTest','report',"TRUE") # Sending information to Rapid that the report has been collected successfully
                time.sleep(0.5)
                if (self.mu.getsymval('T_ROB1','TrigTest','report')) != "TRUE" or self.testRunning == False:
                    self.eventText.insert(tk.END, "ERROR: The report-variable was not \nproperly changed in the rapid code.\n")
                    self.mu.relmast()
                    break
                self.mu.setsymval('T_ROB1','TrigTest','resetArduino',"TRUE") # Triggering the resetting of values in the arduino (Will trigger I/O on/off in Rapid two times)
                time.sleep(0.5)
                if (self.mu.getsymval('T_ROB1','TrigTest','resetArduino')) != "TRUE" or self.testRunning == False:
                    self.eventText.insert(tk.END, "ERROR: The resetArduino-variable was not \nproperly changed in the rapid code.\n")
                    self.mu.relmast()
                    break
                self.mu.relmast()
                if self.testRunning == False:
                    break
                self.mu.start() # By starting the Rapid program again, the resetting of values will be triggered
                self.eventText.insert(tk.END, "Resetting the Arduino...\n")
                counter = 0
                while counter < 10:
                    if self.testRunning == False or self.mu.getexecstat() == "stopped" or self.mu.getsymval('T_ROB1','TrigTest','resetSuccess') == "TRUE":
                        break
                    counter = counter + 1
                    time.sleep(1)
                if self.mu.getexecstat() == "stopped":
                    self.eventText.insert(tk.END, "The robot was stopped during reset.\nReset the Arduino manually before restarting the program.\n")
                    break
                if self.mu.getsymval('T_ROB1','TrigTest','resetSuccess') == "FALSE" or self.testRunning == False:
                    self.mu.stop()
                    self.eventText.insert(tk.END, "ERROR: The reset was NOT successful. \nReset the Arduino manually before restarting the program.\n")
                    break
                elif (self.mu.getexecstat() == "stopped"):
                    self.eventText.insert(tk.END, "The robot has been stopped. The test will not continue.\n")
                    break
                else:
                    self.eventText.insert(tk.END, "The Arduino has been reset.\n")
                    self.eventText.insert(tk.END, "The robot is ready to go into another cycle.\n")
                cyclesRun = cyclesRun + 1
            time.sleep(1)
        self.testRunning = False
        self.testStopped = True
        self.eventText.insert(tk.END, "TEST STOPPED\n")
    
    def tatemTest_vir(self):
        failedReports = 0
        cyclesRun = 0
        while self.testRunning:
            self.eventText.delete("1.0", "end")
            self.testStopped = False
            self.eventText.insert(tk.END, str(self.mu.getexecstat()) + "...\n")
            self.eventText.insert(tk.END, "Total number of cycles run: " + str(cyclesRun) + "\n")
            self.eventText.insert(tk.END, "Total number of failed data collections: " + str(failedReports) + "\n")
            if self.mu.getexecstat() == "stopped" or self.testRunning == False:
                self.eventText.insert(tk.END, "You need to restart the robot manually on \nthe teach pendant before running the program\n")
                break
            if self.mu.getsymval('T_ROB1','Module1','finished') == "TRUE":
                self.mu.stop()
                self.eventText.insert(tk.END, "Robot is stopped for data collection \nand resetting the Arduino.\n")
                self.eventText.insert(tk.END, "Collecting data...\n")
                time.sleep(10) # Simulating getting the report
                report = 2
                if report == None or self.testRunning == False:
                    self.eventText.insert(tk.END, "Something went wrong when collecting the report\n")
                else:
                    self.eventText.insert(tk.END, "Data collected successfully\n")
                if self.testRunning == False:
                    self.eventText.insert(tk.END, "Test was stopped during data collection\n")
                    break
                self.mu.reqmast()
                self.mu.setsymval('T_ROB1','Module1','report',"TRUE") # Sending information to Rapid that the report has been collected successfully
                time.sleep(0.5)
                if (self.mu.getsymval('T_ROB1','Module1','report')) != "TRUE" or self.testRunning == False:
                    self.eventText.insert(tk.END, "ERROR: The report-variable was not \nproperly changed in the rapid code.\n")
                    self.mu.relmast()
                    break
                self.mu.setsymval('T_ROB1','Module1','resetArduino',"TRUE") # Triggering the resetting of values in the arduino (Will trigger I/O on/off in Rapid two times)
                time.sleep(0.5)
                if (self.mu.getsymval('T_ROB1','Module1','resetArduino')) != "TRUE" or self.testRunning == False:
                    self.eventText.insert(tk.END, "ERROR: The resetArduino-variable was not \nproperly changed in the rapid code.\n")
                    self.mu.relmast()
                    break
                self.mu.relmast()
                if self.testRunning == False:
                    break
                self.mu.start() # By starting the Rapid program again, the resetting of values will be triggered
                self.eventText.insert(tk.END, "Resetting the Arduino...\n")
                counter = 0
                while counter < 10:
                    if self.testRunning == False or self.mu.getexecstat() == "stopped" or self.mu.getsymval('T_ROB1','Module1','resetSuccess') == "TRUE":
                        break
                    counter = counter + 1
                    time.sleep(1)
                if self.mu.getexecstat() == "stopped":
                    self.eventText.insert(tk.END, "The robot was stopped during reset.\nReset the Arduino manually before restarting the program.\n")
                    break
                if self.mu.getsymval('T_ROB1','Module1','resetSuccess') == "FALSE" or self.testRunning == False:
                    self.mu.stop()
                    self.eventText.insert(tk.END, "ERROR: The reset was NOT successful. \nReset the Arduino manually before restarting the program.\n")
                    break
                elif (self.mu.getexecstat() == "stopped"):
                    self.eventText.insert(tk.END, "The robot has been stopped. The test will not continue.\n")
                    break
                else:
                    self.eventText.insert(tk.END, "The Arduino has been reset.\n")
                    self.eventText.insert(tk.END, "The robot is ready to go into another cycle.\n")
                cyclesRun = cyclesRun + 1
            time.sleep(1)
        self.testRunning = False
        self.testStopped = True
        self.eventText.insert(tk.END, "TEST STOPPED\n")

    def getFolderLocation(self):
        if self.testRunning == True: 
            self.popupmsg('The program is still running.')
        elif self.testStopped == False: 
            self.popupmsg("The program is being stopped. This can take a while.")
        else:
            filedir = filedialog.askdirectory()
            self.filepath = filedir + "/"
            self.fileDirectoryLabel.config(text = self.filepath)
    # TO_DO: add that if no location is chosen, the default will be set

    # TO_DO: implement a function for testing the IP connection to the robot
    def testRobotIPconnection(self):
        print("Not implemented yet.")

    # TO_DO: implement a function for testing the IP connection to the Arduino
    def testArduinoIPconnection(self):
        print("Not implemented yet.")

    def setpp2main(self):
        if self.testRunning == True: 
            self.popupmsg('The program is still running.')
        elif self.testStopped == False: 
            self.popupmsg("The program is being stopped. This can take a while.")
        elif self.mu.getexecstat() == "running": 
            self.popupmsg("PP to main cannot be set while robot is running.")
        else:
            self.mu.pp2main()
            time.sleep(1)

    # TO_DO: implement this function
    def resetArduino(self):
        if self.testRunning == True: 
            self.popupmsg('The program is still running.')
        elif self.testStopped == False: 
            self.popupmsg("The program is being stopped. This can take a while.")
        else:
            self.popupmsg("This function has not yet been implemented.")
            # Add reset function
    
    def checkingStatus(self):
        while self.testStopped == False:
            time.sleep(0.5)
        self.testStatusLabel.config(text = 'The test is stopped. Press "Start Test" to start a new test', fg = "black", font = ("Arial",10, "bold"), )
    
    def startTest(self):
        if self.testStopped == False:
            self.popupmsg("The program is already running.")
        else:
            self.mu.pp2main() # Might remove? Or add a popup window allowing to set pp2main?
            time.sleep(1) # Might want to move these three lines to below, but not sure how
            self.mu.start()
            if self.mu.getexecstat() == "stopped":
                self.popupmsg('The robot cannot be started from here. Please start the robot manually on the teach pendant first.')
            else:
                if self.threadStarted == True:
                    self.threadTatem.join()
                    self.threadCheck.join()
                self.testRunning = True
                self.testStopped = False
                self.threadTatem = threading.Thread(target=self.tatemTest)
                #self.threadTatem = threading.Thread(target=self.tatemTest_vir)
                self.threadCheck = threading.Thread(target=self.checkingStatus)
                self.threadTatem.start()
                self.threadCheck.start()
                self.threadStarted = True
                self.testStatusLabel.config(text = "TEST STATUS:        RUNNING...", font = ("Arial",11, "bold"), fg = "#3D9140")
    
    def  stopTest(self):
        self.mu.stop()
        self.testRunning = False
        if self.testStopped == False:
            self.testStatusLabel.config(text = "Stopping the test. This can take a while.", font = ("Arial",11, "bold"), fg="#EE4000")
        
    def onClosing(self):
        if self.testRunning == True:
            self.popupmsg('The program is still running. Press "Stop Program" before exiting the window.')
        elif self.testStopped == False:
            self.popupmsg("The program is being stopped. This can take a while. The window cannot shut down until the program has been stopped.")
        else:
            if self.threadTatem != NULL and self.threadStarted == True:
                self.threadTatem.join()
                self.threadCheck.join()
            self.root.destroy()
    
    def popupmsg(self, msg):
        popup = tk.Tk()
        popup.wm_title("!")
        label = ttk.Label(popup, text=msg)
        label.pack(side="top", fill="x", pady=10)
        B1 = ttk.Button(popup, text="OK", command = popup.destroy)
        B1.pack()
        popup.mainloop()
    
    def chooseArduinoIP(self):
        if self.testRunning == True: 
            self.popupmsg('The program is still running.')
        elif self.testStopped == False: 
            self.popupmsg("The program is being stopped. This can take a while.")
        else:
            newArduinoIP = simpledialog.askstring("Arduino IP", "Enter Arudino IP address. \n\nFor default value enter: default\n" ,parent=self.root)
            if newArduinoIP != None and newArduinoIP:
                if newArduinoIP == "default" or newArduinoIP == "Default" or newArduinoIP == "DEFAULT":
                    self.ipArduino = "A1:F8:14:CE:BA:AC"
                else:
                    self.ipArduino = newArduinoIP
            self.ipArduinoLabel.config(text = "Arduino IP: " + self.ipArduino)
        
    def chooseRobotIP(self):
        if self.testRunning == True: 
            self.popupmsg('The program is still running.')
        elif self.testStopped == False: 
            self.popupmsg("The program is being stopped. This can take a while.")
        else:
            newRobotIP = simpledialog.askstring("Robot IP", "Enter Robot IP address. \n\nFor default value enter: default\n",parent=self.root)
            if newRobotIP != None and newRobotIP:
                if newRobotIP == "default" or newRobotIP == "Default" or newRobotIP == "DEFAULT":
                    self.ipRobot = '152.94.0.39'
                else:
                    self.ipRobot = newRobotIP
                #self.mu = rws7class_vir.rws7('127.0.0.1')
                self.mu = RWS.rws7(self.ipRobot)
            self.ipRobotLabel.config(text = "Robot IP: " + self.ipRobot)

    def createApp(self, root):
        
        canvas = tk.Canvas(root, height=710, width=450)
        canvas.pack()

        # Heading
        folderLabel = tk.Label(root, text="TATEM TEST", font = ("Arial",18), padx=2, pady=2, width=30)
        folderLabel.place(x=10,y=5)

        pp2mainbutton = tk.Button(root, text = "Set pp2main", fg = "black", padx=10, pady=10, font = ("Arial",12), width = 12, command=self.setpp2main)
        pp2mainbutton.place(x=50,y=50)

        resetButton = tk.Button(root, text = "Reset Arduino", fg = "black", padx=10, pady=10, font = ("Arial",12), width = 12,command=self.resetArduino) # Not sure how to do this one, will have to do changes to RapidCode as well
        resetButton.place(x=250,y=50)

        startButton = tk.Button(root, text = "Start Test", fg = "black", bg="#3D9140", padx=10, pady=10, font = ("Arial",12, "bold"), width = 11, command=self.startTest) # Not sure this will work
        startButton.place(x=50,y=130)

        stopButton = tk.Button(root, text = "Stop Test", fg = "black", bg="#EE4000", padx=10, pady=10, font = ("Arial",12, "bold"), width = 11, command=self.stopTest)
        stopButton.place(x=250,y=130)

        self.testStatusLabel = tk.Label(root, text=" ", font = ("Arial",12, "bold"), borderwidth=2, padx=4, pady=4)
        self.testStatusLabel.place(x=50,y=180)
        
        # Choosing file location
        folderLabel = tk.Label(root, text="Choose folder for file location:", font = ("Arial",10), padx=2, pady=2)
        folderLabel.place(x=50,y=210)

        folderButton = tk.Button(root, text="Select folder", font = ("Arial",10), command=self.getFolderLocation)
        folderButton.place(x=50,y=240)

        self.fileDirectoryLabel = tk.Label(root, text=self.filepath, font = ("Arial",10),borderwidth=2, width=30, relief="ridge", padx=4, pady=4)
        self.fileDirectoryLabel.place(x=150,y=240)
        
        # Choosing Arduino and Robot IP-addresses
        ipArduinoButton = tk.Button(root, text="Change Arduino IP", font = ("Arial",10), command=self.chooseArduinoIP)
        ipArduinoButton.place(x=280,y=280)
        
        self.ipArduinoLabel = tk.Label(root, text="Arduino IP: A1:F8:14:CE:BA:AC", font = ("Arial",10))
        self.ipArduinoLabel.place(x=50,y=280)
        
        ipRobotButton = tk.Button(root, text="Change Robot IP", font = ("Arial",10), command=self.chooseRobotIP)
        ipRobotButton.place(x=280,y=330)
        
        self.ipRobotLabel = tk.Label(root, text="Robot IP: 152.94.0.39", font = ("Arial",10))
        self.ipRobotLabel.place(x=50,y=330)
        
        # Display test events
        self.eventText = tk.Text(root, height=15, width=43, font = ("Arial",10))
        self.eventText.place(x=50,y=410)
        
        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)

        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    testApp = TestApp(root)
    testApp.createApp(root)
