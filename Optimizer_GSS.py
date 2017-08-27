# Import the simulation package
from Simulator import Simulator
# Import the necessary mathematical functions
from math import sqrt, exp, ceil, floor
# Import the necessary system value
from sys import maxint
############################<<PARAMS>>############################
# Params: Simulator -> Set by user
mu                = 1
simTime           = 100
accuracy          = 4
numServers        = 25
numRepsSim        = 5
desiredUtil       = 0.55
aggressivness     = 0.15
maxMIPS           = 2500000
# Params: Optimization Maximum Values -> Set by updateServerUtil
maxResponseTime   = 5.0
maxUtilization    = 1.0
maxTemperature    = 70
# Params: Simulator -> Calculated
lam               = desiredUtil * numServers
#       Phi -> DO NOT CHANGE -- This is a specific value used by the GSS!
phi               = ( -1.0 + sqrt(5) ) / 2
util              = lam / (float)(mu * numServers)
# Params: GSS
alphaMin          = 1
alphaMax          = numServers
tolerance         = 2
numRepsGSS        = 100
##################################################################

"""
penaltyFunction

This function aims to take in a set of parameters, run a DES simulation, and return the calculated penalty score of the simulation output based on the given inputs.

@param lamb: the interarrival rate for the simulator
@param mu: the job size parameter for the simulator
@param numServers: number of servers that the simulator will contain
@param simTime: the number of time units the simulator is alloted to run for
@param numReps: number of repetitions the simulator will run for
@param maxMIPS: the maximum number of millions of instructions per second (MIPS) that a job can reach
@param aggressivness: the aggressivness parameter determines the number of servers that are initially turned on within the simulator
@return: the total penalty score of the simulation results
"""
def penaltyFunction(lamb, mu, numServers, simTime, numReps, maxMIPS, aggressivness):
    mySim = Simulator(lam, mu, numServers, simTime, numRepsSim, maxMIPS, aggressivness)
    mySim.runSimulation()
    totalPenalty = 0

    maxTemps                = mySim.getMaxTemps()
    responseTimes           = mySim.getAvgResponseTime()
    avgjobsinsys            = mySim.getAvgJobsInSimulation()
    avgUtilizations         = mySim.getAvgServerUtils()
    powerConsumedByServers  = mySim.getPowerConsumptions()

    for rep in powerConsumedByServers:
        repIndex = powerConsumedByServers.index(rep)

        print '*****************************************************'
        print 'Log dump for rep', repIndex+1
        print 'Avg avg utils: ', sum(avgUtilizations[repIndex]) / len(avgUtilizations[repIndex])
        print 'Avg power consumed', sum(powerConsumedByServers[repIndex]) / len(powerConsumedByServers[repIndex])
        print 'Avg Response Time', sum(responseTimes[repIndex]) / len(responseTimes[repIndex])
        for i in range(0, len(rep)):
            print 'Server', i, '\tUtil:', avgUtilizations[repIndex][i], '\tMax temp:', maxTemps[repIndex][i],  '\t\tConsumed:', powerConsumedByServers[repIndex][i], '\tRT:', responseTimes[repIndex][i]

        maxTempForRep      = max(maxTemps[repIndex])
        maxPowerConsForRep = max(powerConsumedByServers[repIndex])
        maxUtilForRep      = max(avgUtilizations[repIndex])
        maxRTForRep        = max(responseTimes[repIndex])

        # Huge penalties for infeasible solutions
        if maxTempForRep > maxTemperature:
            totalPenalty += maxTempForRep
        if maxUtilForRep > maxUtilization:
            totalPenalty += maxUtilForRep
        if maxRTForRep > maxResponseTime:
            totalPenalty += maxRTForRep

        # Calculate norms against the maximums for each list
        # No actual use for this, penalties wouldn't make sense since the normalized scores can only be compared relative to the max...
        # normMaxTemps        = [float(i)/maxTempForRep for i in maxTemps[repIndex]].sort(reverse=True)
        # normPowerConsumed   = [float(i)/maxPowerConsForRep for i in powerConsumedByServers[repIndex]].sort(reverse=True)
        # normAvgUtils        = [float(i)/maxUtilForRep for i in avgUtilizations[repIndex]].sort(reverse=True)
        # normResponseTimes   = [float(i)/maxRTForRep for i in responseTimes[repIndex]].sort(reverse=True)

        avgMaxTempForRep    = sum(maxTemps[repIndex]) / len(maxTemps[repIndex])
        avgPowerConsForRep  = sum(powerConsumedByServers[repIndex]) / len(powerConsumedByServers[repIndex])
        avgUtilForRep       = sum(avgUtilizations[repIndex]) / len(avgUtilizations[repIndex])
        avgRTForRep         = sum(responseTimes[repIndex]) / len(responseTimes[repIndex])

        for item in rep:
            itemIndex = rep.index(item)
            if maxTemps[repIndex][itemIndex] > avgMaxTempForRep:
                totalPenalty += maxTemps[repIndex][itemIndex] - avgMaxTempForRep
            if powerConsumedByServers[repIndex][itemIndex] > avgPowerConsForRep:
                totalPenalty += powerConsumedByServers[repIndex][itemIndex] - avgPowerConsForRep
            if avgUtilizations[repIndex][itemIndex] > avgUtilForRep:
                totalPenalty += avgUtilizations[repIndex][itemIndex] - avgUtilForRep
            if responseTimes[repIndex][itemIndex] > avgRTForRep:
                totalPenalty += responseTimes[repIndex][itemIndex] - avgRTForRep
        # ENDFOR
    return totalPenalty


