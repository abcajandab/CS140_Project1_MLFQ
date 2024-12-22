#CS 140 Project 1: MLFQ Scheduler

#Members
#Cajandab, Alleenna
#Cumabig, Luigi


class Process:
    def __init__(self, name, arrivaltime, CPUburst, IOburst, Q1timeallot, Q2timeallot, level, completionTime, waitingTime):
        self.name = name
        self.arrivaltime = arrivaltime
        self.CPUburst = CPUburst
        self.IOburst = IOburst
        self.Q1timeallot = Q1timeallot
        self.Q2timeallot = Q2timeallot
        self.level = level
        self.completionTime = completionTime
        self.waitingTime = waitingTime

    ## For printing to check    
    def __str__(self):
        return (f"Process {self.name}:\n"
                f"  Arrival Time: {self.arrivaltime}\n"
                f"  CPU Burst: {self.CPUburst}\n"
                f"  IO Burst: {self.IOburst}\n"
                f"  Q1 Time Allotment: {self.Q1timeallot}\n"
                f"  Q2 Time Allotment: {self.Q2timeallot}\n"
                f"  Level: {self.level}")


        
def MLFQ(procList, contextSwitch, timeAllotmentQ1, timeAllotmentQ2):
    # Global time
    time = 0
    
    # List of Queue levels
    Q1list = []
    Q2list = []
    Q3list = []
    
    # List of processes currently in CPU or IO
    CPU = ""
    prevCPU = ""
    demotedProc = ""
    finishedProc = ""
    IOlist = []
    newQueue = []
    prevQueue = []
    IOlistPrint = []
    finalProcList = []
    arrivingProcs = []
    
    contextCounter = contextSwitch
    isContextSwitching = False
    quantum = 4
    while(len(procList) > 0):
        # Check if the process to be run is the same as prev, if not do context switch
        currProc = currentProc(Q1list, Q2list, Q3list)
        if currProc == None: CPU = ""
        if(prevCPU == currProc):
          isContextSwitching = False
          
        addWaitTime(currProc, Q1list, Q2list, Q3list)
        
        # Enqueue incoming processes
        Q1list = enqueueArriving(procList, time, Q1list, arrivingProcs)
          
        # CPU
        if(isContextSwitching and contextSwitch > 0):
            CPU = "Context Switching"
            contextCounter -= 1
            if(contextCounter == 0):
                contextCounter = contextSwitch
                isContextSwitching = False
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
                        currProc.Q1timeallot = timeAllotmentQ1     # renew Q1 time allotment
                        currProc.level = "Q1"
                    else:
                        currProc.level = "Q2"        # change level to Q2
                        
                    addIO(IOlist, currProc)         # add current process if there are still IOburst
                    quantum = 4
                    isContextSwitching = True
                
                elif(quantum == 0):
                    currProc = Q1list.pop(0)
                    if(currProc.Q1timeallot > 0):
                        Q1list.append(currProc)      # stay in queue (dequeue then enqueue)
                    else:
                        Q2list.append(currProc)      # move process to lower queue

                    quantum = 4
                    isContextSwitching = True
                    
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
                        currProc.Q2timeallot = timeAllotmentQ2     # renew Q2 time allotment
                        currProc.level = "Q2"
                    else:
                        currProc.level = "Q3"        # change level to Q3
                        
                    addIO(IOlist, currProc) # add current process if there are still IOburst
                    isContextSwitching = True
                
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
                        
                    addIO(IOlist, currProc) # add current process if there are still IOburst
                    isContextSwitching = True
                    
                prevCPU = CPU
        
        # Print the current status of CPU
        newQueue = printQueues1(Q1list, Q2list, Q3list, CPU, IOlist)
        printOutput(Q1list, Q2list, Q3list, time, CPU, IOlistPrint, arrivingProcs, finishedProc, demotedProc)
        
        IOlistPrint = printIO(IOlist)
        demotedProc = demotion(prevQueue, newQueue)
        prevQueue = printQueues1(Q1list, Q2list, Q3list, CPU, IOlist)
        finishedProc = ""

        # I/O
        to_remove_from_IO = []
        for proc in IOlist:
            proc.IOburst[0] -= 1
            if proc.IOburst[0] <= 0:
                to_remove_from_IO.append(proc)  # mark for removal from IO list
                if proc.level == "Q1" and proc.CPUburst:
                    Q1list.append(proc)
                elif proc.level == "Q2" and proc.CPUburst:
                    Q2list.append(proc)
                elif proc.level == "Q3" and proc.CPUburst:
                    Q3list.append(proc)
                    sort_Q3(Q3list)             # Ensure Q3 is sorted after adding new process
      
        # Remove processes in procList that has no more CPU or IO burst
        finishedProc = removeProc(procList, finishedProc, finalProcList, time)
        
        # Remove processes from IOlist after iteration
        for proc in to_remove_from_IO:
            proc.IOburst.pop(0)
            IOlist.remove(proc)
            
        arrivingProcs = []
        time += 1
    
    print("SIMULATION DONE \n")
    printTurnAroundTime(finalProcList)
    printWaitingTime(finalProcList)
        
        
# Enqueues arriving process
def enqueueArriving(procList, time, Q1list, arrivingProcs):
    for proc in procList:
        if(proc.arrivaltime == time):
            Q1list.append(proc)
            arrivingProcs.append(proc.name)
    return Q1list
    
