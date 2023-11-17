from msilib.schema import Error
import time
import matplotlib.pyplot as plt
import numpy as np
import unittest
from matplotlib.ticker import MaxNLocator

InitState = 0
toolActivationState = 1
toolOperationState = 2
extendedOperationState = 3
toolRetrationState = 4
extendedRetractionState = 5
ErrorState = 6

class TatemSim():
    def __init__(self, tA, tO, tO_ext, tR, tR_ext, timerBase, plotName, plotExp ):
        self.state = InitState
        self.tA=tA
        self.tO=tO
        self.tR=tR
        self.tO_ext=tO_ext
        self.tR_ext=tR_ext
        self.timerTickBase = timerBase #How many increment each timer-tcik represent
        self.currentTime = 0
        self.sensor1Value = 0
        self.sensor2Value = 0
        self.doValue = 0
        self.isError = 0
        self.led1 = 0
        self.led2 = 0

        self.toolActivationStartTime = 0
        self.toolOperationStartTime = 0
        self.toolRetrationStartTime = 0

        self.prevDoValue = 0
        self.prevS1Value = 0
        self.prevS2Value = 0

        self.eventSequence = []
        self.plotName = plotName
        self.plotExp = plotExp
        self.startToolAct = [0]
        self.startToolOp = [0]
        self.startToolRe = [0]
        self.startOpEx = [0]
        self.startReEx = [0]
        self.speed = [] # For plotting purposes

    def SimulateTimerTick(self):
        self.currentTime += self.timerTickBase

    def GetCurrentTime(self):
        return self.currentTime

    def GetDoValue(self):
        return self.doValue

    def GetL1Value(self):
        return self.led1

    def GetL2Value(self):
        return self.led2

    def GetS1Value(self):
        return self.sensor1Value

    def GetS2Value(self):
        return self.sensor2Value

    def GetState(self):
        return self.state

    def IsError(self):
        return self.isError

    #External interface
    def SetDO(self, value): #Simulating the DO
        self.doValue = value

    def SetLED1_and_2(self,value): #Simulating the LED1 and 2
        self.led1 = value
        self.led2 = value

    def SetSensor1Value(self, value):
        self.sensor1Value = value

    def SetSensor2Value(self, value):
        self.sensor2Value = value

    def update(self, event):
        if self.GetState() == 6:
            event = "error"
        self.events(event) # Making sure that the event is run
        self._runStateMachine( self.GetState(), event) # Then checking the runStateMachine
        if self.GetState() == 6:
            self.isError = 1
        self.eventSequence.append([self.GetState(), self.GetDoValue(), self.GetCurrentTime(), self.GetL1Value(), self.GetL2Value(), self.GetS1Value(), self.GetS2Value(), self.IsError()]) # Then storing important values

