from classes.memory import Memory
from classes.process import Process


class Hardware:

    def __init__(self, quantum: int):
        self.time = 0
        self.cpus = [None] * 4
        self.disks: int = 4
        self.memory = Memory(16000)
        self.quantum = quantum
        self.realtimeQueue = []
        self.feedbackQueue = [[], [], []]

    def add_process(self, process: Process) -> bool:
        if process is None:
            return True
        if not self.memory.add_image(process):
            print("Error: Memory is full")
            return False
        if process.priority == 0:
            self.realtimeQueue.append(process)
        else:
            self.feedbackQueue[0].append(process)
        return True

    def remove_process(self, process):
        self.memory.remove_image(process)

    def clock(self):
        self.time += 1

# Atualizar a CPU com os processos, também reduzindo deles o tempo de execução.
# Caso um processo seja executado é retirado os discos necessários do hardware e também a quantidade de memória que
# está sendo utilizada por cada processo. Ao fim deles eles valores são readicionados.
    def update_cpu(self):
        executed = [[], [], []]
        for i in range(len(self.cpus)):
            self.fill_cpu(i)
            if self.cpus[i] is not None:
                if self.cpus[i].has_ended():
                    print("Process", self.cpus[i].PID, " has ended")
                    self.remove_process(self.cpus[i])
                    self.disks += self.cpus[i].ioNeeded
                    self.cpus[i] = None
                elif self.cpus[i].priority != 0 and self.cpus[i].has_reached_cpu_time():
                    print("Process", self.cpus[i].PID, " has achieved quantum")
                    queue = (self.cpus[i].previous_queue + 1) % len(self.feedbackQueue)
                    executed[queue].append(self.cpus[i])
                    self.disks += self.cpus[i].ioNeeded
                    self.cpus[i] = None

        for i in range(len(self.cpus)):
            self.fill_cpu(i)

        for i in range(len(executed[0])):
            self.feedbackQueue[0].append(executed[0][i])
        for i in range(len(executed[1])):
            self.feedbackQueue[1].append(executed[1][i])
        for i in range(len(executed[2])):
            self.feedbackQueue[2].append(executed[2][i])

# Processo adicionado para a CPU, return -> True
    def fill_cpu(self, index) -> bool:
        if self.cpus[index] is None:
            self.cpus[index] = self.dispatcher()
            if self.cpus[index] is not None:
                self.cpus[index].join_cpu(self.quantum)
                self.disks -= self.cpus[index].ioNeeded
                return True
        return False

# Dispachante busca um processo primeiramente da lista de processos de maior priodade e caso negativo
# tenta buscar por um processo na lista de prioridade normal.
    def dispatcher(self) -> Process or None:
        process = self.get_process_realtime()
        if process is None:
            process = self.get_process_feedback()
        return process

    def get_process_realtime(self) -> Process or None:
        process = None
        for p in self.realtimeQueue:
            if p.has_needed_io(self.disks): # verifica ser existe memória suficiente para a execução do processo
                process = p
                break
            else:
                print("discos indisponiveis", self.disks, p.ioNeeded)

        if process is not None:  # retira o processo da fila de maior prioridade para ser executado
            self.realtimeQueue.remove(process)
            return process
        return process

    def get_process_feedback(self) -> Process or None:
        process = None
        for i in range(len(self.feedbackQueue)):
            for p in self.feedbackQueue[i]:
                if p.has_needed_io(self.disks): # verifica ser existe memória suficiente para a execução do processo
                    process = p
                    break

            if process is not None: # retira o processo da fila de prioridade normal para ser executado
                self.feedbackQueue[i].remove(process)
                process.previous_queue = i
                return process
        return process

    def print_state(self):
        print("--------------------")

        print("TIME =", self.time)

        print("CPU STATE")
        print(list(map(lambda p: None if p is None else str(p.PID) + " - " + str(p.quantum), list(self.cpus))))

        print("\nREALTIME QUEUE")
        print(list(map(lambda p: p.PID, list(self.realtimeQueue))))

        print("\nFEEDBACK QUEUE")
        for queue in self.feedbackQueue:
            print(list(map(lambda p: p.PID, list(queue))))

        print("--------------------")

