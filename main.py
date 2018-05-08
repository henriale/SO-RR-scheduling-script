from collections import deque
import process


class Scheduler:
    def __init__(self):
        self.INCOME_QUEUE = []
        self.READY_QUEUE = []
        self.PRIORITY_QUEUE = deque()
        self.time = 1

        # start
        [self.time_quantum, self.processes_count, self.context_shift_size, self.processes] = process.Reader('input.txt').read()

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
        self.result = ""

    def clock(self):
        self.time = self.time + 1

    def run(self):
        # Will process one time unit as long as unfinished processes exist
        while self.INCOME_QUEUE or self.READY_QUEUE or self.PRIORITY_QUEUE or self.running_process:
            # Checks if any requests have become ready
            for req in self.INCOME_QUEUE:
                if not (req.get_arrival_time() == self.time):
                    continue

                if self.running_process and req.get_priority() == self.running_process.get_priority():
                    self.PRIORITY_QUEUE.append(req)
                else:
                    self.READY_QUEUE.append(req)

                self.INCOME_QUEUE.remove(req)

            # Checks if Context Shift is occurring
            if self.context_shift_counter < self.context_shift_size:
                self.result += "C"
                self.context_shift_counter += 1
                self.time += 1
                continue

            # Handles Running Process
            if self.running_process:
                self.running_process.execute(self.time)
                self.result += str(self.running_process.get_number())

                # Finishes process if it is done
                if self.running_process.get_remaining_burst() == 0:
                    self.running_process.finish(self.time)
                    self.context_shift_counter = 0

                    if self.PRIORITY_QUEUE:
                        self.running_process = self.PRIORITY_QUEUE.popleft()
                    else:
                        self.running_process = None

                # Swaps process if Time Quantum is reached
                elif self.running_process.get_quantum_counter() == self.time_quantum:
                    self.running_process.reset_quantum_counter()
                    self.context_shift_counter = 0

                    if self.PRIORITY_QUEUE:
                        self.PRIORITY_QUEUE.append(self.running_process)
                        self.running_process = self.PRIORITY_QUEUE.popleft()

            # Handles idle processor
            else:
                self.result += "-"

            # Handles Ready Queue and High-Priority Queue
            if self.READY_QUEUE:
                # Creates a copy of the ready list and sorts it by priority (maintains queue order at original Ready list)
                sorted_ready = list(self.READY_QUEUE)
                sorted_ready.sort(key=lambda p: p.priority, reverse=False)

                # Assigns a process to be run if processor is idle
                # (Does not trigger Context Shift accordingly with Moodle Example)
                if not self.running_process:
                    self.running_process = sorted_ready[0]
                    self.READY_QUEUE.remove(self.running_process)

                # Swaps processes if there is a process with higher priority than current process, resets Context Shift
                elif sorted_ready[0].get_priority() < self.running_process.get_priority():
                    new_priority = sorted_ready[0].get_priority()

                    # Returns Running Process and High Priority Queue to Ready Queue
                    # Will maintain High Priority queue order and append Running Process last
                    for p in self.PRIORITY_QUEUE:
                        self.READY_QUEUE.append(self.PRIORITY_QUEUE.popleft())

                    self.READY_QUEUE.append(self.running_process)

                    # todo: if 2 or more arrives, should not remove element during iteration
                    # Creates new High Priority Queue with new highest priority and assigns Running Process
                    self.PRIORITY_QUEUE = deque()
                    for p in self.READY_QUEUE:
                        if p.get_priority() == new_priority:
                            self.PRIORITY_QUEUE.append(p)
                            self.READY_QUEUE.remove(p)

                    self.running_process = self.PRIORITY_QUEUE.popleft()
                    self.context_shift_counter = 0

                # If there are new processes with same priority as running process, adds them to priority_queue
                elif sorted_ready[0].get_priority() == self.running_process.get_priority():
                    for p in self.READY_QUEUE:
                        if p.get_priority() == self.running_process.get_priority():
                            self.PRIORITY_QUEUE.append(p)
                            self.READY_QUEUE.remove(p)

            self.time += 1

        print("  P   AT   BT   Pri  CT  TAT   WT   RT ")
        for p in self.original_requests:
            print("%3d  %3d  %3d  %3d  %3d  %3d  %3d  %3d" % (
                p.get_number(), p.get_arrival_time(), p.get_burst_time(), p.get_priority(),
                p.get_completion_time(), p.get_turn_around_time(), p.get_waiting_time(), p.get_response_time()))

        print("\nProcessor Log:\n" + self.result)

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


if __name__ == "__main__":
    Scheduler().run()
