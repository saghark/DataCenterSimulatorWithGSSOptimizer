from sys import maxint

class Job(object):
"""
__init__

Initializer for a job instance

@param startTime: Time at which the job entered the simulation
@param processingTime: Processing time the job requires -> 0 if unspecified and to be set later
@param mips: MIPS the jobs requires -> 0 if unspecified and to be set later
"""
    def __init__(self, startTime, processingTime=0, mips=0):
        super(Job, self).__init__()
        self.startTime = startTime
        self.endTime = maxint
        self.processingTime = processingTime
        self.requiredMIPS = mips
        self.isFinished = False

# Getters

"""
getResponseTime

@return: response time for the job
"""
    def getResponseTime(self):
        return self.endTime - self.startTime

"""
getProcessingTime

@return: processing time for the job
"""
    def getProcessingTime(self):
        return self.processingTime

"""
getMIPS

@return: MIPS required for the job
"""
    def getMIPS(self):
        return self.requiredMIPS


"""
getIsFinished

@return: boolean determining if the job has been finished or not
"""
    def getIsFinished(self):
        return self.isFinished

# Setters

"""
setEndTime

@param endTime: set the time at which the job ended
@return: none
"""
    def setEndTime(self, endTime):
        self.endTime = endTime

"""
setProcessingTime

@param procTime: set the processing time the job requires
@return: none
"""
    def setProcessingTime(self, procTime):
        self.processingTime = procTime

"""
setMIPS

@param mips: MIPS required for the job
@return: none
"""
    def setMIPS(self, mips):
        self.requiredMIPS = mips

"""
setIsFinished

@param status: boolean T/F whether the job has been finished or not
@return: none 
"""
    def setIsFinished(self, status):
        self.isFinished = status
