# Import statements
from Server import Server
from sys import maxint
from math import log, ceil
from random import random, uniform, seed, randint

class Simulator(object):

    """
    __init__

    Initialization function for the Simulator object. Assigns the necessary instance variables based on arguments,
    create the server objects needed, and set up the lists necessary for tracking the results.

    @param lamb: the interarrival rate for the simulator
    @param mu: the job size parameter for the simulator
    @param numServers: number of servers that the simulator will contain
    @param simTime: the number of time units the simulator is alloted to run for
    @param numReps: number of repetitions the simulator will run for
    @param jobMaxMIPS: the maximum number of millions of instructions per second (MIPS) that a job can reach
    @param toTurnOn: the aggressivness parameter determines the number of servers that are initially turned on within the simulator

    @return: none
    """
    def __init__(self, lamb, mu, numServers, simTime, numReps, jobMaxMIPS, toTurnOn):
        super(Simulator, self).__init__()

        # Inistialize instance variables from arguments
        self.maxMIPS = jobMaxMIPS
        self.lamb = lamb
        self.mu = mu
        self.numServers = numServers
        self.simTime = simTime
        self.numRepetitions = numReps
        self.numServersToTurnOn = toTurnOn

        # Fill an array with numServers Server objects
        self.servers = [Server() for i in range(0, numServers)]

        # Initialize to default values
        self.timeToNextArrival = 0
        self.timeToNextDeparture = 0
        self.currentTime = 0
        self.numArrivals = 0
        self.numDepartures = 0
        self.numJobsInSystem = 0

        # Declare arrays to hold data that will be used for analysis by the penaltyFunction
        # This can become its own structure later ?
        self.throughput = []
        self.avgNumJobsInSystem = []
        self.powerConsumedByServers = []
        self.avgServerUtilizations = []
        self.maxTempTracker = []
        self.avgResponseTimes = []

        # For plotting results -- DEPRACATED
        self.avgJobsTracker = []
        self.timeTracker = []

        # Debug logger
        # print '--- Init ----'
        # print 'Turning on ', self.numServersToTurnOn, ' servers...'
        # print '--- **** ----'
        # Turn on self.numServersToTurnOn servers <- declared above
        for server in self.servers:
            if self.servers.index(server) < self.numServersToTurnOn:
                server.setIsServerOn(True)
        # Once the necessary number of servers has been turned on, theres no point in continuing the loop
            else:
                break

    """
    resetVariablesForNewRepetition

    Reset the the necessary variables for a new repetition of the simulation.
    All of the variables being reset are those with default values in the initializer.
    New servers are also created and turned on as necessary

    @return: none
    """
    def resetVariablesForNewRepetition(self):
        # Initialize to default values
        self.servers = [Server() for i in range(0, self.numServers)]
        self.timeToNextArrival = 0
        self.timeToNextDeparture = 0
        self.numJobsInSystem = 0
        self.currentTime = 0
        self.numArrivals = 0
        self.numDepartures = 0
        # Turn on self.numServersToTurnOn servers
        for server in self.servers:
            if self.servers.index(server) < self.numServersToTurnOn:
                server.setIsServerOn(True)
        # Once the necessary number of servers has been turned on, theres no point in continuing the loop
            else:
                break

    """
    getPowerConsumptions

    @return: list containing the power consumption of each server for each repetition
    """
    def getPowerConsumptions(self):
        return self.powerConsumedByServers

    """
    getAvgServerUtils

    @return: list containing the average utilization of each server for each repetition
    """
    def getAvgServerUtils(self):
        return self.avgServerUtilizations

    """
    getMaxTemps

    @return: list containing the maximum temperature of each server for each repetition
    """
    def getMaxTemps(self):
        return self.maxTempTracker

    """
    getThroughput

    @return: list containing the throughput for each repetition
    """
    def getThroughput(self):
        return self.throughput

    """
    getAvgJobsInSimulation

    @return: list containing the average number of jobs within the simulation for each repetition
    """
    def getAvgJobsInSimulation(self):
        return self.avgNumJobsInSystem

    """
    getAvgResponseTime

    @return: list containing the average response time for each server's completed tasks
             for each repetition
    """
    def getAvgResponseTime(self):
        return self.avgResponseTimes

    """
    addNewJobToServers

    Add a new job to a specific server.
    First a processing time is determined using the generateNextProcessingTime() method,
    then the utilization requirements of the job are determined in MIPS and the job is added to a specified server.
    This method should be used when to change a routing policy if necessary.

    """
    def addNewJobToServers(self):
        processingTime = self.generateNextProcessingTime()
        jobMIPS = self.generateNextJobMIPS()
        # Change decision making policy here
        indexOfServerToAssign = self.getIndexUsingShortestQueueWithDNSandRR()
        self.servers[indexOfServerToAssign].addNewArrival(self.currentTime, processingTime, jobMIPS)

    """
    generateNextJobMIPS

    Generate a random MIPS requirement for a job that is to be assigned. MIPS is generated from the desired utilization,
    but is allowed to "wiggle" within an acceptable margin; i.e. if the desired utilization is 0.7 then the MIPS can vary
    between 0.7-0.7*wiggle to 0.7+0.7*wiggle utilization. The utilization ultimately evens out within a few percent of the desired utilization.
    The wiggle can be adjusted to lessen or increase the range.

    Checks are in place to ensure that no utilization below 0 or above 1 can occur relative to the maxMIPS

    @return: the MIPS requirement for a job
    """
    def generateNextJobMIPS(self):
        # Setpoint is generated from Utilization = (Lambda / (Mu*numServers))
        setpoint = self.maxMIPS*(self.lamb / self.numServers)
        wiggle = 0.40
        lower = setpoint - wiggle * setpoint
        upper = setpoint + wiggle * setpoint
        currMIPS = uniform(lower, upper)
        # Checks in place to ensure jobs generated can't drive servers past 100% utilization or below 0% utilization
        if currMIPS / self.maxMIPS > 1.0:
            return self.maxMIPS
        # This seems like a stupid check, but if the lowerbound is somehow negative and the generator returns a value less than 0
        # as a result, this check will catch it.
        elif currMIPS / self.maxMIPS < 0.0:
            return 0.0
        return currMIPS

    """
    generateRandomTime

    Generates a uniform random value based on the input parameter

    @param param: Either lambda or mu depending on the use. Lambda used to generate a job arrival time,
                  mu used to generate a job processing time.

    @return: a random time
    """
    def generateRandomTime(self, param):
        return -1.0 * log(random()) / (float)(param)

    """
    generateNextArrival

    Generates an arrival time based on the interarrival rate Lambda

    @return: arrival time for another job
    """
    def generateNextArrival(self):
        return self.generateRandomTime(self.lamb)

    """
    generateNextProcessingTime

    Generates a processing time for a job based on the job size parameter, mu

    @return: processing time for a job
    """
    def generateNextProcessingTime(self):
        return self.generateRandomTime(self.mu)

    """
    getRandomServer

    Returns the index of a random server amongst all available servers

    @return: index of a random server
    """
    def getRandomServer(self):
        return (randint(0,100)) % len(self.servers)

    """
    getIndexUsingShortestQueueWithDNSandRR

    Determine a server index based on the following:

    (1) - Check servers sequentially and find one that:
          -> (a) - Is already on
          -> (b) - Has a utilization below a certain threshold
    (2) - If (a) and (b) are met then
          -> Assign the job to that server's queue
    (3) - If (a) and (b) are not met
          -> Turn on a new server and use that
    (4) -> If no servers can be turned on since they're all already being used and are on
          -> Assign the job randomly

    @return: index of a server based on the aforementioned rules
    """
    def getIndexUsingShortestQueueWithDNSandRR(self):
        serverChosen = None
        # Threshold for utilization before taking the server out of consideration
        # This could become an instance variable later on...
        upperBoundUtil = 0.9
        # Scan all servers -> Can be made more efficient by keeping track of servers by their utilization and status
        for server in self.servers:
            # Check for (1)
            if server.getIsServerOn() and server.util < upperBoundUtil:
                # Step (2)
                tempLength = maxint if serverChosen is None else serverChosen.getQueueLength()
                if server.getQueueLength() < tempLength:
                    serverChosen = server
                    # Uncomment to see which servers are being selected while they're still on and why
                    # print 'Server ', server.getServerID(), ' is', server.getIsServerOn(), 'and has util ', server.getInstantUtil()
        # If a server has not been assigned that means that (a) and (b) where not met.
        # Now at step (3)
        if serverChosen is None:
            for server in self.servers:
                if not server.getIsServerOn():
                    # Uncomment to see which servers are being turned on
                    # print 'Turning on server ', server.getServerID()
                    server.setIsServerOn(True)
                    serverChosen = server
        # Check if the job still hasn't been assigned
        # Resort to random routing
        # Now at step (4)
        if serverChosen is None:
            # Uncomment to see if the router has to resort to being random due to overutilization
            # If this is happening at anything less than ~95% utilization there's an issue.
            # print 'Had to resort to random routing... '
            return self.getRandomServer()
        return self.servers.index(serverChosen)

    """
    allocatedWithDynamicShutdowns

    This is honestly just here to call the previous method. I'll roll them into one method soon.

    @return: none
    """
    def allocatedWithDynamicShutdowns(self, processingTime, processingMIPS):
        self.servers[self.getIndexUsingShortestQueueWithDNSandRR()].addNewArrival(self.currentTime, processingTime, processingMIPS)

    """
    getServerWithNextDeparture

    Scan the servers and find the server with the next departure time. Can optimize this by keeping track of the servers during
    scans in previous function.

    @return: index of server with the earliest departure time
    """
    def getServerWithNextDeparture(self):
        nextDeparture = self.servers[0]
        for server in self.servers:
            if (server.getNextDepartureTime() < nextDeparture.getNextDepartureTime()):
                nextDeparture = server
        return self.servers.index(nextDeparture)

    """
    updateServerTimes

    Update the times for all servers. The remaining processing times will be updated for jobs being worked on for each server.

    @return: none
    """
    def updateServerTimes(self, elapsedTime):
        for server in self.servers:
            server.updateProcessingTimes(elapsedTime)

    """
    updateAverageNumJobsInSystem

    Updates the rolling average of the number of jobs within the system.

    @return: none
    """
    def updateAverageNumJobsInSystem(self, i, t1, t2):
        self.avgNumJobsInSystem[i] = self.avgNumJobsInSystem[i] * t1 / (float)(t1 + t2) + self.numJobsInSystem * t2 / (float)(t1 + t2)

    """
    runSimulation

    Runs the simulation based on the parameters passed in to the initializer.

    The method will run numRepetitions repetitions of the simulation each lasting simTime in duration.

    How it works:

    -> Check the next arrival time and the next departure timeToNextArrival
        -> If arrival is sooner
            -> Create a new job
            -> Assign the job
        -> If departure is sooner
            -> Handle the departure
        -> Update times
    -> At the end of repetition store all results for processing

    @return: none
    """
    def runSimulation(self):
        # Run the simution for numRepetitions reps
        for simNumber in range(0, self.numRepetitions):
            # print 'Iteration: ', simNumber+1
            # Sets a new seed for the iteration
            seed()
            # Ensure the variables that need to be reset are indeed reset
            self.resetVariablesForNewRepetition()
            # Can't have a departure yet nothing's happened. Arrival has to occur
            self.timeToNextArrival = self.generateNextArrival()
            self.avgNumJobsInSystem.append(0)
            # Outer loop for the simTime
            while (self.currentTime < self.simTime):
                # Base case of 0 jobs being in the system so far
                if (self.numJobsInSystem == 0):
                    self.updateAverageNumJobsInSystem(simNumber, self.currentTime, self.timeToNextArrival)
                    # Update time for arrival to occur
                    self.currentTime += self.timeToNextArrival
                    self.numArrivals += 1
                    # Add first job to random server
                    self.servers[self.getRandomServer()].addNewArrival(self.currentTime, self.generateNextProcessingTime(), self.generateNextJobMIPS())
                    self.numJobsInSystem += 1
                    # Next arrival time generated
                    self.timeToNextArrival = self.generateNextArrival()
                # Base case has passed, now checking for departure vs arrival times
                else:
                    serverWithNextDeparture = self.getServerWithNextDeparture()
                    self.timeToNextDeparture = self.servers[serverWithNextDeparture].getNextDepartureTime()
                    if (self.timeToNextArrival < self.timeToNextDeparture):
                        # Arrival Occurs
                        self.updateAverageNumJobsInSystem(simNumber, self.currentTime, self.timeToNextArrival)
                        # Update sim time
                        self.currentTime += self.timeToNextArrival
                        # Update server times
                        self.updateServerTimes(self.timeToNextArrival)
                        self.numArrivals += 1
                        # Assign the job
                        self.allocatedWithDynamicShutdowns(self.generateNextProcessingTime(), self.generateNextJobMIPS())
                        self.numJobsInSystem += 1
                        # Next arrival time generated
                        self.timeToNextArrival = self.generateNextArrival()
                    else:
                        # Departure Occurs
                        self.updateAverageNumJobsInSystem(simNumber, self.currentTime, self.timeToNextDeparture)
                        # Update sim time
                        self.currentTime += self.timeToNextDeparture
                        self.timeToNextArrival -= self.timeToNextDeparture
                        self.numDepartures += 1
                        self.numJobsInSystem -= 1
                        # Update server times
                        self.updateServerTimes(self.timeToNextDeparture)
                        # Handle departure of the job on the appropriate server
                        self.servers[serverWithNextDeparture].processNextDeparture(self.currentTime)
                self.avgJobsTracker.append(self.avgNumJobsInSystem[simNumber])
                self.timeTracker.append(self.currentTime)
            # ENDWHILE
            # Add all values to lists to be passed back to wrapper for processing
            throughputForRepetition = self.numDepartures / (float)(self.currentTime)
            self.throughput.append(throughputForRepetition)
            # Each list contains the server information for a single repetition.
            # Each of these lists is then appended to the simulator's instance list
            powerConsumptions = []
            serverUtilizations = []
            maxTemps = []
            responseTimes = []
            for server in self.servers:
                serverUtilizations.append(server.getAvgUtilization())
                powerConsumptions.append(server.getTotalEnergyConsumption())
                maxTemps.append(server.getMaxTemp())
                responseTimes.append(server.getAvgResponseTime())
            self.powerConsumedByServers.append(powerConsumptions)
            self.avgServerUtilizations.append(serverUtilizations)
            self.maxTempTracker.append(maxTemps)
            self.avgResponseTimes.append(responseTimes)
            # ENDFOR
        # ENDFOR

# UNUSED / LEGACY
# def getXAxis(self):
#     return self.timeTracker
#
# def getYAxis(self):
#     return self.avgJobsTracker
#
# def printState(self):
#     print '-------------------------------------------------------'
#     print 'TTNA\t', self.timeToNextArrival
#     ttnd = self.servers[self.getServerWithNextDeparture()].getNextDepartureTime()
#     print 'TTND\t', ttnd
#     print 'Current Time\t', self.currentTime
#     print 'Jobs in sys\t', self.numJobsInSystem
#     print 'Arrivals\t', self.numArrivals
#     print 'Departures\t', self.numDepartures
#     print 'Avg jobs in sim\t', self.avgNumJobsInSystem
#     for elem in self.servers:
#         elem.printServerState()
#     print '*******************************************************'
#     if (ttnd < self.timeToNextArrival):
#         print 'DEPART from: ', self.servers[self.getServerWithNextDeparture()].getServerID()
#     else:
#         print 'ARRIVAL to: ', self.servers[self.getShortestQueueLength()].getServerID()
#     raw_input('Next Iteration...')
