import json

from service.fault_diagnosis_service import fault_diagmosis
from utils.data_tools import is_number, utc_to_local


def data_collection_process_json():
    """
        从json中获取原始调用链数据、部署数据、原始指标数据、原始日志数据、异常指标数据和异常日志数据
        Args:

        Returns: 返回对应的从json中获取到的数据
    """

    #获取异常指标数据
    f = open('../data/hadoop_data/exception_data/result-infi.json', 'r')
    original_exception_metric_data = json.load(f)
    exception_metric_data = original_exception_metric_data['3EUz83cBglWMAhILSC5I']
    #获取日志指标数据
    f = open('../data/hadoop_data/exception_data/result_log-infi.json', 'r')
    original_exception_log_data = json.load(f)
    exception_log_data = original_exception_log_data['3EUz83cBglWMAhILSC5I']
    #获取原始指标、调用链、日志数据
    f = open('../data/hadoop_data/3EUz83cBglWMAhILSC5I.json', 'r')
    original_data = json.load(f)
    items = original_data[0]['_source']['items']
    traces = original_data[0]['_source']['traces']
    logs = original_data[0]['_source']['logs']
    #获取原始部署数据
    f = open('../data/hadoop_data/deployment_info.json', 'r')
    deployment_data = json.load(f)
    return exception_metric_data,exception_log_data,original_data,items,traces,logs,deployment_data

def get_original_trace_data(traces):
    """
    将traces处理成目标输入数据：每条记录包括id、pid、serviceId、serviceName、serviceType、startTime、traceId等字段
    hadoop的traces是将traces组织在一起的
    :param traces:
    :return:目标格式的List
    """
    traceData = list()
    for trace in traces:
        i_dict = json.loads(trace)
        for index, span in enumerate(i_dict['data']['trace']['spans']):
            if span['parentSpanId'] != -1: continue
            else:
                if len(span['refs'])== 0:
                    tmp_dict = {}
                    tmp_dict['id'] = span['segmentId']
                    tmp_dict['pid'] = -1
                    tmp_dict['serviceId'] = span['serviceCode']#serviceCode并不能唯一标识服务实例，需要再讨论
                    tmp_dict['serviceName'] = span['serviceCode']
                    tmp_dict['serviceType'] = span['type']
                    tmp_dict['startTime'] = span['startTime']
                    tmp_dict['traceId'] = span['traceId']
                    traceData.append(tmp_dict)
                else:
                    for k in span['refs']:
                        tmp_dict = {}
                        tmp_dict['id'] = span['segmentId']
                        tmp_dict['pid'] = k['parentSegmentId']
                        tmp_dict['serviceId'] = span['serviceCode']  # serviceCode并不能唯一标识服务实例，需要再讨论
                        tmp_dict['serviceName'] = span['serviceCode']
                        tmp_dict['serviceType'] = span['type']
                        tmp_dict['startTime'] = span['startTime']
                        tmp_dict['traceId'] = span['traceId']
                        traceData.append(tmp_dict)
    return traceData

def get_deployment_data(deployment_data):
    """
    将部署数据处理成目标输入数据：每条记录包含serviceInstanceId、serviceName、hostId、hostName、containerId、containerName等字段
    :param deployment_data:
    :return:目标格式List
    """
    return deployment_data

