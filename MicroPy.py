from time import sleep
from types import FunctionType as FT
from threading import Timer


class MicroPyInterrupt:
    """
    Class that allows for repeated timed interrupts that trigger a defined event function.
    """
    def __init__(self, INTERVAL, event_function):
        self.interval = INTERVAL
        self.event = event_function
        self.run = False
        self.timer = 0
        self.event_counter = 0

    def start(self):
        """
        Starts timed interrupt routine.
        :return: Nothing.
        """
        self.run = True
        self.timer = Timer(self.interval, self.interrupt)
        self.timer.start()

    def interrupt(self):
        """
        Wrapper method for the interrupt. Used to trigger event function and then start timer over for next iteration.
        :return: Nothing.
        """
        if self.run:
            self.timer = Timer(self.interval, self.interrupt)
            self.timer.start()
            self.event()
            self.event_counter += 1

    def stop(self):
        """
        Stops timed interrupt routine.
        :return:
        """
        self.run = False
        self.timer.cancel()
        self.event_counter = 0

    def changeActiveInterval(self, interval):
        """
        Allows for changing the time interval between interrupts while the routine is running. This will start timer
            over using the new interval.
        :param interval: Time between interrupts.
        :return: Nothing.
        """
        self.run = False
        self.timer.cancel()
        self.interval = interval
        self.timer = Timer(self.interval, self.interrupt)
        self.run = True
        self.timer.start()

    def changeActiveEvent(self, event_function):
        """
        Allows for changing the event function bound to the interrupt while the routine is running. This will start
            the timer over using the new event function.
        :param event_function: Function bound to interrupt.
        :return: Nothing.
        """
        self.run = False
        self.timer.cancel()
        self.event = event_function
        self.timer = Timer(self.interval, self.interrupt)
        self.run = True
        self.timer.start()

class MicroPyStateMachine:
    """
    Class to aid in using state machines with defined functions for each state.
    """
    def __init__(self, numStates = 0):
        self.numStates = numStates
        self.stateBindings = []
        self.argList = []
        self.metaData = {}
        self.currentState = None
        self.internalLooping = False
        self.loopDelay = 0

    def checkBindings(self):
        """
        Checks if state binding list is populated with the correct number of states of all function type.
        :return: boolean
        """
        if self.numStates == 0:
            print("Error: zero states found.")
            return False
        elif len(self.stateBindings) != self.numStates:
            print("Error: missing state binding.")
            return False
        elif not all(isinstance(x, FT) for x in self.stateBindings):
            print("Error: invalid state binding.")
            return False
        return True

    def run(self):
        """
        Runs a single iteration of the state machine based on the current state. Takes output from functions to
            determine next state as well as create an argument list for the next state's function call.
        :return: Nothing.
        """
        if self.checkBindings():
            self.currentState, self.argList = self.stateBindings[self.currentState](self.argList)

    def run_InternalLoop(self, startState = None):
        """
        Creates an internal loop that iterates through the state machine in the same manner as the run() method.
            Requires a returned negative value as the next state to stop internal looping.
        :param startState: Optional starting state value.
        :return:
        """
        if not self.checkBindings():
            return
        if startState is not None:
            if type(startState) is int and 0 <= startState < self.numStates:
                self.currentState = startState
            else:
                print("Error: invalid start state.")
                return

        self.internalLooping = True
        while self.internalLooping:
            self.currentState, self.argList = self.stateBindings[self.currentState](self.argList)
            if self.currentState < 0:
                self.internalLooping = False
                return
            sleep(self.loopDelay)

