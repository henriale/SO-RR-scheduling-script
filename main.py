from collections import deque
import process as proc


class Scheduler:
    def __init__(self):
        self.INCOME_QUEUE = []
        self.READY_QUEUE = []
        self.PRIORITY_QUEUE = deque()
        self.time = 1

        # start
        [self.time_quantum, self.processes_count, self.context_shift_size, self.processes] = proc.Reader(
            'input.txt').read()

        # todo: use proper queue instead
        self.INCOME_QUEUE = self.processes
        # Keeps a copy of the original requests list (Will update Processes as they change)
        self.original_requests = list(self.INCOME_QUEUE)
        # Process being executed
        self.running_process = None
        # Ready Queue (Processes that are ready to execute)
        # todo: use proper queue instead
        self.READY_QUEUE = []
        # todo: use proper queue instead
        # High Priority Queue (Ready processes with same priority as Running Process)
        self.PRIORITY_QUEUE = deque()
        # Handles Context Shift (Will bypass Context Shift when Processor is Idle similar to Moodle example)
        self.context_shift_counter = 1
        # Current time
        self.time = 1
        # Resulting String displaying Processes over Time
        self.log = ""

    def clock(self):
        self.time = self.time + 1

    def has_process_to_run(self):
        return self.INCOME_QUEUE or self.READY_QUEUE or self.PRIORITY_QUEUE or self.running_process

    def run(self):
        # Checks if any requests have become ready
        arrivals = self.get_new_arrivals()
        if arrivals:
            self.enqueue_processes(arrivals)

        # Checks if Context Shift is occurring
        if self.should_switch_context():
            self.switch_context()
            return

        # Handles Running Process
        if self.has_process_to_run2():
            self.run_process()
        else:
            self.write_log("-")

        # Handles Ready Queue and High-Priority Queue
        if self.READY_QUEUE:
            # Creates a copy of the ready list and sorts it by priority (maintains queue order at original Ready list)
            sorted_ready = list(self.READY_QUEUE)
            sorted_ready.sort(key=lambda p: p.priority, reverse=False)

            # Assigns a process to be run if processor is idle
            # (Does not trigger Context Shift accordingly with Moodle Example)
            if not self.running_process:
                self.running_process = sorted_ready[0]
                self.remove_ready_process(self.running_process)

            # Swaps processes if there is a process with higher priority than current process, resets Context Shift
            elif sorted_ready[0].get_priority() < self.running_process.get_priority():
                new_priority = sorted_ready[0].get_priority()

                # Returns Running Process and High Priority Queue to Ready Queue
                # Will maintain High Priority queue order and append Running Process last
                self.enqueue_ready_process(self.running_process)
                while self.PRIORITY_QUEUE:
                    self.enqueue_ready_process(self.PRIORITY_QUEUE.popleft())

                # Creates new High Priority Queue with new highest priority and assigns Running Process
                self.PRIORITY_QUEUE = deque()
                READY_COPY = list(self.READY_QUEUE)
                for p in READY_COPY:
                    if p.get_priority() == new_priority:
                        self.enqueue_priority_process(p)
                        self.remove_ready_process(p)

                self.running_process = self.PRIORITY_QUEUE.popleft()
                self.context_shift_counter = 0

            # If there are new processes with same priority as running process, adds them to priority_queue
            elif sorted_ready[0].get_priority() == self.running_process.get_priority():
                READY_COPY = list(self.READY_QUEUE)
                for p in READY_COPY:
                    if p.get_priority() == self.running_process.get_priority():
                        self.enqueue_priority_process(p)
                        self.remove_ready_process(p)

        print("  P   AT   BT   Pri   IO  CT  TAT   WT   RT ")
        for p in self.original_requests:
            print("%3d  %3d  %3d  %3d  %3d  %3d  %3d  %3d  %3d" % (
                p.get_number(), p.get_arrival_time(), p.get_burst_time(), p.get_priority(), p.get_io_time(),
                p.get_completion_time(), p.get_turn_around_time(), p.get_waiting_time(), p.get_response_time()))

        print("\nProcessor Log:\n" + self.log)

        # Calculating required averages
        n = 0
        total_response_time = 0
        total_waiting_time = 0
        total_turn_around_time = 0

        for p in self.original_requests:
            total_response_time += p.get_response_time()
            total_waiting_time += p.get_waiting_time()
            total_turn_around_time += p.get_turn_around_time()
            n += 1

        average_response_time = total_response_time / n
        average_waiting_time = total_waiting_time / n
        average_turn_around_time = total_turn_around_time / n

        print("\nAverage Response Time: " + str(average_response_time)
              + "\nAverage Waiting Time: " + str(average_waiting_time)
              + "\nAverage Turn Around Time: " + str(average_turn_around_time))

    def run_process(self):
        self.running_process.execute(self.time)
        self.write_log(self.running_process.get_number())

        # Finishes process if it is done
        if self.running_process.is_done():
            self.running_process.finish(self.time)
            self.context_shift_counter = 0

            if self.PRIORITY_QUEUE:
                self.running_process = self.PRIORITY_QUEUE.popleft()
            else:
                self.running_process = None

            return

        # Swaps process if Time Quantum is reached
        if self.timeslice_has_ended():
            self.running_process.reset_quantum_counter()
            self.context_shift_counter = 0

            if self.PRIORITY_QUEUE:
                self.enqueue_priority_process(self.running_process)
                self.running_process = self.PRIORITY_QUEUE.popleft()

    def remove_ready_process(self, p):
        self.READY_QUEUE.remove(p)

    def should_switch_context(self):
        return self.context_shift_counter < self.context_shift_size

    def has_new_arrivals(self):
        for req in self.INCOME_QUEUE:
            if not (req.get_arrival_time() == self.time):
                return True
        return False

    def get_new_arrivals(self):
        arrivals = []

        COPY_INCOME_QUEUE = list(self.INCOME_QUEUE)
        for process in COPY_INCOME_QUEUE:
            if not (process.get_arrival_time() == self.time):
                continue

            self.INCOME_QUEUE.remove(process)
            arrivals.append(process)

        return arrivals

    def enqueue_processes(self, arrivals):
        for process in arrivals:
            if self.running_process and process.get_priority() == self.running_process.get_priority():
                self.enqueue_priority_process(process)
            else:
                self.enqueue_ready_process(process)

    def enqueue_ready_process(self, process):
        self.READY_QUEUE.append(process)

    def enqueue_priority_process(self, process):
        self.PRIORITY_QUEUE.append(process)

    def switch_context(self):
        self.write_log("C")
        self.context_shift_counter += 1
        self.clock()

    def write_log(self, message):
        self.log += str(message)

    def has_process_to_run2(self):
        return bool(self.running_process)

    def timeslice_has_ended(self):
        return self.running_process.get_quantum_counter() == self.time_quantum


if __name__ == "__main__":
    scheduler = Scheduler()

    while scheduler.has_process_to_run():
        scheduler.run()
        scheduler.clock()
