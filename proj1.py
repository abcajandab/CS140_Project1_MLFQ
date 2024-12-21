#CS 140 Project 1: MLFQ Scheduler

#Members
#Cajandab, Alleenna
#Cumabig, Luigi


class Process:
    def __init__(self, name, arrivaltime, CPUburst, IOburst, Q1timeallot, Q2timeallot, level):
        self.name = name
        self.arrivaltime = arrivaltime
        self.CPUburst = CPUburst
        self.IOburst = IOburst
        self.Q1timeallot = Q1timeallot
        self.Q2timeallot = Q2timeallot
        self.level = level

    ## For printing to check    
    def __str__(self):
        return (f"Process {self.name}:\n"
                f"  Arrival Time: {self.arrivaltime}\n"
                f"  CPU Burst: {self.CPUburst}\n"
                f"  IO Burst: {self.IOburst}\n"
                f"  Q1 Time Allotment: {self.Q1timeallot}\n"
                f"  Q2 Time Allotment: {self.Q2timeallot}\n"
                f"  Level: {self.level}")


        
def MLFQ(procList, contextSwitch):
    # Global time
    time = 0
    
    # List of Queue levels
    Q1list = []
    Q2list = []
    Q3list = []
    
    # List of processes currently in CPU or IO
    prevCPU = ""
    CPU = ""
    IOlist = []
    arrivingProcs = []
    
    contextCounter = contextSwitch
    contextSwitching = False
    quantum = 4
    while(len(procList) > 0):
        # Check if the process to be run is the same as prev, if not do context switch
        currProc = currentProc(Q1list, Q2list, Q3list)
        if(prevCPU == currProc):
          contextSwitching = False

        # Enqueue incoming processes
        Q1list = enqueueIncoming(procList, time, Q1list, arrivingProcs) #Enqueue the newly arriving process.
          
        # CPU
        if(contextSwitching and contextSwitch > 0):
            CPU = "Context Switching"
            contextCounter -= 1
            if(contextCounter == 0):
                contextCounter = contextSwitch
                contextSwitching = False
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
                    quantum = 4
                    contextSwitching = True
                
                elif(quantum == 0):
                    currProc = Q1list.pop(0)
                    if(currProc.Q1timeallot > 0):
                        Q1list.append(currProc)      # stay in queue (dequeue then enqueue)
                    else:
                        Q2list.append(currProc)      # move process to lower queue
                    
                    quantum = 4
                    contextSwitching = True
                    
                prevCPU = CPU
                    
            # Q2 (Medium Priority Queue): First-come First Served Scheduling
            elif(len(Q2list) > 0):
                CPU = Q2list[0].name
                Q2list[0].CPUburst[0] -= 1
                Q2list[0].Q2timeallot -= 1
                
                if(Q2list[0].CPUburst[0] == 0):
                    currProc = Q2list.pop(0)
                    currProc.CPUburst.pop(0)         # remove 0 CPU burst time
                    if(currProc.Q2timeallot > 0):
                        currProc.Q2timeallot = 8     # renew Q2 time allotment
                        currProc.level = "Q2"
                    else:
                        currProc.level = "Q3"        # change level to Q3
                        
                    IOlist = addIO(IOlist, currProc) # add current process if there are still IOburst
                    contextSwitching = True
                
                elif(Q2list[0].Q2timeallot == 0):
                    currProc = Q2list.pop(0)
                    Q3list.append(currProc)          # move process to lower queue
                    sortQ3(Q3list)
                    
                prevCPU = CPU
            
            # Q3 (Least Priority Queue): Shortest Job First
            elif(len(Q3list) > 0):
                CPU = Q3list[0].name
                Q3list[0].CPUburst[0] -= 1
                
                if(Q3list[0].CPUburst[0] == 0):
                    currProc = Q3list.pop(0)
                    currProc.CPUburst.pop(0)         # remove 0 CPU burst time
                        
                    IOlist = addIO(IOlist, currProc) # add current process if there are still IOburst
                    contextSwitching = True
                    
                prevCPU = CPU
        
        # make a function to print this: (to make it cleaner)
        printQueue = printQueues(Q1list, Q2list, Q3list)
        print("At Time = ", time)                                           # At Time = 8
        print(f"Queues : {printQueue[0]};{printQueue[1]};{printQueue[2]}")  # Queues : [B, C];[];[]
        print("CPU : ", CPU, "\n")                                          # CPU : A
        
        # I/O 
        for proc in IOlist:
            proc.IOburst[0] -= 1
            if(proc.IOburst[0] <= 0):
                proc.IOburst.pop(0)    # remove the 0 IO burst
                IOlist.remove(proc)    # remove from IO list
                if(proc.level == "Q1" and proc.CPUburst):
                    Q1list.append(proc)
                elif(proc.level == "Q2" and proc.CPUburst):
                    Q2list.append(proc)
                elif(proc.level == "Q3" and proc.CPUburst):
                    Q3list.append(proc)
                    sortQ3(Q3list)
        
        removeProc(procList)
        time += 1
            