# Remove process from procList (used to stop the main while loop)
def removeProc(procList, finishedProc, finalProcList, time):
    for proc in procList:
        if(not proc.CPUburst and not proc.IOburst):
            finishedProc = proc.name
            proc.completionTime = time + 1
            finalProcList.append(proc)
            procList.remove(proc)
    return finishedProc

# Add process in the IO list is it still has IO bursts
def addIO(IOlist, currProc):
    if(len(currProc.IOburst) > 0):
        IOlist.append(currProc)

# Returns the process that will run the CPU 
def currentProc(Q1list, Q2list, Q3list):
    for proc in Q1list:
        return proc.name
    for proc in Q2list:
        return proc.name
    for proc in Q3list:
        return proc.name
    return None

# Sorts Q3 by their CPU burst
def sortQ3(Q3list):
    Q3list.sort(key=lambda proc: proc.CPUburst[0] if proc.CPUburst else float('inf'))

# Returns names of active processes in queues
def printQueues(Q1list, Q2list, Q3list, CPU, IOlistPrint):
  Q1 = [x.name for x in Q1list if x.name != CPU and x.name not in IOlistPrint]
  Q2 = [x.name for x in Q2list if x.name != CPU and x.name not in IOlistPrint]
  Q3 = [x.name for x in Q3list if x.name != CPU and x.name not in IOlistPrint]
  return [Q1, Q2, Q3]

# Similar to the above function (no need to include in documentation)
def printQueues1(Q1list, Q2list, Q3list, CPU, IOlistPrint):
  Q1 = [x.name for x in Q1list if x.name not in IOlistPrint]
  Q2 = [x.name for x in Q2list if x.name not in IOlistPrint]
  Q3 = [x.name for x in Q3list if x.name not in IOlistPrint]
  return [Q1, Q2, Q3]

# Returns processes currently in IO
def printIO(IOlist):
  return [proc.name for proc in IOlist]

# Prints necessary output per time step
def printOutput(Q1list, Q2list, Q3list, time, CPU, IOlist, arrivingProcs, finishedProc, demotedProc):
  printQueue = printQueues(Q1list, Q2list, Q3list, CPU, IOlist)
  print("At Time = ", time)                                           # Time
  
  if len(arrivingProcs) > 0 : print("Arriving : ", arrivingProcs)     # Arriving processes
  if finishedProc != "" : print(finishedProc, " DONE")
  
  print(f"Queues : {printQueue[0]};{printQueue[1]};{printQueue[2]}")  # Queues
  print("CPU : ", CPU)                                                # Current process using CPU
  
  if len(IOlist) > 0 : print("IO : ", IOlist)
  if demotedProc != "" : print(demotedProc, "DEMOTED")
  
  print()
  
# Returns demoted process
def demotion(prevQueue, newQueue):
    demotions = ""
    if len(prevQueue) == 0 : return demotions
    
    prevQ1, prevQ2, prevQ3 = prevQueue
    newQ1, newQ2, newQ3 = newQueue
    # Check for demotions from Q1 to Q2
    for proc in prevQ1:
        if proc in newQ2:
            demotions = proc
    # Check for demotions from Q2 to Q3
    for proc in prevQ2:
        if proc in newQ3:
            demotions = proc

    return demotions

# Adds wait time to every process waiting in the queue
def addWaitTime(currproc, Q1list, Q2list, Q3list):
  for proc in Q1list:
    if currproc != proc.name : proc.waitingTime += 1
  for proc in Q2list:
    if currproc != proc.name : proc.waitingTime += 1
  for proc in Q3list:
    if currproc != proc.name : proc.waitingTime += 1

# Prints turnaround time of each process and their average
def printTurnAroundTime(finalProcList):
  finalProcList.sort(key=lambda p: p.name)
  total = 0
    
  for proc in finalProcList:
    turnAround = proc.completionTime - proc.arrivaltime
    total += turnAround
    print(f"Turn-around time for Process {proc.name} : {proc.completionTime} - {proc.arrivaltime} = {turnAround} ms")
      
  avgTurnAround = total/len(finalProcList)
  print(f"Average Turn-around time = {avgTurnAround} ms")
    
# Prints waiting time for each process
def printWaitingTime(finalProcList):
  finalProcList.sort(key=lambda p: p.name)
  for proc in finalProcList:
    print(f"Waiting time for Process {proc.name} : {proc.waitingTime} ms")



def main(): 
    print("# Enter Scheduler Details #")
    num_processes = int(input())
    timeAllotmentQ1 = int(input())
    timeAllotmentQ2 = int(input())
    contextSwitch = int(input())
    
    print(f"# Enter {num_processes} Process Details #")
    procList = []

    for i in range(num_processes):
      process_info = input().split(";")
      process_name = process_info[0]
      arrival_time = int(process_info[1])
      CPUburst = []
      IOburst = []
      for i in range(2, len(process_info)):
        if i % 2 == 0:
          CPUburst.append(int(process_info[i]))
        else:
          IOburst.append(int(process_info[i]))
      procList.append(Process(process_name, arrival_time, CPUburst, IOburst, timeAllotmentQ1, timeAllotmentQ2, "Q1", 0, 0))


    #Print proccesses (for checking)
    print("Processes in procList:")
    for process in procList:
      print(process)
      print("-" * 40)
    
    
    MLFQ(procList, contextSwitch, timeAllotmentQ1, timeAllotmentQ2)
    
if __name__ == "__main__":
    main()