"""
optimizerGSS

the optimizerGSS used the golden section search to optimize the number of servers required a given workload based on the simulation penalty scores that are determined each iteration. Convergence occurs when the results are within some tolerance.
@param alphaMin: the lowerbound of the search space
@param alphaMax: the upperbound of the search space
@param tolerance: the acceptable tolerance to terminate the search and declare success
@param numReps: the number of iterations that the search can occur for at maximum
@param numServers: the maximum number of servers allowable

@return: none -- prints results in console or whever the results are piped to
"""
def optimizerGSS(alphaMin, alphaMax, tolerance, numReps, numServers):
    print " x1\t x2\t    fx1\t\t   fx2\t\t b-a"
    x1 = floor(phi*alphaMin + (1-phi)*alphaMax)
    x2 = ceil((1-phi)*alphaMin + phi*alphaMax)
    fx1 = penaltyFunction(lam, mu, numServers, simTime, numRepsSim, maxMIPS, x1)
    fx2 = penaltyFunction(lam, mu, numServers, simTime, numRepsSim, maxMIPS, x2)
    numIters = 1
    lastDiff = maxint
    for i in range(1, numReps):
        print "%.2f\t%.2f\t%.2f\t%.2f\t%.2f" % (x1, x2, fx1, fx2, alphaMax-alphaMin)
        # Search space is now in the lower two thirds of the previous iteration
        if fx1 < fx2:
            alphaMax = x2
            x2 = x1
            fx2 = fx1
            x1 = floor(phi*alphaMin + (1-phi)*alphaMax)
            fx1 = penaltyFunction(lam, mu, numServers, simTime, numRepsSim, maxMIPS, x1)
        # Search space is now in the upper two thirds of the previous iteration
        else:
            alphaMin = x1
            x1 = x2
            fx1 = fx2
            x2 = ceil((1-phi)*alphaMin + phi*alphaMax)
            fx2 = penaltyFunction(lam, mu, numServers, simTime, numRepsSim, maxMIPS, x2)
        numIters = numIters + 1
        currDiff = abs(alphaMax - alphaMin)
        # Check for convergence
        if abs(alphaMax - alphaMin) <= tolerance:
            # Converged! Can terminate and print results
            print '\n----------FINAL DUMP-----------'
            print ' x1 =', x1
            print 'fx1 =', fx1
            print ' x2 =', x2
            print 'fx2 =', fx2
            print '  a =',alphaMin
            print '  b =',alphaMax
            print 'Converged after', numIters, 'iterations...'
            print '--------------------------------\n'
            return
        lastDiff = currDiff
        # Endif
    # Endfor
    # No convergence occured after the maximum number of allowed iterations
    print '\n----------FINAL DUMP-----------'
    print ' x1 =', x1
    print 'fx1 =', fx1
    print ' x2 =', x2
    print 'fx2 =', fx2
    print '  a =',alphaMin
    print '  b =',alphaMax
    print 'NO convergence after', numIters, 'iterations...'
    print '--------------------------------\n'
# End function

optimizerGSS(alphaMin, alphaMax, tolerance, numRepsGSS, numServers)