class MicroPyBuffer:
    """
    Class wrapper for a simple circular buffer.
    """
    def __init__(self, length, overwrite=True, readChronological=True):
        self.length = length
        self.buffer = []
        self.writer = 0
        self.reader = 0
        self.overwrite = overwrite
        self.readChronological = readChronological
        self.ready = None

        self.typeCheck()
        self.initBuffer()

    def typeCheck(self):
        """
        Checks if necessary fields for the buffer are of the correct type. Will set ready status to true if all fields
            meet the requirements.
        :return: Nothing.
        """
        self.ready = True

        if not type(self.length) is int:
            print("Error: invalid length argument type.")
            self.ready = False
        if not type(self.overwrite) is type(False):
            print("Error: invalid overwrite argument type.")
            self.ready = False
        if not type(self.readChronological) is type(False):
            print("Error: invalid readChronological argument type.")
            self.ready = False

        print("Ready Status: ", self.ready)


    def initBuffer(self):
        """
        Initializes buffer with all None value types.
        :return: Nothing.
        """
        for i in range(self.length):
            self.buffer[i] = None

    def reset(self):
        """
        Resets buffer to initial conditions and resets cursors to 0.
        :return: Nothing.
        """
        self.initBuffer()
        self.reader = 0
        self.writer = 0

    def isReady(self):
        """
        Returns True if parameters for the buffer are of correct type, otherwise False.
        :return: Boolean.
        """
        return self.ready

    def isReadable(self):
        """
        Returns True if there is any data in the buffer, otherwise False.
        :return: Boolean.
        """
        if not self.ready:  # check ready status
            print("Error: not ready to execute.")
            return False

        if self.buffer[self.reader] is None:
            return False
        else:
            return True

    def isWriteable(self):
        """
        Returns True if there is an open spot to write data in the buffer or if overwrite is allowed.
        :return: Boolean.
        """
        if not self.ready:  # check ready status
            print("Error: not ready to execute.")
            return False

        if self.overwrite:
            return True
        elif self.buffer[self.writer] is None:
            return True
        else:
            return False

    def toggleOverwrite(self):
        """
        Toggles overwrite status.
        :return: Nothing.
        """
        if not self.ready:  # check ready status
            print("Error: not ready to execute.")
            return False

        self.overwrite = not self.overwrite

    def toggleReadChronological(self):
        """
        Toggles readChronological status.
        :return: Nothing.
        """
        if not self.ready:  # check ready status
            print("Error: not ready to execute.")
            return False

        self.readChronological = not self.readChronological

    def add(self, data):
        """
        Adds piece of data to the next writeable spot in the buffer, then increments writer cursor. If failed, cursor
            does not increment.
        :param data: Data to be added.
        :return: True for success, False for failure.
        """
        if not self.ready:  # check ready status
            print("Error: not ready to execute.")
            return False

        if self.buffer[self.writer] is None:
            self.buffer[self.writer] = data
            self.writer = (self.writer + 1) % self.length
            return True
        elif self.overwrite:
            self.buffer[self.writer] = data
            self.writer = (self.writer + 1) % self.length
            if self.readChronological:
                self.reader = (self.writer + 1) % self.length
            return True
        else:
            return False

    def get(self):
        """
        Gets next available piece of data in the buffer.
        :return: Data found or None. Returns False if ready status is not met.
        """
        if not self.ready:  # check ready status
            print("Error: not ready to execute.")
            return False

        if self.buffer[self.reader] is None:
            return None
        else:
            data = self.buffer[self.reader]
            self.buffer[self.reader] = None
            self.reader = (self.reader + 1) % self.length
            return data

    def jumpToNew(self):
        """
        Jumps reader to most recently written data in buffer and sets all other values to None.
        :return: Nothing.
        """
        if not self.ready:  # check ready status
            print("Error: not ready to execute.")
            return False

        newIndex = self.reader - 1
        if newIndex < 0:
            newIndex = self.length - 1
        for i in range(self.length):
            if not i == newIndex:
                self.buffer[i] = None
        self.reader = newIndex
        
