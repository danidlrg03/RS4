# from pickle import TRUE
import rws7class
import rws7class_vir
import time
from datetime import datetime
import os
import tatemCom


### CODE FOR SAVING VALUES IN FILE - only for testing purposes
def writetofile(text):
    e = datetime.now()
    filename = e.strftime("%Y-%m-%d_%H-%M-%S")+'.txt'
    filedir = 'C:\TFS\Paint\GIT\TATEM\datasets\TATEMFILES\\'
    foldername = e.strftime("%Y-%m-%d\\")
    isDir = os.path.exists(filedir)
    isFolder = os.path.exists(filedir+foldername)

    if not isDir: os.makedirs(filedir)
    if not isFolder: os.makedirs(filedir+foldername)

    with open(filedir+foldername+filename, 'a', encoding='utf-8') as f:
        f.write(text)
        f.close()

### TRYING THE CODE FOR COLLECTING THE REPORT - only temporary solution (will need to incorporate this into the tatemCom file later)
def get_report(address, filedir):
    print(f'get report from TATEM on address {address}')
    report = tatemCom.asyncio.run( tatemCom.run_remote_cmd( 'getreport', address ) )
    if report[-2:]=='$0':
        #self.poutput('Report received:')
        repDict = tatemCom.json.loads(report[:-2])
    else:
        print( 'Not able to convert report from json to dict:', report )
        repDict = None
    #print( report )
    tatemCom.writeFile(repDict, filedir)
    return repDict


## CODE FOR CONNECTING TO THE ROBOT
def tatemTest(mu, ipaddress, filedir):
    failedReports = 0
    cyclesRun = 0
    while True:
        print("-----")
        print(mu.getexecstat())
        if mu.getexecstat() == "stopped":
            print("You need to restart the robot manually on the teach pendant before running the program")
            break
        if mu.getsymval('T_ROB1','TrigTest','finished') == "TRUE":
            mu.stop()
            print(mu.getexecstat())
            print("Getting report and resetting the arduino")
            print("collecting report...")
            try:
                report = get_report(ipaddress, filedir)
            except:
                failedReports = failedReports + 1
                print("Something went wrong when collecting the report. There will be no report from this run.")
            else:
                print("Report collected successfully")
            mu.reqmast()
            mu.setsymval('T_ROB1','TrigTest','report',"TRUE") # Sending information to Rapid that the report has been collected successfully
            time.sleep(0.5)
            if (mu.getsymval('T_ROB1','TrigTest','report')) != "TRUE":
                print("ERROR: The report-variable was not properly changed in the rapid code.")
                mu.relmast()
                break
            mu.setsymval('T_ROB1','TrigTest','resetArduino',"TRUE") # Triggering the resetting of values in the arduino (Will trigger I/O on/off in Rapid two times)
            time.sleep(0.5)
            if (mu.getsymval('T_ROB1','TrigTest','resetArduino')) != "TRUE":
                print("ERROR: The resetArduino-variable was not properly changed in the rapid code.")
                mu.relmast()
                break
            print("The Arduino is to be reset...")
            mu.relmast()
            mu.start() # By starting the Rapid program again, the resetting of values will be triggered
            print(mu.getexecstat())
            counter = 0
            while counter < 10:
                #print(mu.getsymval('T_ROB1','TrigTest','resetSuccess'))
                if mu.getsymval('T_ROB1','TrigTest','resetSuccess') == "TRUE":
                    break
                counter = counter + 1
                time.sleep(1)
            if mu.getsymval('T_ROB1','TrigTest','resetSuccess') == "FALSE":
                mu.stop()
                print("ERROR: The reset was NOT successful. Reset the Arduino manually before restarting the program.")
                break
            elif (mu.getexecstat() == "stopped"):
                print("The robot has been stopped. The test will not continue.")
                break
            else:
                print("The Arduino has been reset")
                print("The robot is ready to go into another cycle")
            cyclesRun = cyclesRun + 1
        print("Total number of cycles run: " + str(cyclesRun))
        print("Total number of failed reports: " + str(failedReports))
        time.sleep(1)
    print("TEST STOPPED")
        
