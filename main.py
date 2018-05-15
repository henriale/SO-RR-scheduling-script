# Pontifícia Universidade Católica do Rio Grande do Sul
# Escola Politécnica
# Disciplina de Sistemas Operacionais
# Prof. Avelino Zorzo
# ----------------------------
# Gabriel Ferreira Kurtz (Engenharia de Software)
# gabriel.kurtz@acad.pucrs.br

# Alexandre Araujo (Ciência da Computação)
# alexandre.henrique@acad.pucrs.br

# Maio/2018
# ----------------------------
# Simulador de Escalonamento de Software

# Este programa foi desenvolvido para a disciplina de SisOp da FACIN
# (Escola Politécnica/PUCRS). Trata-se de um um script para simular
# uma fila no modelo Round Robin com prioridades fixas.

# O programa lê um imput de dados representando processos e deve
# simular seu processo de CPU e I/O, imprimindo ao final uma String
# que demonstre os processos ao longo do tempo, bem como os dados de
# Tempo de Resposta e Tempo de Espera médios.


from collections import deque
import process as proc


class Scheduler:
    def __init__(self, processes, timeslice=2, context_shift_size=1):
        self.timeslice = timeslice
        self.context_shift_size = context_shift_size
        self.processes = processes
        self.processes_count = len(self.processes)

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
        # IO Queue: Handles processes that are currently in IO
        self.IO_QUEUE = []
        # Handles Context Shift (Will bypass Context Shift when Processor is Idle similar to Moodle example)
        self.context_shift_counter = 1
        # Current time
        self.time = 1
        # Resulting String displaying Processes over Time
        self.log = ""

    def clock(self):
        self.time = self.time + 1

    def has_process_to_run(self):
        return self.INCOME_QUEUE or self.READY_QUEUE or self.PRIORITY_QUEUE or self.running_process or self.IO_QUEUE

    def run(self):
        # Checks if any requests have become ready
        arrivals = self.get_new_arrivals()
        if arrivals:
            self.enqueue_processes(arrivals)

        # Checks if Context Shift is occurring
        if self.should_switch_context():
            self.switch_context()
            return

        if self.should_run_process():
            self.run_process()
            
        else:
            self.write_log("-")


        if(self.running_process):
            if self.running_process.start_io():
                self.enqueue_io()         

        if (self.IO_QUEUE):
            for p in self.IO_QUEUE:
                p.run_io()
            IO_COPY = list(self.IO_QUEUE)
            for p in IO_COPY:
                if p.get_io_counter() == 0:
                    self.IO_QUEUE.remove(p)
                    arrivals.append(p)
            if(arrivals):
                for p in arrivals:
                    if(self.should_run_process()):
                        if p.get_priority() == self.running_process.get_priority():
                            self.PRIORITY_QUEUE.appendleft(p)
                        else:
                            self.READY_QUEUE.append(p)
                    else:
                        self.READY_QUEUE.append(p)


        # Handles Ready Queue and High-Priority Queue
        if self.READY_QUEUE:
            # Creates a copy of the ready list and sorts it by priority (maintains queue order at original Ready list)
            sorted_ready = list(self.READY_QUEUE)
            sorted_ready.sort(key=lambda p: p.priority, reverse=False)

            # Assigns a process to be run if processor is idle
            # (Does not trigger Context Shift accordingly with Moodle Example)
            if not self.running_process:
                if(self.PRIORITY_QUEUE):
                    self.running_process = self.PRIORITY_QUEUE.popleft()

                elif(sorted_ready):
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

        self.clock()

    def report(self):
        average_response_time, average_turn_around_time, average_waiting_time = self.calc_averages()
        self.print_all_processes()
        self.print_execution_log()

        self.print_time_averages(average_response_time, average_turn_around_time, average_waiting_time)

    def print_time_averages(self, average_response_time, average_turn_around_time, average_waiting_time):
        print("Average Response Time: " + str(average_response_time))
        print("Average Waiting Time: " + str(average_waiting_time))
        print("Average Turn Around Time: " + str(average_turn_around_time))

    def calc_averages(self):
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

        return average_response_time, average_turn_around_time, average_waiting_time

    def print_all_processes(self):
        print("  P   AT   BT   Pri  CT  TAT   WT   RT   IO")
        for p in self.original_requests:
            print("%3d  %3d  %3d  %3d  %3d  %3d  %3d  %3d  %3s" % (
                p.get_number(), p.get_arrival_time(), p.get_burst_time(), p.get_priority(), p.get_completion_time(),
                p.get_turn_around_time(), p.get_waiting_time(), p.get_response_time(), str(p.get_io_times())))

    def print_execution_log(self):
        print("\nProcessor Log:\n" + self.log)

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

    def enqueue_io(self):
        self.IO_QUEUE.append(self.running_process)
        if(self.PRIORITY_QUEUE):
            self.running_process = self.PRIORITY_QUEUE.popleft()
        else:
            self.running_process = None
        self.context_shift_counter = 0

    def switch_context(self):
        self.write_log("C")
        self.context_shift_counter += 1
        self.clock()

    def write_log(self, message):
        self.log += str(message)

    def should_run_process(self):
        return bool(self.running_process)

    def timeslice_has_ended(self):
        return self.running_process.get_quantum_counter() == self.timeslice


if __name__ == "__main__":
    scheduler = proc.Reader("input.txt").read_scheduler()

    while scheduler.has_process_to_run():
        scheduler.run()

    scheduler.report()