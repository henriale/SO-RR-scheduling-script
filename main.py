from time import sleep
from collections import deque
import process

# Toggles if Data File will be printed before running algorithm
_PRINT_DATA_FIRST_ = True


def main():
    print('''
-------------------------------------------------------------
-------------------------------------------------------------
--- Pontificia Universidade Catolica do Rio Grande do Sul ---
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

    [time_quantum, processes_count, context_shift_size, processes] = process.Reader('input.txt').read()

    # Context Shift Size
    context_shift_size = 1

    if (_PRINT_DATA_FIRST_):
        print("Time Quantum: %d" % time_quantum)
        print("Context shift: %d" % context_shift_size)
        print("  P   AT   BT   Pri ")

    requests = processes
    for p in processes:
        print("%d  %2d  %2d  %d" % (p.get_number(), p.get_arrival_time(), p.get_burst_time(), p.get_priority()))
        # requests.append(p)

    # Keeps a copy of the original requests list (Will update Processes as they change)
    original_requests = list(requests)
    # Process being executed
    running_process = None
    # Ready Queue (Processes that are ready to execute)
    ready = []
    # High Priority Queue (Ready processes with same priority as Running Process)
    priority_queue = deque()
    # Handles Context Shift (Will bypass Context Shift when Processor is Idle similar to Moodle example)
    context_shift_counter = 1
    # Current time
    time = 1
    # Resulting String displaying Processes over Time
    result = ""

    print("\n--- Starting Processes ---")

    # Will process one time unit as long as unfinished processes exist
    # while(time<35):
    while requests or ready or priority_queue or running_process:
        # Checks if any requests have become ready
        set_remove = []
        for req in requests:
            if req.get_arrival_time() == time:

                if running_process:
                    # Adds new process to High Priority queue if it has same priority as current process
                    if req.get_priority() == running_process.get_priority():
                        priority_queue.append(req)
                        set_remove.append(req)
                    # Appends new process to Ready Queue if it has higher or lower priority (will be handled later)
                    else:
                        ready.append(req)
                        set_remove.append(req)
                # Appends new process to Ready Queue if there is no Running Process (will be handled later)
                else:
                    ready.append(req)
                    set_remove.append(req)

        while set_remove:
            requests.remove(set_remove.pop())

        # Checks if Context Shift is occurring
        if context_shift_counter < context_shift_size:
            result += "C"
            context_shift_counter += 1
            time += 1
            continue

        # Handles Running Process
        if running_process:
            running_process.execute(time)
            result += str(running_process.get_number())

            # Finishes process if it is done
            if running_process.get_remaining_burst() == 0:
                running_process.finish(time)
                context_shift_counter = 0

                if priority_queue:
                    running_process = priority_queue.popleft()
                else:
                    running_process = None

            # Swaps process if Time Quantum is reached
            elif running_process.get_quantum_counter() == time_quantum:
                running_process.reset_quantum_counter()
                context_shift_counter = 0

                if priority_queue:
                    priority_queue.append(running_process)
                    running_process = priority_queue.popleft()

        # Handles idle processor
        else:
            result += "-"

        # Handles Ready Queue and High-Priority Queue
        if ready:
            # Creates a copy of the ready list and sorts it by priority (maintains queue order at original Ready list)
            sorted_ready = list(ready)
            sorted_ready.sort(key=lambda p: p.priority, reverse=False)

            # Assigns a process to be run if processor is idle
            # (Does not trigger Context Shift accordingly with Moodle Example)
            if not running_process:
                running_process = sorted_ready[0]
                ready.remove(running_process)

            # Swaps processes if there is a process with higher priority than current process, resets Context Shift
            elif sorted_ready[0].get_priority() < running_process.get_priority():
                new_priority = sorted_ready[0].get_priority()

                # Returns Running Process and High Priority Queue to Ready Queue
                # Will maintain High Priority queue order and append Running Process last
                for p in priority_queue:
                    ready.append(priority_queue.popleft())

                ready.append(running_process)

                # todo: if 2 or more arrives, should not remove element during iteration
                # Creates new High Priority Queue with new highest priority and assigns Running Process
                priority_queue = deque()
                for p in ready:
                    if p.get_priority() == new_priority:
                        priority_queue.append(p)
                        ready.remove(p)

                running_process = priority_queue.popleft()
                context_shift_counter = 0

            # If there are new processes with same priority as running process, adds them to priority_queue
            elif sorted_ready[0].get_priority() == running_process.get_priority():
                for p in ready:
                    if p.get_priority() == running_process.get_priority():
                        priority_queue.append(p)
                        ready.remove(p)

        time += 1

    print("--- Finishing Processes ---")
    print("  P   AT   BT   Pri  CT  TAT   WT   RT ")

    for p in original_requests:
        print("%3d  %3d  %3d  %3d  %3d  %3d  %3d  %3d" % (
            p.get_number(), p.get_arrival_time(), p.get_burst_time(), p.get_priority(),
            p.get_completion_time(), p.get_turn_around_time(), p.get_waiting_time(), p.get_response_time()))

    print("\nProcessor Log:\n" + result)

    # Calculating required averages
    n = 0
    total_response_time = 0
    total_waiting_time = 0
    total_turn_around_time = 0

    for p in original_requests:
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
    main()
