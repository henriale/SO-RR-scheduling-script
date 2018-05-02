from time import sleep


def no_process_to_run():
    return True


file = open("input.txt")

processes_count = int(file.readline())
TQ = int(file.readline())
C = 1
processes = []
queue = []

# data format: AT BT P
[processes.append([int(x) for x in line.split(" ")]) for line in file.readlines()]

print("Time Quantum (TQ): %d" % TQ)
print("Context shift (C): %d" % C)
print("P  AT  BT  Priority")
[print("%d  %2d  %2d  %d" % (pn, p[0], p[1], p[2])) for pn, p in enumerate(processes, start=1)]

T = 0
while True:
    sleep(1.5)
    print("Time: %d" % T)

    # 1. verify if process start
    for process in processes:
        if process[0] == T:
            # todo: sort by priority after appending
            queue.append(process)

    T = T + 1
    # 2. verify if has process to run
    if no_process_to_run():
        continue

    # 3. account context switching
    T = T + 1
    # 4. take from queue the process with highest priority to run
