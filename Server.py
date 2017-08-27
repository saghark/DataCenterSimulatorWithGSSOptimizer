from Job import Job
from sys import maxint
from PowerModel import PowerModel
from HeatModel import HeatModel

class Server(object):

    # Class variable -> Keep track of number of instances / use that as ID
    _numInstances = 0
    # CPU capacity for MIPS -> used to determine utilization
    _processingPowerInMIPS = 2500000

"""
__init__

Initialize a server based on input parameters and default values as necessary

@return: none
"""
    def __init__(self):
        super(Server, self).__init__()
        # Queue used to track the job processing times
        self.queue = []
        # List used to track the jobs finished
        self.jobsFinished = []
        # List used to track the utilization history of the server
        self.utilizationHistory = []
        # Instance ID
        self.serverID = Server._numInstances
        # Server status
        self.isBusy = False
        # Server on/off
        self.isTurnedOn = False
        self.util = 0.0
        self.energyConsumed = 0.0
        # Initialize the power model associated with the server
        self.powerModel = PowerModel()
        # Initialize the heat model associated with the server
        self.heatModel = HeatModel()
        # Using the number of jobs as the moving average tracker for the utilization
        self.numJobsProcessed = 0
        self.maxTemp = 0.0
        # Update the number of instances of the Server class
        Server._numInstances += 1

# Getters

"""
getAvgUtilization

@return: the average utilization of the server based on the utilization history
"""
    def getAvgUtilization(self):
        if self.numJobsProcessed > 0:
            return round(sum(self.utilizationHistory) / self.numJobsProcessed, 2)
        else:
            return 0.0

"""
getAvgResponseTime

Determines the average response time of all jobs completed by the server. If the
server finished no jobs (i.e. was off) then return default value - 0

@return: average respones time of all completed jobs
"""
    def getAvgResponseTime(self):
        if len(self.jobsFinished) > 0:
            numJobsFinished = 0
            sumTimes = 0
            for job in self.jobsFinished:
                if job.getIsFinished():
                    sumTimes += job.getResponseTime()
                    numJobsFinished += 1
            return sumTimes / numJobsFinished
        return 0

"""
getInstantUtil

@return: the instantaneous utiliazation of the server
"""
    def getInstantUtil(self):
        return self.util

"""
getIsServerOn

@return: boolean server on or off
"""
    def getIsServerOn(self):
        return self.isTurnedOn

"""
getServerID

@return: instance number for the object
"""
    def getServerID(self):
        return self.serverID

"""
getQueueLength

@return: length of the job queue for the server
"""
    def getQueueLength(self):
        return len(self.queue)

"""
getNextDepartureTime

@return: time of the next departure from the server based on the job queue
"""
    def getNextDepartureTime(self):
        if (len(self.queue) > 0):
            return self.queue[0].getProcessingTime()
        return maxint

"""
getIsBusy

@return: whether the server is working on a job or not - boolean True/False
"""
    def getIsBusy(self):
        return self.isBusy

"""
getTotalEnergyConsumption

@return: energy consumed by the server up to the point of calling this method
"""
    def getTotalEnergyConsumption(self):
        return round(self.energyConsumed, 2)

"""
getMaxTemp

@return: maximum temperature reached by the server thus far
"""
    def getMaxTemp(self):
        return round(self.maxTemp, 2)

# Setter
"""
setIsServerOn

Set the power state of the server (turned on or off).

@param isOn: True if want server to be on False if want server to be off
"""
    def setIsServerOn(self, isOn):
        self.isTurnedOn = isOn

# Functionality methods

"""
processNextDeparture

Process the next departure from the queue of jobs as long as there as jobs within the queue.
Add the departing job to the list of jobs finished. Update the utilization history as well.
If the queue is empty after the job departs then the server will shut down.

@return: none
"""

    def processNextDeparture(self, endTime):
        if (len(self.queue) > 0):
            self.queue[0].setIsFinished(True)
            self.queue[0].setEndTime(endTime)
            self.jobsFinished.append(self.queue.pop(0))
            self.utilizationHistory.append(self.util)
            self.numJobsProcessed += 1
        if (len(self.queue) == 0):
            # print 'Server ', self.serverID, ' turning off...'
            self.util = 0.0
            self.isBusy = False
            self.isTurnedOn = False

"""
addNewArrival

Adds a new job to the server's job queue. Sets the server status to being busy

@return: none
"""
    def addNewArrival(self, simTime, processingTime, mips):
        if (processingTime > 0):
            newJob = Job(simTime, processingTime, mips)
            self.queue.append(newJob)
            self.isBusy = True

# Update methods
"""
updateServerUtil

Updates the server's current utilization based on the maximum processing power
available to server and the processing requirements of the current job

@return: none
"""
    def updateServerUtil(self):
        self.util = self.queue[0].getMIPS() / Server._processingPowerInMIPS

"""
updateMaxTemp

Updates the maximum temperature of the server if the current temperature exceeds
the previous maximum temperature

@return: none
"""
    def updateMaxTemp(self):
        currTemp = self.heatModel.getCurrTemp(self.util)
        if (self.maxTemp < currTemp):
            self.maxTemp = currTemp

"""
updateProcessingTimes

Updates the processing time of the current job being worked on. Also calls to update
the utilization, temperature, and power consumption of the servers.

@return: none 
"""
    def updateProcessingTimes(self, elapsedTime):
        if (len(self.queue) > 0):
            updatedProcessingTime = self.queue[0].getProcessingTime() - elapsedTime
            self.queue[0].setProcessingTime(updatedProcessingTime)
            self.updateServerUtil()
            self.updateMaxTemp()
            self.energyConsumed += self.powerModel.getPowerConsumed(self.util, elapsedTime)

# UNUSED / DEPRACATED
# def printServerState(self):
#     print 'ServerID: ', self.serverID, ' - queue length ', len(self.queue), ' jobs:'
#     print self.queue
