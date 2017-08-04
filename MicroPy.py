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
        CHecks if necessary fields for the buffer are of the correct type. Will set ready status to true if all fields
            meet the requirements.
        :return: Nothing.
        """
        if not type(self.length) is int:
            print("Error: invalid length argument type.")
            self.ready = False
        elif not type(self.overwrite) is type(False):
            print("Error: invalid overwrite argument type.")
            self.ready = False
        elif not type(self.readChronological) is type(False):
            print("Error: invalid readChronological argument type.")
            self.ready = False
        else:
            self.ready = True

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
        if not self.ready:
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
        if not self.ready:
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
        if not self.ready:
            return
        self.overwrite = not self.overwrite
        
    def toggleReadChronological(self):
        """
        Toggles readChronological status.
        :return: Nothing.
        """
        if not self.ready:
            return
        self.readChronological = not self.readChronological
        
    def add(self, data):
        """
        Adds piece of data to the next writeable spot in the buffer, then increments writer cursor. If failed, cursor
            does not increment.
        :param data: Data to be added.
        :return: True for success, False for failure.
        """
        if not self.ready:
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
        if not self.ready:
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
        if not self.ready:
            return
        newIndex = self.reader - 1
        if newIndex < 0:
            newIndex = self.length - 1
        for i in range(self.length):
            if not i == newIndex:
                self.buffer[i] = None
        self.reader = newIndex
