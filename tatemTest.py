import threading
import time

# Initializes and runs the TATEM test
class runTatemTest(threading.Thread):
    # Creating the test object. Contains the BLE-object and the robot-object.
    def __init__(self, arduino, robot):
        self.Arduino = arduino # The connected bluetooth object
        self.Robot = robot # The rws object of the robot
        self.stop = False
        
        threading.Thread.__init__(self)
        self.start()
    
    # Running the TATEM-test. This function overrides the "run"-function in the thread class. 
    def run(self):
        while self.stop == False: # Will first check that the "stoptest"-variable has not been changed
            self.Robot.StartCycle() # Then we will start the robot
            time.sleep(1)
            if self.Robot.RobotState() == "stopped":
                print("Was not able to start the robot.")
                self.stop = True # Not sure this is necessary
                break
            while self.Robot.GetCycleStatus() == "InProgress" and self.stop == False: # Remain passive while the robot is running in its cycle
                time.sleep(1)
            if self.stop == True or self.Robot.GetCycleStatus() == "Stopped":
                print("Program stopped. You may need to collect the report and reset the Arduino manually before starting again.")
                break
            elif self.Robot.GetCycleStatus() == "Finished": # Waiting for the cycle to finish
                if self.Arduino.IsConnected():
                    try:
                        self.Arduino.GetReport() # Fetching the data from the Arduino
                    except:
                        print("Something went wrong when collecting the data")
                    try:
                        self.Arduino.Reset() # Resetting the Arduino
                    except:
                        print("Something went wrong when resetting the arduino")
                else:
                    print("Connection to Arduino is lost. Collect report and reset Arduino manually before continuing.")
                    self.stop = True # Not sure this is necessary
                    break
                    # Maybe want to try to restart the connection here instead - see if we can get it up and running again before collecting the report
    
    # Stopping both the test and the robot.
    def stopTest(self):
        self.stop = True
        self.Robot.StopCycle()

def main():
    
    print("Hello")

if __name__ == "__main__":
    main()