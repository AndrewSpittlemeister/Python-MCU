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