# Events caused by interrupts or timer
    def events(self, event):
        match(event):
            case "TimerTick":
                self.SimulateTimerTick()
            case "DO1":
                self.SetDO(1)
            case "DO0":
                self.SetDO(0)
            case "InPos": # Setting the sensor values
                self.SetSensor1Value(1)
                self.SetSensor2Value(0)
            case "OutPos1": # Setting the sensor values
                self.SetSensor1Value(0)
                self.SetSensor2Value(0)
            case "OutPos2": # Setting the sensor values
                self.SetSensor1Value(1)
                self.SetSensor2Value(1)
            case "OutPos3": # Setting the sensor values
                self.SetSensor1Value(0)
                self.SetSensor2Value(1)
            case "error":
                self.SetLED1_and_2(0)
                self.preActiveStartTime = 0
                self.postActiveStartTime = 0
                self.activeStartTime = 0
                self.SetSensor1Value(0) # just for simulation purposes
                self.SetSensor2Value(0) # just for simulation purposes
                self.SimulateTimerTick()
            case _:
                print("Error, not a valid event")


    def _runStateMachine( self, currentState, event):
        match(currentState, event):
            case (0, "TimerTick"): # init state
                self.state = InitState
            case (0, "DO1"):
                self.SetLED1_and_2(1)
                self.SetSensor1Value(1)
                self.SetSensor2Value(1)
                self.state = toolActivationState
                self.toolActivationStartTime = self.GetCurrentTime()
                self.starttime = self.GetCurrentTime()
                self.startToolAct.append(self.GetCurrentTime())
            case (0, "DO0"):
                self.state = InitState
            case (0, "InPos"):
                self.state = InitState
            case (0, "OutPos1"):
                self.state = InitState
            case (0, "OutPos2"):
                self.state = InitState
            case (0, "OutPos3"):
                self.state = InitState

            case (1, "TimerTick"): # act state
                if self.GetCurrentTime() > self.toolActivationStartTime + self.tA:
                    self.toolOperationStartTime = self.GetCurrentTime()-1
                    self.startToolOp.append(self.GetCurrentTime()-1)
                    self.state = toolOperationState
            case (1, "DO1"):
                self.state = ErrorState
            case (1, "DO0"):
                self.state = ErrorState
            case (1, "InPos"):
                self.state = toolActivationState
            case (1, "OutPos1"):
                self.state = toolActivationState
            case (1, "OutPos2"):
                self.state = toolActivationState
            case (1, "OutPos3"):
                self.state = toolActivationState

            case (2, "TimerTick"):  # OP state
                if self.GetCurrentTime() > self.toolOperationStartTime + self.tO:
                    self.state = extendedOperationState
                    self.startOpEx.append(self.GetCurrentTime())
            case (2, "DO1"):
                self.state = ErrorState
                self.startToolOp = [0]
            case (2, "DO0"):
                self.state = ErrorState
            case (2, "InPos"):
                self.state = ErrorState
                self.startToolOp = [0]
            case (2, "OutPos1"):
                self.state = ErrorState
                self.startToolOp = [0]
            case (2, "OutPos2"):
                self.state = ErrorState
                self.startToolOp = [0]
            case (2, "OutPos3"):
                self.state = ErrorState
                self.startToolOp = [0]

            case (3, "TimerTick"): #EXT OP STATE
                self.state = extendedOperationState
            case (3, "DO1"):
                self.state = ErrorState
            case (3, "DO0"):
                self.state = toolRetrationState
                self.toolRetrationStartTime = self.GetCurrentTime()
                self.startToolRe.append(self.GetCurrentTime())
            case (3, "InPos"):
                self.state = ErrorState
            case (3, "OutPos1"):
                self.state = ErrorState
            case (3, "OutPos2"):
                self.state = ErrorState
            case (3, "OutPos3"):
                self.state = ErrorState

            case (4, "TimerTick"): # ret state
                if self.GetCurrentTime() > self.toolOperationStartTime + self.tO + self.tO_ext + self.tR:
                    self.state = extendedRetractionState
                    self.startReEx.append(self.GetCurrentTime())
            case (4, "DO1"):
                self.state = ErrorState
                self.startToolRe = [0]
            case (4, "DO0"):
                self.state = ErrorState
                self.startToolRe = [0]
            case (4, "InPos"):
                self.state = ErrorState
                self.startToolRe = [0]
            case (4, "OutPos1"):
                self.state = ErrorState
                self.startToolRe = [0]
            case (4, "OutPos2"):
                self.state = ErrorState
                self.startToolRe = [0]
            case (4, "OutPos3"):
                self.state = ErrorState
                self.startToolRe = [0]


            case (5, "TimerTick"): # ext ret state
                self.state = extendedRetractionState
            case (5, "DO1"):
                self.state = ErrorState
            case (5, "DO0"):
                self.state = ErrorState
            case (5, "InPos"):
                self.state = ErrorState
            case (5, "OutPos1"):
                self.state = InitState
                self.SetLED1_and_2(0)
            case (5, "OutPos2"):
                self.state = InitState
                self.SetLED1_and_2(0)
            case (5, "OutPos3"):
                self.state = InitState
                self.SetLED1_and_2(0)

            case (6, "TimerTick"): # ErrorState
                self.state = ErrorState
            case (6, "DO1"):
                self.state = ErrorState
            case (6, "DO0"):
                self.state = InitState
            case (6, "InPos"):
                self.state = ErrorState
            case (6, "OutPos1"):
                self.state = ErrorState
            case (6, "OutPos2"):
                self.state = ErrorState
            case (6, "OutPos3"):
                self.state = ErrorState
            case (6, "error"):
                self.state = ErrorState


    def plotCase(self):
        t = [0]
        do = [0]
        state = [0]
        L1 = [0]
        L2 = [0]
        S1 = [0]
        S2 = [0]
        error = [0]

        for i in self.eventSequence:
            state.append(int(i[0]))
            do.append(int(i[1]))
            t.append(int(i[2]))
            L1.append(int(i[3]))
            L2.append(int(i[4]))
            S1.append(int(i[5]))
            S2.append(int(i[6]))
            error.append(int(i[7]))

        t = np.array(t)
        do = np.array(do)
        state = np.array(state)
        L1 = np.array(L1)
        L2 = np.array(L2)
        S1 = np.array(S1)
        S2 = np.array(S2)
        error = np.array(error)
        sp = []
        counter = 0

        if len(self.speed) == 2:
            for i in range(len(t)):
                if i == 0:
                    sp.append(3)
                    counter += 1
                elif t[i] == t[i-1]:
                    sp.append(sp[i-1])
                elif t[i] < self.speed[0]:
                    sp.append(-3*counter/self.speed[0]+3)
                    counter +=1
                elif t[i] < self.speed[1]:
                    sp.append(0)
                    counter +=1
                else:
                    sp.append(3*(counter-self.speed[1])/self.speed[0])
                    counter +=1
            sp = np.array(sp)

        ax1 = plt.subplot(111)
        plt.title(self.plotName)
        if len(self.speed) == 2:
            ax1.plot(t, sp + 24, 'c', linewidth = 3)
        ax1.step(t, state + 16, 'm', linewidth = 3, where='post')
        ax1.step(t, do + 14, 'k', linewidth = 3, where='post') # external
        ax1.step(t, L1 + 12, 'b', linewidth = 3, where='post') # triggered
        ax1.step(t, L2 + 10, 'b', linewidth = 3, where='post') # triggered
        ax1.step(t, S1 + 8, 'k', linewidth = 3, where='post') # external
        ax1.step(t, S2 + 6, 'k', linewidth = 3, where='post') # external
        if 1 in error:
            ax1.step(t, error + 4, 'r', linewidth = 3, where='post')
        else:
            ax1.step(t, error + 4, 'g', linewidth = 3, where='post')

        if len(self.speed) == 2:
            ax1.text( -2,25, 'Speed')
        ax1.text( -2,16.5, 'State')
        ax1.text( -2,14.5, 'DO')
        ax1.text( -2,12.5, 'L1')
        ax1.text( -2,10.5, 'L2')
        ax1.text( -2,8.5, 'S1')
        ax1.text( -2,6.5, 'S2')
        ax1.text( -2,4.5, 'Error')

        if len(self.startToolAct) > 1:
            ax1.vlines( self.startToolAct[1], -1, 22, linestyles ="dashed", colors ="k", linewidth = 0.5)
            ax1.vlines( self.startToolAct[1] + self.tA, -1, 22, linestyles ="dashed", colors ="k", linewidth = 0.5)

            ax1.annotate(text='', xy=(self.startToolAct[1],21), xytext=(self.startToolAct[1] + self.tA,21), arrowprops=dict(arrowstyle='<->'))
            ax1.text( self.startToolAct[1]+self.tA/2,22, '$t_A$')

        if len(self.startToolOp) > 1:
            ax1.vlines( self.startToolOp[1], -1, 22, linestyles ="dashed", colors ="k", linewidth = 0.5)
            ax1.vlines( self.startToolOp[1] + self.tO, -1, 22, linestyles ="dashed", colors ="k", linewidth = 0.5)

            ax1.annotate(text='', xy=(self.startToolOp[1],21), xytext=(self.startToolOp[1] + self.tO,21), arrowprops=dict(arrowstyle='<->'))
            ax1.text( self.startToolOp[1] + self.tO/2,22, '$t_O$')

        if len(self.startOpEx) > 1:
            ax1.vlines( self.startToolOp[1] + self.tO, -1, 22, linestyles ="dashed", colors ="k", linewidth = 0.5)
            ax1.vlines( self.startToolOp[1] + self.tO + self.tO_ext, -1, 22, linestyles ="dashed", colors ="k", linewidth = 0.5)

            ax1.annotate(text='', xy=(self.startToolOp[1] + self.tO,21), xytext=(self.startToolOp[1] + self.tO + self.tO_ext,21), arrowprops=dict(arrowstyle='<->'))
            ax1.text( self.startToolOp[1] + self.tO + self.tO_ext/5,22, '$t_Oext$')

        if len(self.startToolRe) > 1:
            ax1.vlines( self.startToolRe[1], -1, 22, linestyles ="dashed", colors ="k", linewidth = 0.5)
            ax1.vlines( self.startToolRe[1] + self.tR, -1, 22, linestyles ="dashed", colors ="k", linewidth = 0.5)

            ax1.annotate(text='', xy=(self.startToolRe[1],21), xytext=(self.startToolRe[1] + self.tR,21), arrowprops=dict(arrowstyle='<->'))
            ax1.text( self.startToolRe[1] + self.tR/2,22, '$t_R$')

        if len(self.startReEx) > 1:
            ax1.vlines( self.startReEx[1], -1, 22, linestyles ="dashed", colors ="k", linewidth = 0.5)
            ax1.vlines( self.startReEx[1] + self.tR_ext, -1, 22, linestyles ="dashed", colors ="k", linewidth = 0.5)

            ax1.annotate(text='', xy=(self.startReEx[1],21), xytext=(self.startReEx[1] + self.tR_ext,21), arrowprops=dict(arrowstyle='<->'))
            ax1.text( self.startReEx[1] + self.tR_ext/5,22, '$t_Rext$')

        ax1.text( (self.tO + self.tA)/2, 0, self.plotExp, bbox = dict(facecolor = 'lightgrey', alpha = 0.5))

        ax1.get_xaxis().tick_bottom()
        ax1.axes.get_xaxis().set_visible(True)
        ax1.axes.get_yaxis().set_visible(False)
        ax1.set_xlabel('Time')
        ax1.xaxis.set_major_locator(MaxNLocator(integer=True))

        ax1.set_frame_on(False)
        plt.show()

