class Reader:
    def __init__(self, filename):
        self.file = open(filename)

    def read(self):
        processes_count = int(self.file.readline())
        time_quantum = int(self.file.readline())
        context_cost = 1
        processes = []

        # data format: AT BT P
        for number, line in enumerate(self.file.readlines(), start=1):
            line_data = []
            for x in line.split(" "):
                line_data.append(int(x))

            process = Process(number, line_data[0], line_data[1], line_data[2])
            processes.append(process)

        self.file.close()

        return [time_quantum, processes_count, context_cost, processes]


class Process:
    def __init__(self, number, arrival_time, burst_time, priority):
        self.number = number
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_burst = burst_time
        self.priority = priority
        self.quantum_counter = 0
        self.turn_around_time = 0
        self.response_time = 0
        self.waiting_time = 0
        self.completion_time = 0

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

    # Executes Process for one time unit
    def execute(self, time):
        self.remaining_burst -= 1
        self.quantum_counter += 1

        if self.response_time == 0:
            self.response_time = time - self.arrival_time

    # Resets Quantum Counter
    def reset_quantum_counter(self):
        self.quantum_counter = 0

    # Finishes Process and calculates requested data
    def finish(self, time):
        self.completion_time = time + 1
        self.turn_around_time = self.completion_time - self.arrival_time
        self.waiting_time = self.turn_around_time - self.burst_time


class Scheduler:
    def __init__(self, time_quantum):
        self.time_quantum = time_quantum
        self.running_time = 0
        self.running_process = None

    def run(self, process=None):
        if self.process_has_changed(process):
            self.running_time = self.running_time + 1

    def process_has_changed(self, process):
        pass

