from MicroPy import MicroPyStateMachine
from time import sleep


def do1(args):
    print('do1')
    return 1, []

def do2(args):
    print('do2')
    return 0, []


########
# main #
########
def main():
    SM = MicroPyStateMachine(2)
    SM.stateBindings.append(do1)
    SM.stateBindings.append(do2)
    SM.currentState = 0

    for i in range(5):
        SM.run()
        sleep(1)

    print('-----------------')
    SM.loopDelay = 1
    SM.run_InternalLoop(0)

main()