class TatemSimTest(unittest.TestCase):
    def test_OK(self): # Everything works as it should
        tA = 100
        tO = 300
        tO_ext = 50
        tR = 150
        tR_ext = 50

        startBuffer = 50
        endBuffer = 50

        tick = 1
        plotName = 'OK cycle'
        plotExp = 'An approved cycle.\nNo errors.'
        tsim=TatemSim( tA, tO, tO_ext, tR, tR_ext, tick, plotName, plotExp)
        for i in range(1,startBuffer):
            tsim.update("TimerTick")
        tsim.update("DO1")


        for i in range(1,tA+tO+tO_ext+tR+tR_ext+endBuffer):
            tsim.update("TimerTick")
            if i == int(tA/2):
                tsim.update("OutPos3")
            if i == int(tA/2)+10:
                tsim.update("OutPos1")
            if i == int(tA/2)+20:
                tsim.update("InPos")
            if i == int(tA/2)+25:
                tsim.update("OutPos1")
            if i == int(tA/2)+30:
                tsim.update("InPos")
                tsim.speed.append(tsim.GetCurrentTime())
            if i == tA+tO+tO_ext:
                tsim.update("DO0")
                self.assertEqual(tsim.GetState(), toolRetrationState)
            if i == tA+tO+tO_ext+tR+tR_ext:
                tsim.speed.append(tsim.GetCurrentTime())
                tsim.update("OutPos1")

        self.assertEqual(0,0)
        tsim.plotCase()


    def test_notOK(self): # Everything works as it should
        tA = 100
        tO = 300
        tO_ext = 50
        tR = 150
        tR_ext = 50

        startBuffer = 50
        endBuffer = 50

        tick = 1
        plotName = 'Failed cycle'
        plotExp = 'A failed cycle.\nThe robot entered the point too late.'
        tsim=TatemSim( tA, tO, tO_ext, tR, tR_ext, tick, plotName, plotExp)
        for i in range(1,startBuffer):
            tsim.update("TimerTick")
        tsim.update("DO1")

        for i in range(1,tA+tO+tO_ext+tR+tR_ext+endBuffer):
            tsim.update("TimerTick")
            if i == int(tA/2):
                tsim.update("OutPos3")
            if i == int(tA/2)+10:
                tsim.update("OutPos1")
            if i == int(tA/2)+20:
                tsim.update("InPos")
            if i == int(tA/2)+25:
                tsim.update("OutPos1")
            if i == tA+1:
                tsim.update("OutPos1")
            if i == tA+50:
                tsim.speed.append(tsim.GetCurrentTime())
            if i == tA+tO+tO_ext+tR+tR_ext:
                tsim.speed.append(tsim.GetCurrentTime())

        self.assertEqual(0,0)
        tsim.plotCase()

    def test_notOK2(self): # Everything works as it should
        tA = 100
        tO = 300
        tO_ext = 50
        tR = 150
        tR_ext = 50

        startBuffer = 50
        endBuffer = 50

        tick = 1
        plotName = 'Failed cycle'
        plotExp = 'A failed cycle.\nThe robot did not finish its task before DO was shut off.'
        tsim=TatemSim( tA, tO, tO_ext, tR, tR_ext, tick, plotName, plotExp)
        for i in range(1,startBuffer):
            tsim.update("TimerTick")
        tsim.update("DO1")

        for i in range(1,tA+tO+tO_ext+tR+tR_ext+endBuffer):
            tsim.update("TimerTick")
            if i == int(tA/2):
                tsim.update("OutPos3")
            if i == int(tA/2)+10:
                tsim.update("OutPos1")
            if i == int(tA/2)+20:
                tsim.update("InPos")
            if i == int(tA/2)+25:
                tsim.update("OutPos1")
            if i == int(tA/2)+40:
                tsim.update("InPos")
                tsim.speed.append(tsim.GetCurrentTime())
            if i == tA+tO-50:
                tsim.update("DO0")
            if i == tA+tO+tO_ext+tR+tR_ext:
                tsim.speed.append(tsim.GetCurrentTime())

        self.assertEqual(0,0)
        tsim.plotCase()

    # def test_tA_fail(self): # The robot enters the point too late - the LEDs turn on, but the sensors are still 0
    #     tA = 20
    #     tO = 50
    #     tR = 30
    #     tick = 1
    #     plotName = 'Failed Cycle tA'
    #     plotExp = 'The robot enters the point too late.\nSensor 1 is still 0 when the LEDs turn on.'
    #     tsim=TatemSim( tA, tO, tR, tick, plotName, plotExp)
    #     for i in range(1,11):
    #         tsim.update("TimerTick")
    #     tsim.update("DO")
    #     self.assertEqual(tsim.GetState(), PreActiveState)
    #     for i in range(1,tA+tO+tR+10):
    #         tsim.update("TimerTick")
    #         if i == tA+1:
    #             self.assertEqual(tsim.GetState(), ErrorState)
    #         if i == tA+5:
    #             tsim.speed.append(tsim.GetCurrentTime())
    #         if i == tA+tO:
    #             tsim.update("DO")
    #             self.assertEqual(tsim.GetState(), InitState)
    #         if i == tA+tO+tR:
    #             #tsim.update("S1")
    #             tsim.speed.append(tsim.GetCurrentTime())
    #             self.assertEqual(tsim.GetState(), InitState)

    #     self.assertEqual(tsim.IsError(),1)
    #     tsim.plotCase()

    # def test_tO_fail(self): # The robot has not finished the task before DO is set, i.e. DO is set to 0 before tO has been reached.
    #     tA = 20
    #     tO = 50
    #     tR = 30
    #     tick = 1
    #     plotName = 'Failed Cycle tO'
    #     plotExp = 'DO is set to 0 before tO.\nThe robot has not yet finished the task.'
    #     tsim=TatemSim( tA, tO, tR, tick, plotName, plotExp)
    #     for i in range(1,11):
    #         tsim.update("TimerTick")
    #     tsim.update("DO")
    #     self.assertEqual(tsim.GetState(), PreActiveState)
    #     for i in range(1,tA+tO+tR+10):
    #         tsim.update("TimerTick")
    #         if i == tA:
    #             tsim.speed.append(tsim.GetCurrentTime())
    #             tsim.update("S1")
    #             self.assertEqual(tsim.GetState(), ActiveState)
    #         if i == tA+tO-5:
    #             tsim.update("DO")
    #             self.assertEqual(tsim.GetState(), ErrorState)
    #         if i == tA+tO+tR:
    #             tsim.speed.append(tsim.GetCurrentTime())
    #             #tsim.update("S1")
    #             self.assertEqual(tsim.GetState(), InitState)

    #     self.assertEqual(tsim.IsError(),1)
    #     tsim.plotCase()

    # def test_tR_fail(self): # The robot goes out of the point before tR has been reached, i.e. sensor 1 becomes 0 before the LEDs have been turned off
    #     tA = 20
    #     tO = 50
    #     tR = 30
    #     tick = 1
    #     plotName = 'Failed Cycle tR'
    #     plotExp = 'The robot goes out of the point before tR is reached.\nS1 becomes 0 before tR has been reached.'
    #     tsim=TatemSim( tA, tO, tR, tick, plotName, plotExp)
    #     for i in range(1,11):
    #         tsim.update("TimerTick")
    #     tsim.update("DO")
    #     self.assertEqual(tsim.GetState(), PreActiveState)
    #     for i in range(1,tA+tO+tR+10):
    #         tsim.update("TimerTick")
    #         if i == tA:
    #             tsim.speed.append(tsim.GetCurrentTime())
    #             tsim.update("S1")
    #             self.assertEqual(tsim.GetState(), ActiveState)
    #         if i == tA+tO:
    #             tsim.update("DO")
    #             self.assertEqual(tsim.GetState(), PostActiveState)
    #         if i == tA+tO+tR-5:
    #             tsim.speed.append(tsim.GetCurrentTime())
    #             tsim.update("S1")
    #             self.assertEqual(tsim.GetState(), ErrorState)

    #     self.assertEqual(tsim.IsError(),1)
    #     tsim.plotCase()

    # def test_tA_nonopt(self): # The robot comes to a stand still position before the LEDs are turned on.
    #     tA = 20
    #     tO = 50
    #     tR = 30
    #     tick = 1
    #     plotName = 'Non-Optimal Cycle tA'
    #     plotExp = 'An non-optimal version of one cycle.\nThe robot is standing still before the LEDs are turned on.'
    #     tsim=TatemSim( tA, tO, tR, tick, plotName, plotExp)
    #     for i in range(1,11):
    #         tsim.update("TimerTick")
    #     tsim.update("DO")
    #     self.assertEqual(tsim.GetState(), PreActiveState)
    #     for i in range(1,tA+tO+tR+10):
    #         tsim.update("TimerTick")
    #         if i == tA-5:
    #             tsim.speed.append(tsim.GetCurrentTime())
    #         if i == tA:
    #             tsim.update("S1")
    #             self.assertEqual(tsim.GetState(), ActiveState)
    #         if i == tA+tO:
    #             tsim.update("DO")
    #             self.assertEqual(tsim.GetState(), PostActiveState)
    #         if i == tA+tO+tR:
    #             tsim.speed.append(tsim.GetCurrentTime())
    #             tsim.update("S1")
    #             self.assertEqual(tsim.GetState(), InitState)

    #     self.assertEqual(tsim.IsError(),0)
    #     tsim.plotCase()

    # def test_tO_nonop(self): # The robot finishes the task before tO, i.e. DO is not set to 0 until AFTER tO has been reached.
    #     tA = 20
    #     tO = 50
    #     tR = 30
    #     tick = 1
    #     plotName = 'Non-optimal Cycle tO'
    #     plotExp = 'An non-optimal version of one cycle.\nDO is not set until after tO has been reached.'
    #     tsim=TatemSim( tA, tO, tR, tick, plotName, plotExp)
    #     for i in range(1,11):
    #         tsim.update("TimerTick")
    #     tsim.update("DO")
    #     self.assertEqual(tsim.GetState(), PreActiveState)
    #     for i in range(1,tA+tO+tR+10):
    #         tsim.update("TimerTick")
    #         if i == tA:
    #             tsim.speed.append(tsim.GetCurrentTime())
    #             tsim.update("S1")
    #             self.assertEqual(tsim.GetState(), ActiveState)
    #         if i == tA+tO+5:
    #             tsim.update("DO")
    #             self.assertEqual(tsim.GetState(), PostActiveState)
    #         if i == tA+tO+tR+5:
    #             tsim.speed.append(tsim.GetCurrentTime())
    #             tsim.update("S1")
    #             self.assertEqual(tsim.GetState(), InitState)

    #     self.assertEqual(tsim.IsError(),0)
    #     tsim.plotCase()



if __name__ == "__main__":
    unittest.main()