def enqueueIncoming(procList, time, Q1list, arrivingProcs):
    for proc in procList:
        if(proc.arrivaltime == time):
            Q1list.append(proc)
            arrivingProcs.append(proc.name)
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

def removeProc(procList):
    for proc in procList:
        if(not proc.CPUburst and not proc.IOburst):
            procList.remove(proc)

def currentProc(Q1list, Q2list, Q3list):
    for proc in Q1list:
        return proc.name
    for proc in Q2list:
        return proc.name
    for proc in Q3list:
        return proc.name
    return None
      
def sortQ3(Q3list):
    Q3list.sort(key=lambda proc: proc.CPUburst[0] if proc.CPUburst else float('inf'))




def main():

    ##this works na for parsing! commented out rn bc its easier to check with the hardcoded details
    
##    print("# Enter Scheduler Details #")
##    num_processes = int(input())
##    timeAllotmentQ1 = int(input())
##    timeAllotmentQ2 = int(input())
##    contextSwitch = int(input())
##    
##    print(f"# Enter {num_processes} Process Details #")
##    procList = []
##
##    for i in range(num_processes):
##        process_info = input().split(";")
##        process_name = process_info[0]
##        arrival_time = int(process_info[1])
##        CPUburst = []
##        IOburst = []
##        for i in range(2, len(process_info)):
##            if i % 2 == 0:
##                CPUburst.append(int(process_info[i]))
##            else:
##                IOburst.append(int(process_info[i]))
##        procList.append(Process(process_name, arrival_time, CPUburst, IOburst, timeAllotmentQ1, timeAllotmentQ2, "Q1" ))

    
    timeAllotmentQ1 = 8
    timeAllotmentQ2 = 8
    contextSwitch = 0
    
    # Process A
    A_CPUburst = [2, 6]
    A_IOburst = [2]
    A = Process("A", 2, A_CPUburst, A_IOburst, timeAllotmentQ1, timeAllotmentQ2, "Q1")
    
    # Process B
    B_CPUburst = [5,5,5]
    B_IOburst = [2,2]
    B = Process("B", 0, B_CPUburst, B_IOburst, timeAllotmentQ1, timeAllotmentQ2, "Q1")

    # Process C
    C_CPUburst = [30]
    C_IOburst = []
    C = Process("C", 0, C_CPUburst, C_IOburst, timeAllotmentQ1, timeAllotmentQ2, "Q1")
    
    # List of processes
    procList = []
    
    procList.append(A)
    procList.append(B)
    procList.append(C)


    #Print proccesses (for checking)
    print("Processes in procList:")
    for process in procList:
         print(process)
         print("-" * 40)
    
    
    MLFQ(procList, contextSwitch)
    
if __name__ == "__main__":
    main()
