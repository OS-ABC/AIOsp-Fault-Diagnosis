class DeploymentDataEntry:
    def __init__(self, serviceInstanceId:str, serviceName: str, hostId: str = None,hostName:str = None,containerId:str =None,containerName:str= None):
        self.serviceInstanceId = serviceInstanceId
        self.serviceName = serviceName
        self.hostId = hostId
        self.hostName = hostName
        self.containerId = containerId
        self.containerName = containerName

class TraceDataEntry:
    def __init__(self, id:str, pid: str, serviceId: str,traceId:str,serviceName:str = None,serviceType:str =None,startTime:str= None):
        self.id = id
        self.pid = pid
        self.serviceId = serviceId
        self.serviceName = serviceName
        self.serviceType = serviceType
        self.startTime = startTime
        self.traceId = traceId

class OriginalMetricEntry:
    def __init__(self, metricId:str, metricName: str, timestamp:str, value: float, metricBelongTo:str, units:str = None,metricBelongLevel:str= None):
        self.metricId = metricId
        self.metricName = metricName
        self.timestamp = timestamp
        self.value = value
        self.units = units
        self.metricBelongTo = metricBelongTo
        self.metricBelongLevel = metricBelongLevel

class OriginalLogEntry:
    def __init__(self, logId:str, timestamp:str, logMessage: str, logBelongTo:str, logLevel: str = None, logBelongLevel:str= None):
        self.logId = logId
        self.timestamp = timestamp
        self.logMessage = logMessage
        self.logLevel = logLevel
        self.logBelongTo = logBelongTo
        self.logBelongLevel = logBelongLevel

class ExceptionMetricEntry:
    def __init__(self, startTime:str, endTime:str, metricId: str, metricName:str, value: float, metricBelongTo:str, units:str = None,metricBelongLevel:str= None):
        self.startTime = startTime
        self.endTime = endTime
        self.metricId = metricId
        self.metricName = metricName
        self.value = value
        self.metricBelongTo = metricBelongTo
        self.units = units
        self.metricBelongLevel = metricBelongLevel

class ExceptionLogEntry:
    def __init__(self, startTime:str, endTime:str, logId: str, logBelongTo:str, logExceptionSegment: str, logBelongLevel:str= None):
        self.startTime = startTime
        self.endTime = endTime
        self.logId = logId
        self.logExceptionSegment = logExceptionSegment
        self.logBelongTo = logBelongTo
        self.logBelongLevel = logBelongLevel