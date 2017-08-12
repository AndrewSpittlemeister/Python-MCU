from MicroPy import MicroPyInterrupt
import time

# Test Edit

def do_something():
    print(time.time() - T[0])
    T[0] = time.time()
    print('doing something')


def do_something_else():
    print(time.time() - T[0])
    T[0] = time.time()
    print('doing something else')

T = [time.time()]

#########
# Main: #
#########
def main():
    myTimer = MicroPyInterrupt(2, do_something)
    myTimer.benchmark_time = time.time()
    myTimer.start()

    time.sleep(5)  # Should trigger 2 times

    print('changing interval')
    myTimer.changeActiveInterval(3)  # function to change interval while timer-interrupt is live.
    T[0] = time.time()
    time.sleep(7)  # should trigger 2 times

    print('changing function')
    myTimer.changeActiveEvent(
        do_something_else)  # method to change interrupt event function while timer-interrupt is live.
    T[0] = time.time()
    time.sleep(7)  # Should trigger 2 times

    # note that both change methods reset the timer.

    print('done')
    myTimer.stop()


main()