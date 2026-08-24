import time


class Timer:

    def __init__(self):
        self.start_time = None


    def start(self):

        self.start_time = time.perf_counter()


    def elapsed_ms(self):

        if self.start_time is None:
            return 0


        return (
            time.perf_counter()
            -
            self.start_time
        ) * 1000