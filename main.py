from collections import deque
import process


def main():
    [time_quantum, processes_count, context_shift_size, processes] = process.Reader('input.txt').read()

    # todo: use proper queue instead
    INCOME_QUEUE = processes
    # Keeps a copy of the original requests list (Will update Processes as they change)
    original_requests = list(INCOME_QUEUE)
    # Process being executed
    running_process = None
    # Ready Queue (Processes that are ready to execute)
    # todo: use proper queue instead
    READY_QUEUE = []
    # todo: use proper queue instead
    # High Priority Queue (Ready processes with same priority as Running Process)
    PRIORITY_QUEUE = deque()
    # Handles Context Shift (Will bypass Context Shift when Processor is Idle similar to Moodle example)
    context_shift_counter = 1
    # Current time
    time = 1
    # Resulting String displaying Processes over Time
    result = ""

    # Will process one time unit as long as unfinished processes exist
    while INCOME_QUEUE or READY_QUEUE or PRIORITY_QUEUE or running_process:
        # Checks if any requests have become ready
        for req in INCOME_QUEUE:
            if not (req.get_arrival_time() == time):
                continue

            if running_process and req.get_priority() == running_process.get_priority():
                PRIORITY_QUEUE.append(req)
            else:
                READY_QUEUE.append(req)

            INCOME_QUEUE.remove(req)


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

                if PRIORITY_QUEUE:
                    running_process = PRIORITY_QUEUE.popleft()
                else:
                    running_process = None

            # Swaps process if Time Quantum is reached
            elif running_process.get_quantum_counter() == time_quantum:
                running_process.reset_quantum_counter()
                context_shift_counter = 0

                if PRIORITY_QUEUE:
                    PRIORITY_QUEUE.append(running_process)
                    running_process = PRIORITY_QUEUE.popleft()

        # Handles idle processor
        else:
            result += "-"

        # Handles Ready Queue and High-Priority Queue
        if READY_QUEUE:
            # Creates a copy of the ready list and sorts it by priority (maintains queue order at original Ready list)
            sorted_ready = list(READY_QUEUE)
            sorted_ready.sort(key=lambda p: p.priority, reverse=False)

            # Assigns a process to be run if processor is idle
            # (Does not trigger Context Shift accordingly with Moodle Example)
            if not running_process:
                running_process = sorted_ready[0]
                READY_QUEUE.remove(running_process)

            # Swaps processes if there is a process with higher priority than current process, resets Context Shift
            elif sorted_ready[0].get_priority() < running_process.get_priority():
                new_priority = sorted_ready[0].get_priority()

                # Returns Running Process and High Priority Queue to Ready Queue
                # Will maintain High Priority queue order and append Running Process last
                for p in PRIORITY_QUEUE:
                    READY_QUEUE.append(PRIORITY_QUEUE.popleft())

                READY_QUEUE.append(running_process)

                # todo: if 2 or more arrives, should not remove element during iteration
                # Creates new High Priority Queue with new highest priority and assigns Running Process
                PRIORITY_QUEUE = deque()
                for p in READY_QUEUE:
                    if p.get_priority() == new_priority:
                        PRIORITY_QUEUE.append(p)
                        READY_QUEUE.remove(p)

                running_process = PRIORITY_QUEUE.popleft()
                context_shift_counter = 0

            # If there are new processes with same priority as running process, adds them to priority_queue
            elif sorted_ready[0].get_priority() == running_process.get_priority():
                for p in READY_QUEUE:
                    if p.get_priority() == running_process.get_priority():
                        PRIORITY_QUEUE.append(p)
                        READY_QUEUE.remove(p)

        time += 1

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
