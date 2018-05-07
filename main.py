from time import sleep
from collections import deque

# Toggles if Data File will be printed before running algorithm
_PRINT_DATA_FIRST_ = True

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

	# Reading input file and generating data structure
	file = open("input.txt")
	print("--- Importing Data ---")
	# Total Processes
	processes_count = int(file.readline())
	# Time Quantum Size
	time_quantum = int(file.readline())
	# Context Shift Size
	context_shift_size = 1
	# Holds every Process request read from File
	requests = read_processes(file)
	file.close()


	if(_PRINT_DATA_FIRST_):
		print("Time Quantum: %d" % time_quantum)
		print("Context shift: %d" % context_shift_size)
		print("  P   AT   BT   Pri ")
	
		for p in requests:
			print("%3d  %3d  %3d  %3d" % (p.get_number(), p.get_arrival_time(), p.get_burst_time(), p.get_priority()))


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
	while(requests or ready or priority_queue or running_process):
		
		#print("Request: " + str(requests[0].get_number()))

		#print("\nStarting Loop - CS: " + str(context_shift_counter) + " Time: " + str(time))
		
		#print(str(requests) + "\n" + str(ready) + "\n" + str(priority_queue) + "\n" + str(running_process))

		
		# Checks if any requests have become ready
		set_remove = []
		for req in requests:
			print(str(req.get_number()) + " - Time: " + str(req.get_arrival_time()))
			if(req.get_arrival_time() == time):
				
				if(running_process):
					# Adds new process to High Priority queue if it has same priority as current process
					if(req.get_priority() == running_process.get_priority()):
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

		while(set_remove):
			aux = set_remove.pop()
			requests.remove(aux)

		# Checks if Context Shift is occurring
		if(context_shift_counter < context_shift_size):
			result += "C"
			context_shift_counter += 1
			time += 1
			continue

		# Handles Running Process
		if(running_process):
			running_process.execute(time)
			result += str(running_process.get_number())

			# Finishes process if it is done
			if(running_process.get_remaining_burst() == 0):
				running_process.finish(time)
				context_shift_counter = 0
			
				if(priority_queue):
					running_process = priority_queue.popleft()
				else:
					running_process = None
			
			# Swaps process if Time Quantum is reached
			elif(running_process.get_quantum_counter() == time_quantum):
				running_process.reset_quantum_counter()
				context_shift_counter = 0
			
				if(priority_queue):
					priority_queue.append(running_process)
					running_process = priority_queue.popleft()

		# Handles idle processor
		else:
			result += "-"

		# Handles Ready Queue and High-Priority Queue
		if(ready):
			# Creates a copy of the ready list and sorts it by priority (maintains queue order at original Ready list)
			sorted_ready = list(ready)
			sorted_ready.sort(key=lambda p: p.priority, reverse=False)
			
			# Assigns a process to be run if processor is idle (Does not trigger Context Shift accordingly with Moodle Example)
			if(not(running_process)):
				running_process = sorted_ready[0]
				ready.remove(running_process)
				context_shift_counter == 1
			
			# Swaps processes if there is a process with higher priority than current process, resets Context Shift
			elif(sorted_ready[0].get_priority() < running_process.get_priority()):
				new_priority = sorted_ready[0].get_priority()
				
				# Returns Running Process and High Priority Queue to Ready Queue
				# Will maintain High Priority queue order and append Running Process last
				for p in priority_queue:
					ready.append(priority_queue.popleft())
				ready.append(running_process)
				
				# Creates new High Priority Queue with new highest priority and assigns Running Process
				priority_queue = deque()
				for p in ready:
					if(p.get_priority() == new_priority):
						priority_queue.append(p)
						ready.remove(p)

				running_process = priority_queue.popleft()
				context_shift_counter = 0

			# If there are new processes with same priority as running process, adds them to priority_queue
			elif(sorted_ready[0].get_priority() == running_process.get_priority()):
				for p in ready:
					if(p.get_priority() == running_process.get_priority()):
						priority_queue.append(p)
						ready.remove(p)
						

#		for p in ready:
#			print("CS: " + str(context_shift_counter) + " Time: " + str(time) + " Ready: " + str(p.get_number()))

#		for p in priority_queue:
#			print(str(time) + " Queue: " + str(p.get_number()))

		time += 1
	print("--- Finishing Processes ---")

	print("  P   AT   BT   Pri  CT  TAT   WT   RT ")
	
	for p in original_requests:
		print("%3d  %3d  %3d  %3d  %3d  %3d  %3d  %3d" % (p.get_number(), p.get_arrival_time(), p.get_burst_time(), p.get_priority(),
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
		 +"\nAverage Waiting Time: " + str(average_waiting_time)
		 +"\nAverage Turn Around Time: " + str(average_turn_around_time))

class Process:
	def __init__(self, PN, AT, BT, P):
		# Process Number
		self.number = PN
		# Arrival Time
		self.arrival_time = AT
		# Burst Time
		self.burst_time = BT
		# Burst Time remaining until process finishes
		self.remaining_burst = BT
		# Priority
		self.priority = P
		# Number of Time Quantum fractions used by process (changes Context and resets at 3)
		self.quantum_counter = 0
		# Turn Around time
		self.turn_around_time = 0
		# Response Time
		self.response_time = 0
		# Waiting Time
		self.waiting_time = 0
		# Completion time
		self.completion_time = 0
		
		
	# Getters			
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
		if(self.response_time == 0):
			self.response_time = time - self.arrival_time
	
	# Resets Quantum Counter
	def reset_quantum_counter(self):
		self.quantum_counter = 0

	# Finishes Process and calculates requested data
	def finish(self, time):
		self.completion_time = time + 1
		self.turn_around_time = self.completion_time - self.arrival_time
		self.waiting_time = self.turn_around_time - self.burst_time


		

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


if __name__ == "__main__":
	main()