# Commented rws7class and replaced it with RWS used at UiS
# Replaced all the functions used from rws7class with their counter parts from RWS
# Also used some other functions from RWS that do the job of some the code in this file

# import rws7class
from rwsuis import RWS
from datetime import datetime

# All necessary communication with the robot controller is handled from here.
class TatemRapidIf:
    # Creating the rapid-object representing the robot
    def __init__(self, ip):
        self.ip = ip
        self.mu= None
    
    # Creating the rws-object for communication with the robot
    def Connect(self):
        self.mu = RWS.RWS(self.ip)

    # Deleting the rws-object
    def Disconnect(self):
        self.mu = None
    
    # Checking if there is a connection to the robot. Will create a time-out error if there is no connection.
    def CheckConnection(self):
        connection = False
        status = self.mu.get_execution_state()
        if status != None:
            connection = True
        return connection
    
    # Staring the robot
    def StartCycle(self):
        if self.mu == None:
            print("No robot is connected.")
        else:
            if self.mu.is_running():
                print("The program is already running.")
            else:
                self.mu.start_RAPID()
                if self.mu.get_execution_state() == "stopped":
                    print('The robot cannot be started from here. Please start the robot manually on the teach pendant.')
    
    # Stopping the robot
    def StopCycle(self):
        if self.mu == None:
            print("No robot is connected.")
        else:
            self.mu.stop_RAPID()
        pass

    # Retrieving the robot state ("running" or "stopped")
    def RobotState(self):
        if self.mu == None:
            return "No robot is connected."
        else:
            return self.mu.get_execution_state()
    
    # Retrieving which part of the cycle the robot is in
    def GetCycleStatus(self):
        if self.mu == None:
            return "No robot is connected."
        else:
            status = self.mu.get_rapid_variable('finished')
            runState = self.mu.get_execution_state()
            if status == "TRUE" and runState == "stopped": # Waiting to collect the report and resetting the arduino before being started again
                return "Finished"
            elif status == "FALSE" and runState == "stopped": # Could either mean that the program has not yet started or that the robot was stopped during the run
                return "Stopped"
            elif status == "FALSE" or runState == "running": # Means that the program is running in its cycle
                return "InProgress"
            else:
                return "Undefined"
    
    # This is not necessary
    # Retrieving the tA-value from the rapid-code
    def GettA(self):
        tA = self.mu.get_rapid_variable('tA')
        return tA
    
    # Retrieving the tO-value from the rapid-code
    def GettO(self):
        tO = self.mu.get_rapid_variable('tOp')
        return tO
    
    # Retrieving the tR-value from the rapid-code
    def GettR(self):
        tR = self.mu.get_rapid_variable('tR')
        return tR


def main():
    tatemRapidIf = TatemRapidIf('10.47.89.50')
    tatemRapidIf.Connect()
    print(" Robot is in state {}".format( tatemRapidIf.RobotState()) )
    tatemRapidIf.DisConnect()

if __name__ == "__main__":
    main()