class MicroPyPID:
    """
    Class wrapper for defining and running a PID control loop.
    """
    def __init__(self, setpoint, CObias, timeDelta = None, upperSumBound = None, lowerSumBound = None, Kc = None, Ki = None, Kd = None):
        self.setpoint = setpoint

        self.CObias = CObias
        self.Kc = Kc
        self.Ki = Ki
        self.Kd = Kd

        self.timeDelta = timeDelta
        self.prevError = 0
        self.errorSum = 0
        self.upperSumBound = upperSumBound
        self.lowerSumBound = lowerSumBound

        self.loopType = self.getLoopType()

        self.ready = None
        self.typeCheck()
        
    def reset(self, setpoint, CObias, timeDelta = None, upperSumBound = None, lowerSumBound = None, Kc = None, Ki = None, Kd = None):
        """
        Resets all PID parameters and starts control loop over.
        :return: Nothing.
        """
        self.setpoint = setpoint

        self.CObias = CObias
        self.Kc = Kc
        self.Ki = Ki
        self.Kd = Kd

        self.timeDelta = timeDelta
        self.prevError = 0
        self.errorSum = 0
        self.upperSumBound = upperSumBound
        self.lowerSumBound = lowerSumBound

        self.loopType = self.getLoopType()

        self.ready = None
        self.typeCheck()
        
    def clear(self):
        """
        Only clears prevError and errorSum to 0.
        :return: Nothing.
        """
        self.prevError = 0
        self.errorSum = 0

    def getLoopType(self):
        """
        Returns the control loop type (P, PI, or PID) based on what parameters were given.
        :return: String containing control loop type.
        """
        loopType = ""
        if self.Kc is not None:
            loopType += 'P'
            if self.Ki is not None:
                loopType += 'I'
                if self.Kd is not None:
                    loopType += 'D'
        return loopType

    def typeCheck(self):
        """
        Verifies that required parameters for the specified control loop type are of the correct type.
        :return: Nothing.
        """
        self.ready = True

        if not (self.loopType == "P" or self.loopType == "PI" or self.loopType == "PID"):
            print("Error: invalid control loop type.")
            self.ready = False
        if not (type(self.setpoint) is float or type(self.setpoint) is int):
            print("Error: invalid setpoint type.")
            self.ready = False
        if not (type(self.CObias) is float or type(self.CObias) is int):
            print("Error: invalid CObias type.")
            self.ready = False

        # check PID constants according to control loop type:
        if 'P' in self.loopType:  # check Kc parameter
            if not (type(self.Kc) is float or type(self.Kc) is int):
                print("Error: invalid Kc type.")
                self.ready = False

            if 'I' in self.loopType:  # check Ki parameter + time delta + sum bound
                if not (type(self.Ki) is float or type(self.Ki) is int):
                    print("Error: invalid Ki type.")
                    self.ready = False
                if not (type(self.timeDelta) is float or type(self.timeDelta) is int):
                    print("Error: invalid timeDelta type.")
                    self.ready = False
                if not (type(self.upperSumBound) is float or type(self.upperSumBound) is int):
                    print("Error: invalid upperSumBound type.")
                    self.ready = False
                if not (type(self.lowerSumBound) is float or type(self.lowerSumBound) is int):
                    print("Error: invalid lowerSumBound type.")
                    self.ready = False

                if 'D' in self.loopType:  # check Kd parameter
                    if not (type(self.Kd) is float or type(self.Kd) is int):
                        print("Error: invalid Kd type.")
                        self.ready = False

        print("Ready Status: ", self.ready)

    def getOutput(self, reading):
        """
        Calculates new controller output based on control loop type.
        :return: Controller output (float) or False (bool) when not ready or invalid input.
        """
        if not self.ready:  # check ready status
            print("Error: not ready to execute.")
            return False

        if not (type(reading) is float or type(reading) is int):  # check if reading is of valid type
            print("Error: invalid reading type.")
            return False

        output = self.CObias

        if 'P' in self.loopType:  # contribute proportional term
            current_error = self.setpoint - reading
            output += self.Kc * current_error

            if 'I' in self.loopType:  # contribute integral term
                self.errorSum += current_error

                # format sum to be within defined range:
                if self.errorSum < self.lowerSumBound:
                    self.errorSum = self.lowerSumBound
                elif self.errorSum > self.upperSumBound:
                    self.errorSum = self.upperSumBound

                output += self.Ki * self.errorSum * self.timeDelta

                if 'D' in self.loopType:  # contribute derivative term
                    errorDelta = current_error - self.prevError
                    output += errorDelta / self.timeDelta

            self.prevError = current_error

        return output

class MicroPyRollingAverage:
    """
    Class wrapper for computing rolling average.
    """
    def __init__(self, sampleSize = None):
        self.sampleSize = sampleSize
        self.average = 0
        self.ready = None
        self.typeCheck()

    def typeCheck(self):
        """
        Verifies that sampleSize is of the correct type and sets ready status.
        :return: Nothing.
        """
        self.ready = True

        if not (type(self.sampleSize) is float or type(self.sampleSize) is int):
            print("Error: invalid sampleSize type.")
            self.ready = False

        print("Ready Status: ", self.ready)

    def getAverage(self, newSample = None):
        """
        Computes latest running average if valid newSample parameter is filled and returns average, otherwise just
            returns the last average.
        :param newSample: Optional parameter to added to the rolling average.
        :return: Latest running average value or False if ready status is False.
        """
        if not self.ready:  # check ready status
            print("Error: not ready to execute.")
            return False

        if newSample is None:  # return average without processing new sample
            return self.average

        elif not (type(newSample) is float or type(newSample) is int):
            print("Error: invalid newSample type.")
            return self.average

        else:  # process new sample and return updated average
            self.average -= self.average / self.sampleSize
            self.average += newSample / self.sampleSize
            return self.average