def get_original_metric_data(items):
    """
    将原始指标数据处理成目标输入数据：每条记录包含timestamp、metricId、metricName、value、units、metricBelongTo、metricBelongLevel
    :param items:
    :return:目标格式List
    """
    originalMetricData = list()
    for item_str in items:
        item = json.loads(item_str)
        metricId = item['id']
        metricName = item['name']
        units = item['units']
        applicationName = item['applicationName']
        metricBelongTo = None
        metricBelongLevel = None
        if applicationName == "Zabbix server":
            continue
        else:
            if applicationName is None:
                continue
            elif applicationName.startswith('Hadoop'):
                if applicationName == "Hadoop":
                    name_split = metricName.split(':')
                    metricBelongTo = name_split[0]
                    metricBelongLevel = "service"
                else:
                    applicationName_split = applicationName.split()
                    metricBelongTo = applicationName_split[1]
                    metricBelongLevel = "service"
            elif applicationName.startswith('Docker'):
                if applicationName == "Docker":
                    continue
                else:
                    applicationName_split = applicationName.split()
                    metricBelongTo = applicationName_split[2][1:]
                    metricBelongLevel = "docker"
            else:
                metricBelongTo = item['hostName']
                metricBelongLevel = "host"
        stampTimes = item['allClock']
        values = item['allValue']
        stampTimes_splits = stampTimes.strip().split(',')
        values_splits = values.strip().split(',')
        if len(stampTimes_splits) > 0 and len(stampTimes_splits) == len(values_splits):
            for index,value in enumerate(stampTimes_splits):
                tmp_metric = dict()
                tmp_metric['metricId'] =  str(metricId)
                tmp_metric['metricName'] = metricName
                tmp_metric['metricBelongTo'] = metricBelongTo
                tmp_metric['metricBelongLevel'] = metricBelongLevel
                tmp_metric['units'] = units
                tmp_metric['timestamp'] = value
                if is_number(values_splits[index]):
                    tmp_metric['value'] = float(values_splits[index])
                    originalMetricData.append(tmp_metric)
        else:
            continue
    return originalMetricData

def get_original_log_data(logs):
    """
    将原始日志数据处理成目标输入数据：每条记录包含timestamp、logId、logMessage、logLevel、logBelongTo、logBelongLevel等字段
    :param logs:
    :return:目标格式List
    """
    originalLogData = list()
    for key, logList in logs.items():
        if len(logList) == 0:
            continue
        logId = key
        for log_str in logList:
            log = json.loads(log_str)
            tmp_log = dict()
            tmp_log['logId'] = logId
            if logId == "stderr":
                tmp_log['logLevel'] = None
                tmp_log['logMessage'] = log['message']
                log_time = log['@timestamp']
                log_time = utc_to_local(log_time)
                tmp_log['timestamp'] = log_time
            else:
                if "level" in log:
                    tmp_log['logLevel'] = log['level']
                else:
                    tmp_log['logLevel'] = None
                tmp_log['logMessage'] = log['log_message']
                log_time = log['log_time']
                log_time = utc_to_local(log_time)
                tmp_log['timestamp'] = log_time
            if logId.startswith('hadoop'):
                logId_splits = logId.strip().split('-')
                logBelongTo = logId_splits[2]
                tmp_log['logBelongLevel'] = "service"
                if logBelongTo == "datanode":
                    tmp_log['logBelongTo'] = "DataNode"
                elif logBelongTo == "namenode":
                    tmp_log['logBelongTo'] = "NameNode"
                elif logBelongTo == "nodemanager":
                    tmp_log['logBelongTo'] = "NodeManager"
                elif logBelongTo == "resourcemanager":
                    tmp_log['logBelongTo'] = "ResourceManager"
                elif logBelongTo == "secondarynamenode":
                    tmp_log['logBelongTo'] = "SecondaryNameNode"
            else:
                tmp_log['logBelongTo'] = log['host']['name']
                tmp_log['logBelongLevel'] = "host"
            originalLogData.append(tmp_log)
    return originalLogData

