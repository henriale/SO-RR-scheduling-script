# todo: move scheduler into this module
from main import Scheduler


class Reader:
    def __init__(self, filename):
        self.file = open(filename)

    def read_scheduler(self):
        processes_count = int(self.file.readline())
        timeslice = int(self.file.readline())
        processes = []

        # data format: AT BT P
        for number, line in enumerate(self.file.readlines(), start=1):
            line_data = []
            for x in line.split(" "):
                line_data.append(int(x))

            if len(line_data) == 3:
                process = Process(number, line_data[0], line_data[1], line_data[2], [])
                processes.append(process)

            elif len(line_data) >= 4:
                io_times = []
                for i in range(3, len(line_data)):
                    io_times.append(line_data[i])
                process = Process(number, line_data[0], line_data[1], line_data[2], io_times)
                processes.append(process)

        self.file.close()

        return Scheduler(processes, timeslice)


class Process:
    def __init__(self, number, arrival_time, burst_time, priority, io_times):
        self.number = number
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_burst = burst_time
        self.priority = priority
        self.quantum_counter = 0
        self.turn_around_time = 0
        self.response_time = -1
        self.waiting_time = 0
        self.completion_time = 0
        self.io_times = io_times
        self.io_counter = 0

    def get_number(self):
        return self.number

    def get_arrival_time(self):
        return self.arrival_time

    def get_burst_time(self):
        return self.burst_time

    def get_remaining_burst(self):
        return self.remaining_burst

    def get_priority(self):
        return self.priority

    def get_response_time(self):
        return self.response_time

    def get_waiting_time(self):
        return self.waiting_time

    def get_quantum_counter(self):
        return self.quantum_counter

    def get_turn_around_time(self):
        return self.turn_around_time

    def get_completion_time(self):
        return self.completion_time

    def get_io_times(self):
        return self.io_times

    def get_io_counter(self):
        return self.io_counter


    # Executes Process for one time unit
    def execute(self, time):
        self.remaining_burst -= 1
        self.quantum_counter += 1

        if self.response_time == -1:
            self.response_time = time - self.arrival_time

    def start_io(self):
        if (self.burst_time - self.remaining_burst) in self.io_times:
            self.io_counter = 4
            self.io_times.remove(self.burst_time - self.remaining_burst)
            return True
        return False

    def run_io(self):
        self.io_counter -= 1

    def reset_quantum_counter(self):
        self.quantum_counter = 0

    def is_done(self):
        return self.get_remaining_burst() <= 0

    # calculates requested data
    def finish(self, time):
        self.completion_time = time
        self.turn_around_time = self.completion_time - self.arrival_time
        self.waiting_time = self.turn_around_time - self.burst_time
