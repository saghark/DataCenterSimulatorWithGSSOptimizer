

class HeatModel(object):
    # Idle power consumption in watts
    __idleTemp = 40
    # Linear power consumption with respect to Utilization
    __linearTemp = 40
    # Total max consumption = idle + linear
    # i.e. __maxConsume = __idleConsume + __linearConsume
    def __init__(self):
        super(HeatModel, self).__init__()

    """
    getPowerConsumed

    @param util: utilization to calculate temperature for
    @return: instantaneous temperature based on utilization
    """
    def getCurrTemp(self, util):
        return HeatModel.__idleTemp + util * HeatModel.__linearTemp
