class Process:
    def __init__(self, name, arrivaltime, CPUburst, IOburst, Q1timeallot, Q2timeallot, level):
        self.name = name
        self.arrivaltime = arrivaltime
        self.CPUburst = CPUburst
        self.IOburst = IOburst
        self.Q1timeallot = Q1timeallot
        self.Q2timeallot = Q2timeallot
        self.level = level
        
def MLFQ(procList, contextSwitch):
    # Global time
    time = 0
    
    # List of Queue levels
    Q1list = []
    Q2list = []
    Q3list = []
    
    # List of processes currently in CPU or IO
    CPU = ""
    IOlist = []
    standby = []
    
    contextSwitching = False
    quantum = 4
    while(len(procList) > 0):
        # Enqueue incoming processes
        Q1list = enqueueIncoming(procList, time, Q1list)
        
        # CPU
        if(contextSwitching and contextSwitch > 0): 
            pass
        else:
            # Q1 (Top Priority Queue): Round Robin Scheduling - 4 ms quantum
            if(len(Q1list) > 0 and quantum > 0):
                CPU = Q1list[0].name
                Q1list[0].CPUburst[0] -= 1
                Q1list[0].Q1timeallot -= 1
                quantum -= 1
                
                if(Q1list[0].CPUburst[0] == 0):
                    currProc = Q1list.pop(0)
                    currProc.CPUburst.pop(0)         # remove 0 CPU burst time
                    if(currProc.Q1timeallot > 0):
                        currProc.Q1timeallot = 8     # renew Q1 time allotment
                        currProc.level = "Q1"
                    else:
                        currProc.level = "Q2"        # change level to Q2
                        
                    IOlist = addIO(IOlist, currProc) # add current process if there are still IOburst
                    standby.append(currProc)         # add in standby list while in IO
                    quantum = 4
                    contextSwitching = True
                
                if(quantum == 0):
                    currProc = Q1list.pop(0)
                    if(currProc.Q1timeallot > 0):
                        Q1list.append(currProc)      # stay in queue (dequeue then enqueue)
                    else:
                        Q2list.append(currProc)      # move process to lower queue
                    
                    quantum = 4
                    contextSwitching = True
                    
            # Q2 (Medium Priority Queue): First-come First Served Scheduling
            elif(len(Q2list) > 0):
                # currProc = Q2list[0]
                # do something
                pass
            
            # Q3 (Least Priority Queue): Shortest Job First
            else:
                # currProc = Q3list[0]
                # do something
                pass
        
        # I/O 
        for proc in IOlist:
            proc.IOburst[0] -= 1
            if(proc.IOburst[0] == 0):
                proc.IOburst.pop(0)                   # remove the 0 IO burst
                if(proc.level == "Q1"):
                    Q1list.append(proc)
                elif(proc.level == "Q2"):
                    Q2list.append(proc)
                else:
                    Q3list.append(proc)
        
        printQueue = printQueues(Q1list, Q2list, Q3list)
        print("At Time = ", time)                                           # At Time = 8
        print(f"Queues : {printQueue[0]};{printQueue[1]};{printQueue[2]}")  # Queues : [B, C];[];[]
        print("CPU : ", CPU, "\n")                                          # CPU : A
        
        time += 1
        
        if(time == 15):
            break
            
def enqueueIncoming(procList, time, Q1list):
    for proc in procList:
        if(proc.arrivaltime == time):
            Q1list.append(proc)
    return Q1list
    
def addIO(IOlist, currProc):
    if(len(currProc.IOburst) > 0):
        IOlist.append(currProc)
    return IOlist
    
def printQueues(Q1list, Q2list, Q3list):
  Q1 = [x.name for x in Q1list]
  Q2 = [x.name for x in Q2list]
  Q3 = [x.name for x in Q3list]
  return [Q1, Q2, Q3]

def main():
    timeAllotmentQ1 = 8
    timeAllotmentQ2 = 8
    contextSwitch = 0
    
    # Process A
    A_CPUburst = [15, 5]
    A_IOburst = [10]
    A = Process("A", 0, A_CPUburst, A_IOburst, timeAllotmentQ1, timeAllotmentQ2, "Q1")
    
    # Process B
    B_CPUburst = [8, 4]
    B_IOburst = [5]
    B = Process("B", 0, B_CPUburst, B_IOburst, timeAllotmentQ1, timeAllotmentQ2, "Q1")
    
    # List of processes
    procList = []
    
    procList.append(A)
    procList.append(B)
    
    MLFQ(procList, contextSwitch)
    
if __name__ == "__main__":
    main()
