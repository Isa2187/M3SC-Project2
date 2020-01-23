import numpy as np
import scipy as sp
import csv
import sys

#Using the BellmanFord function provided, I modified it by 
#introducing a new argument noLink, which is a real number 
#pre-determined based on the weights of the weight matrix,
#which in out case is based on the job times for any
#given list of jobs that we may be given
def MyBellmanFord(ist,isp,wei,noLink):

    #ist = index of start node
    #isp = index of end node
    #wei = weight matrix whose weights in our case represent
    #      the times between nodes   
    #noLink = real number which is unique to the
    #         pre-constructed weight matrix, and is used below
    #         so that we do not use any edges of weight noLink
    #Note: noLink is a really big number which symbolises 
    #      there being no link between two nodes. In the 
    #      original BellmanFord function, an entry of 0 
    #      represented there being no connection between two 
    #      nodes, but in this case the weights represent
    #      times and we do wish to consider time periods of
    #      0 length, so now noLink represents a very large 
    #      time which is undesirable to us, hence we do not 
    #      use edges of this weight
    
    #Assign V to be the number of nodes in our network
    V = wei.shape[1]

    #Step 1: Initialization (this is provided to us)
    Inf    = sys.maxint
    d      = np.ones((V),float)*np.inf
    p      = np.zeros((V),int)*Inf
    d[ist] = 0

    #Step 2: Iterative relaxation (this was given to us)
    #Note: One subtle change I made was on line 50 below,
    #      namely if (w != noLink), so we only consider edges
    #      where we do not encounter a place at which there is
    #      no connection between two nodes, which is
    #      represented by an edge of weight noLink in the 
    #      pre-constructed weight matrix
    for i in range(0,V-1):
        for u in range(0,V):
            for v in range(0,V):
                w = wei[u,v]
                if (w != noLink):
                    if (d[u]+w < d[v]):
                        d[v] = d[u] + w
                        p[v] = u

    #Step 3: Check for negative-weight cycles (this was given
    #        to us). I did make a small change on line 66,
    #        namely if (w != noLink) as opposed to if (w != 0)
    #Note: due to the fact that we have a directed acyclic 
    #      graph, we should not expect to find any 
    #      negative-weight cycles, but it must be considered
    #      since the Bellman-Ford algorithm can take negative
    #      weights
    for u in range(0,V):
        for v in range(0,V):
            w = wei[u,v]
            if (w != noLink):
                if (d[u]+w < d[v]):
                    print('graph contains a negative-weight cycle')

    #Step 4: Determine the shortest path (this was given to 
    #        us), and store it in the list shpath
    shpath = [isp]
    while p[isp] != ist:
        shpath.append(p[isp])
        isp = p[isp]
    shpath.append(ist)

    return shpath[::-1]

#calcWei is a function that was given to us, which produces
#a weight matrix given some information that is inputted as 
#arguments of the function in the form of arrays
def calcWei(RA,RB,RT):

    #Set n to be 2*(number of jobs) + 2, where in our case the
    #number of jobs that need completing is 13, giving n = 28.
    #This is so that in our weight matrix, every job has a
    #"start" and "finish" node, and ensures the existence of a
    #"virtual" start node and a "virtual" finish node so we
    #can implement the given algorithm
    n = 28
    wei = np.zeros((n,n),dtype=float)
    m = len(RA)
    for i in range(m):
        wei[RA[i],RB[i]] = RT[i]
    return wei

#Read in the data containing the job duration times and job
#dependencies from the text file JobInformation, and store
#the data in the arrays startNodes, finishNodes and jobTimes
startNodes = np.empty(0,dtype=int)
finishNodes = np.empty(0,dtype=int)
jobTimes = np.empty(0,dtype=float)

with open('JobInformation','r') as file:
    AAA = csv.reader(file)
    for row in AAA:
        startNodes=np.concatenate((startNodes,[int(row[0])]))
        finishNodes=np.concatenate((finishNodes,[int(row[1])]))
        jobTimes=np.concatenate((jobTimes,[float(row[2])]))
file.close()

#Compute the weight matrix for our jobs using the information
#imported from JobInformation
weightMatrix = calcWei(startNodes,finishNodes,jobTimes)

#Assign maxTime to be the largest entry of weightMatrix, which
#gives us the time of the job with the longest duration time
maxTime = np.amax(weightMatrix)
#Assign noLink1 to be the -maxTime*100, which will be used 
#by MyBellmanFord to determine where no edges exist between 
#any two given nodes
#Note: For any given job list, the value of maxTime and 
#      therefore noLink1 will be specific and always
#      applicable, so it is a valid way of assigning and
#      recognising where there is no connection between two
#      nodes in the directed graph   
noLink1 = -maxTime*100

#Where we originally had a weight of 0 between two nodes in
#the original weightMatrix, due to the functionality of
#calcWei this first 0 symbolised the fact there is no
#connection, so replace all of these 0's by noLink1
index1 = np.where(weightMatrix == 0)
weightMatrix[index1] = noLink1

