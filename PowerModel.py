

class PowerModel(object):
    # Idle power consumption in watts
    __idleConsume = 100
    # Linear power consumption with respect to Utilization
    __linearConsume = 100
    # Total max consumption = idle + linear
    # i.e. __maxConsume = __idleConsume + __linearConsume
    # Source:
    # https://software.intel.com/sites/default/files/m/d/4/1/d/8/power_consumption.pdf
    def __init__(self):
        super(PowerModel, self).__init__()


"""
getPowerConsumed

@param util: utilization to calculate consumption for
@param timeElapsed: duration of consumption
@return: the power consumption based on the utilization over the elapsed time
"""
    def getPowerConsumed(self, util, timeElapsed):
        powerAtUtil = PowerModel.__idleConsume + PowerModel.__linearConsume * util
        return timeElapsed * powerAtUtil