def get_exception_metric_data(exception_metric_data):
    """
    将异常指标数据处理成输入数据：每条记录包含startTime、endTime、metricId、metricName、value、units、metricBelongTo、metricBelongLevel等字段
    :param exception_metric_data:
    :return:目标格式List
    """
    exceptionMetricData = list()
    for ex_metric in exception_metric_data:
        tmp_dict = dict()
        metricId = ex_metric['metricId']
        metricName = ex_metric['metricName']
        units = None
        metricBelongTo = None
        metricBelongLevel = None
        applicationName = ex_metric['belongTo']
        if applicationName == "Zabbix server":
            continue
        else:
            if applicationName is None:
                continue
            elif applicationName.startswith('Hadoop'):
                if applicationName == "Hadoop":
                    name_split = metricName.split(':')
                    metricBelongTo = name_split[0]
                    metricBelongLevel = "service"
                else:
                    applicationName_split = applicationName.split()
                    metricBelongTo = applicationName_split[1]
                    metricBelongLevel = "service"
            elif applicationName.startswith('Docker'):
                if applicationName == "Docker":
                    continue
                else:
                    applicationName_split = applicationName.split()
                    metricBelongTo = applicationName_split[2][1:]
                    metricBelongLevel = "docker"
            else:
                # metricBelongTo = ex_metric['hostName']
                metricBelongTo = "fuguangbo-0002"
                metricBelongLevel = "host"
        stampTimes = ex_metric['testTime']
        values = ex_metric['value']
        stampTimes_splits = stampTimes.strip().split(',')
        values_splits = values.strip().split(',')
        if len(stampTimes_splits) > 0 and len(stampTimes_splits) == len(values_splits):
            for index, value in enumerate(stampTimes_splits):
                tmp_metric = dict()
                tmp_metric['metricId'] = str(metricId)
                tmp_metric['metricName'] = metricName
                tmp_metric['metricBelongTo'] = metricBelongTo
                tmp_metric['metricBelongLevel'] = metricBelongLevel
                tmp_metric['units'] = units
                tmp_metric['endTime'] = value
                tmp_metric['startTime'] = value
                if is_number(values_splits[index]):
                    tmp_metric['value'] = float(values_splits[index])
                    exceptionMetricData.append(tmp_metric)
        else:
            continue
    return exceptionMetricData

def get_exception_log_data(exception_log_data):
    """
    将异常日志数据处理成目标输入数据：每条记录包含startTime、endTime、logId、logExceptionSegment、logBelongLevel、logBelongTo等字段
    :param exception_log_data:
    :return: 目标格式List
    """
    exceptionLogData = list()
    for logSegment in exception_log_data:
        tmp_log = dict()
        startTime = logSegment['testTime']
        endTime = logSegment['testTime']
        logId = logSegment['logId'].strip().split(':')[0]
        logExceptionSegment = logSegment['logDetail']
        if logId.startswith('hadoop'):
            logId_splits = logId.strip().split('-')
            logBelongTo = logId_splits[2]
            tmp_log['logBelongLevel'] = "service"
            if logBelongTo == "datanode":
                tmp_log['logBelongTo'] = "DataNode"
            elif logBelongTo == "namenode":
                tmp_log['logBelongTo'] = "NameNode"
            elif logBelongTo == "nodemanager":
                tmp_log['logBelongTo'] = "NodeManager"
            elif logBelongTo == "resourcemanager":
                tmp_log['logBelongTo'] = "ResourceManager"
            elif logBelongTo == "secondarynamenode":
                tmp_log['logBelongTo'] = "SecondaryNameNode"
        else:
            tmp_log['logBelongTo'] = logSegment["belongTo"].strip().split(':')[0]
            tmp_log['logBelongLevel'] = "host"
        tmp_log['startTime'] = startTime
        tmp_log['endTime'] = endTime
        tmp_log['logId'] = logId
        tmp_log['logExceptionSegment'] = logExceptionSegment
        exceptionLogData.append(tmp_log)
    return exceptionLogData

if __name__ == '__main__':
    exception_metric_data, exception_log_data, original_data, items, traces, logs, deployment_data = data_collection_process_json()
    deploymentData = get_deployment_data(deployment_data)
    traceData = get_original_trace_data(traces)
    original_metricData = get_original_metric_data(items)
    original_logData = get_original_log_data(logs)
    exception_metricData = get_exception_metric_data(exception_metric_data)
    exception_logData = get_exception_log_data(exception_log_data)
    fault_diagmosis(deploymentData, traceData, original_metricData, original_logData, exception_metricData,
                    exception_logData)
    pass