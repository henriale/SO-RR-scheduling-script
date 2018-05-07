from collections import deque


def main():
    print(
        '''
-------------------------------------------------------------
-------------------------------------------------------------
--- Pontifícia Universidade Católica do Rio Grande do Sul ---
--- Escola Politécnica ---
--- Disciplina de Sistemas Operacionais ---
--- Prof. Avelino Zorzo ---
-----------------------------------------------
--- ALGORITMO DE ESCALONAMENTO DE PROCESSOS ---
-----------------------------------------------
--- Alexandre Araujo (Ciência da Computação) ---
--- Gabriel F. Kurtz (Engenharia de Software) ---
-------------------------------------------------
-------------------------------------------------

        ''')

    # Reading input file and generating data structure
    file = open("input.txt")
    processes_count = int(file.readline())
    TQ = int(file.readline())
    C = 1

    processes = read_processes(file)
    file.close()

    print("Time Quantum (TQ): %d" % TQ)
    print("Context shift (C): %d" % C)
    print("P  AT  BT  Priority")

    requests = []
    for p in processes:
        print("%d  %2d  %2d  %d" % (p.get_number(), p.get_arrival_time(), p.get_burst_time(), p.get_priority()))
        requests.append(p)

    ready = []
    queue = deque()
    running_process = None
    context_counter = 5

    time = 1
    while time < 35:
        # Checks if Context Shift is occurring
        if context_counter == 0:
            print("C", end='')
            context_counter += 1
            time += 1
            continue

        context_counter += 1

        if running_process:
            print(running_process.get_number(), end='')
        else:
            print("-", end='')

        # Checks if any requests have become ready
        for req in requests:
            if req.get_arrival_time() == time:
                requests.remove(req)
                ready.append(req)

        if ready:
            # Creates a copy of the ready list and sorts it by priority (maintains queue order at original Ready list)
            sorted_ready = list(ready)
            sorted_ready.sort(key=lambda p: p.priority, reverse=False)

            # Assigns a process to be run if processor is idle
            if not running_process:
                running_process = sorted_ready[0]
                ready.remove(running_process)
                # why is this checking without any action???
                context_counter == 1

            # Swaps processes if there is a process with higher priority than current process
            elif sorted_ready[0].get_priority() < running_process.get_priority():
                new_priority = sorted_ready[0].get_priority()

                ready.append(running_process)
                for p in queue:
                    ready.append(queue.popleft())

                queue = deque()
                for p in ready:
                    if p.get_priority() == new_priority:
                        queue.append(p)
                        ready.remove(p)

                running_process = queue.popleft()
                context_counter = 0

            # If there are new processes with same priority as running process, adds them to queue
            elif sorted_ready[0].get_priority() == running_process.get_priority():
                for p in ready:
                    if p.get_priority() == running_process.get_priority():
                        queue.append(p)
                        ready.remove(p)

        if context_counter == 4:
            context_counter = 0

            if queue:
                queue.append(running_process)
                running_process = queue.popleft()

        #       for p in ready:
        #           print("CC: " + str(context_counter) + " Time: " + str(time) + " Ready: " + str(p.get_number()))

        #       for p in queue:
        #           print(str(time) + " Queue: " + str(p.get_number()))

        time += 1


class Process:
    def __init__(self, PN, AT, BT, P):
        # Process Number
        self.number = PN
        # Arrival Time
        self.arrival_time = AT
        # Burst Time
        self.burst_time = BT
        # Priority
        self.priority = P
        # Answer Time
        self.answer_time = 0
        # Waiting Time
        self.waiting_time = 0

    def get_number(self):
        return self.number

    def get_arrival_time(self):
        return self.arrival_time

    def get_burst_time(self):
        return self.burst_time

    def get_priority(self):
        return self.priority


# Reads processes from file and returns them in a list of objects
def read_processes(file):
    count = 1
    processes = []

    # data format: AT BT P
    for line in file.readlines():

        line_data = []
        for x in line.split(" "):
            line_data.append(int(x))

        process = Process(count, line_data[0], line_data[1], line_data[2])
        processes.append(process)

        count += 1

    return processes


def no_process_to_run():
    return True

if __name__ == "__main__":
    main()