def tatemTest_vir(mu, ipaddress, filedir):
    while True:
        print("-----")
        print(mu.getexecstat())
        if mu.getexecstat() == "stopped":
            print("You need to restart the robot manually on the teach pendant before running the program")
            break
        if mu.getsymval('T_ROB1','Module1','finished') == "TRUE":
            mu.stop()
            print(mu.getexecstat())
            print("Getting report and resetting the arduino")
            print("collecting report...")
            report = 2
            if report == None:
                print("Something went wrong when collecting the report")
                break
            else:
                print("Report collected successfully")
                mu.reqmast()
                mu.setsymval('T_ROB1','Module1','report',"TRUE") # Sending information to Rapid that the report has been collected successfully
                if (mu.getsymval('T_ROB1','Module1','report')) != "TRUE":
                    print("ERROR: The report-variable was not properly changed in the rapid code.")
                    mu.relmast()
                    break
                mu.setsymval('T_ROB1','Module1','resetArduino',"TRUE") # Triggering the resetting of values in the arduino (Will trigger I/O on/off in Rapid two times)
                if (mu.getsymval('T_ROB1','Module1','resetArduino')) != "TRUE":
                    print("ERROR: The resetArduino-variable was not properly changed in the rapid code.")
                    mu.relmast()
                    break
                print("The report has been collected and the Arduino is to be reset...")
                mu.relmast()
                # TO_DO: Add a failsafe here - only start again if it is safe to do so
                mu.start() # By starting the Rapid program again, the resetting of values will be triggered
                print(mu.getexecstat())
                counter = 0
                while counter < 10:
                    print(mu.getsymval('T_ROB1','Module1','resetSuccess'))
                    if mu.getsymval('T_ROB1','Module1','resetSuccess') == "TRUE":
                        break
                    counter = counter + 1
                    time.sleep(1)
                if mu.getsymval('T_ROB1','Module1','resetSuccess') == "FALSE":
                    mu.stop()
                    print("ERROR: The reset was NOT successful. Reset the Arduino manually before restarting the program.")
                    break
                else:
                    print("The Arduino has been reset")
                    print("The robot is ready to go into another cycle")
        time.sleep(1)
    print("TEST STOPPED")



# Do not need to request mastership for starting/stopping for now
# Do need to request it for setting the values though
# This works for now for the real robot, given that you first start the robot from the teach pendant
def testCom(mu):
    print(mu.getexecstat())
    print(mu.getsymval('T_ROB1','TrigTest','finished'))
    print(mu.getsymval('T_ROB1','TEST_COM','testVar'))
    mu.stop()
    print(mu.getexecstat())
    time.sleep(2)
    mu.start()
    print(mu.getexecstat())
    time.sleep(2)
    mu.stop()
    mu.reqmast()
    mu.setsymval('T_ROB1','TEST_COM','testVar', 12)
    mu.relmast()
    print(mu.getsymval('T_ROB1','TEST_COM','testVar'))
    mu.start()
    print(mu.getexecstat())
    time.sleep(1)
    mu.stop()
    
    
# TO_DO: add the opportunity to switch the module name and robot name and IP adress(?) when calling the function
# Can then choose if it should be virtual or not
# TO_DO: Need to have a way of finding the correct IP address to enter for connecting to the arduino
if __name__ == "__main__":
    mu_vir = rws7class_vir.rws7('127.0.0.1')
    mu_conn = rws7class.rws7('192.168.125.1')
    mu_tatem = rws7class.rws7('10.47.89.50')
    #tatemTest_vir(mu)
    #testCom(mu_conn)
    ipaddress = "1C:F3:A4:84:91:47"
    filedir = 'C:\TFS\TATEM\datasets\\'
    #tatemTest(mu_conn, ipaddress, filedir)
    tatemTest_vir(mu_vir, ipaddress, filedir)