#Where we have a weight of -1 between two nodes, I used this
#to represent either a job dependency or an edge between the
#"virtual" start and finish nodes in the file JobInformation;
#since we need all of these edges to have weight 0, change all
#of these -1's to 0's. This must happen after the previous
#line so the two sets of 0's are not confused
index2 = np.where(weightMatrix == -1)
weightMatrix[index2] = 0

#Initialise a list of jobs called jobList, which keeps track
#of which jobs we are yet to find in a current longest job
#sequence; once a job appears in a current longest string, it 
#will be removed from jobList. This is to ensure that we do
#not  run the function MyBellmanFord unnecessarily, since this
#will be computationally expensive so we want to run the
#function as few times as possible
#Note: I used 13 since we have 13 jobs (numbered from 0 to 12)
#      to complete, but this can be changed accordingly
jobList = list(np.arange(13))

#Initialise workFlow to store the longest string of jobs 
#before we then iteratively determine the subsequent shorter
#job strings
#Note: I will not store sub-sequences of any job strings that 
#      are found to be the longest strings at any given
#      iteration e.g if [0,1,4] is found to be a longest
#      string, the subsequent job string [0,1] will not be
#      stored in workFlow, as this will lead to unnecessary
#      implementations of MyBellmanFord
workFlow = []

#Whilst we still need to determine the earliest possible start
#and finish times for a job, run MyBellmanFord using the 
#current weightMatrix (this will be altered slightly below),
#with the "virtual" start node (index 26) as our starting node
#and the "virtual" finish node (index 27) as our final node
while len(jobList) != 0:    

    #Obtain the current longest string of jobs, and store it
    #in the list longestString. Since we wish to find the
    #longest string, I input -weightMatrix because the
    #Bellman-Ford algorithm is designed to find the shortest
    #path, so by doing this it finds the shortest path for the
    #negative times which is hence the longest path for the
    #positive times.
    #Also recall that noLink1 is a negative number, but in
    #-weightMatrix any entries that were initially noLink1 
    #now become equal to -noLink1, so I want MyBellmanFord to
    #recognise -noLink1 as there not being a connection
    #between two nodes in -weightMatrix as opposed to noLink1
    longestString = MyBellmanFord(26,27,-weightMatrix,-noLink1) 
       
    #Since longestString contains the indexes of the "virtual"
    #start node, "virtual" finish node and the "start" and
    #"finish" nodes of all of the respective jobs in between,
    #the code below ensures that longestString consists of a
    #string of jobs with the correct numbering i.e. the
    #desired string of jobs which can easily be read and
    #respects the numbering of the jobs in question
    del longestString[0]
    del longestString[-1]
    longestString = longestString[1::2]
    
    for i in range(len(longestString)):
        longestString[i] = (longestString[i]-1)/2
    
    #Once we have obtained the longest string of jobs in its
    #desired form, add it to the list of strings workFlow 
    #using append
    workFlow.append(longestString)  
    
    #To ensure we only run MyBellmanFord as many times as is 
    #absolutely necessary, once a job appears in a longest 
    #string I remove the connection between the finish nodes
    #of these jobs and the "virtual" finish node; this is to
    #avoid the occurrence of sub-sequences of jobs appearing
    #in workFlow. I also remove these jobs from jobList
    #because we now know the order in which these jobs must
    #appear, meaning we do not run MyBellmanFord excessively
    #for the reasons outlined above
    for i in longestString:
        if i in jobList:
            jobList.remove(i) 
            weightMatrix[2*i+1,27] = noLink1
            
#List the times taken to complete each of the jobs in the
#array jobDurations so that we can refer to it when
#determining the earliest possible start and finish times for
#the jobs from workFlow                
jobDurations = [41,51,50,36,38,45,21,32,32,49,30,19,26]

#Initialise two arrays of size 13 since we have 13 jobs, which
#will store the earliest possible start and finish times for
#each of the jobs
earliestStartTimes = np.zeros(13)
earliestFinishTimes = np.zeros(13)

#For every string of jobs in workFlow, cumulatively determine 
#the earliest possible start and finish times for all of the 
#jobs by going through every job sequence in workFlow.
#Note: due to the fact that workFlow does not contain any 
#      sub-sequences, as well as the fact workFlow begins
#      with the longest string and descends from there, even
#      if we do have the occurrence of a particular job in 
#      multiple strings, the job orders will not conflict with
#      each other, meaning it is acceptable to override
#      values in the iterations below. This is because every
#      time we obtain a longest path, we know for a fact that
#      this must be the longest way of completing EVERY job in
#      that sequence, and it is not possible for the order to
#      change later on because if it did, then the original
#      longest string containing this job wouldn't actually be
#      the longest string.
for string in workFlow:
    
    #sumTime is initialised to 0, and as we go through each 
    #string of jobs we add the duration time of the current
    #job to it so that it keeps track of the cumulative time
    #for a given string as we go through it
    sumTime = 0
    for i in string:
        earliestStartTimes[i] = sumTime
        sumTime = sumTime + jobDurations[i]
        earliestFinishTimes[i] = sumTime