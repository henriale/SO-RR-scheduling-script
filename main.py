from time import sleep

def main():
	print(
		'''
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

	file = open("input.txt")

	
	# Reading input file and generating data structure
	file = open("input.txt")
	processes_count = int(file.readline())
	TQ = int(file.readline())
	C = 1
	
	processes = read_processes(file)
	queue = []
	file.close()

	print("Time Quantum (TQ): %d" % TQ)
	print("Context shift (C): %d" % C)
	print("P  AT  BT  Priority")
	
	for p in processes:
		print("%d  %2d  %2d  %d" % (p.get_number(), p.get_arrival_time(), p.get_burst_time(), p.get_priority()))

	T = 1
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