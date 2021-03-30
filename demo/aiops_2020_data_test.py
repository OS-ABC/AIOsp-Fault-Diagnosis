import json

from service.fault_diagnosis_service import fault_diagmosis
from utils.data_tools import is_number


def data_collection_process_json():
    """
        从json中获取原始调用链数据、部署数据、原始指标数据、原始日志数据、异常指标数据和异常日志数据
        Args:

        Returns: 返回对应的从json中获取到的数据
    """

    # 获取未处理的异常数据
    f = open('../data/aiops_data_2020/2020_04_11/items_exception_result.json', 'r')
    original_exception_metric_data = json.load(f)
    exception_metric_data = original_exception_metric_data
    f.close()

    f = open('../data/aiops_data_2020/2020_04_11/origina_items.json', 'r')
    original_items = json.load(f)
    items = original_items
    f.close()

    f = open('../data/aiops_data_2020/2020_04_11/origina_traces.json', 'r')
    original_traces = json.load(f)
    traces = {}
    for i, (k, v) in enumerate(original_traces.items()):
        if i <= 500:
            traces[k] = v
        else:
            break
    f.close()

    f = open('../data/aiops_data_2020/2020_04_11/original_deployment_data.json', 'r')
    deployment_data = json.load(f)
    f.close()
    return exception_metric_data, items, traces, deployment_data

def get_original_trace_data(traces):
    """
    将traces处理成目标输入数据：每条记录包括id、pid、serviceId、serviceName、serviceType、startTime、traceId等字段
    aiops_2020处理的traces是将traces组织在一起的
    :param traces:
    :return:目标格式的List
    """
    traceData = list()
    for traceId, trace in traces.items():
        for index, span in enumerate(trace):
            if span['pid'] == 'None':
                span['pid'] = -1
            tmp_dict = {}
            tmp_dict['id'] = span['id']
            tmp_dict['pid'] = span['pid']
            tmp_dict['serviceId'] = span['serviceId']  # serviceCode并不能唯一标识服务实例，需要再讨论
            tmp_dict['serviceName'] = span['serviceName']
            tmp_dict['serviceType'] = span['serviceType']
            tmp_dict['startTime'] = span['startTime']
            tmp_dict['traceId'] = traceId
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
    for key,metrics in items.items():
        metricId = metrics['metricId']
        metricName = metrics['metricId']
        units = None
        metricBelongTo = metrics['metricBelongTo']
        metricBelongLevel = metrics['metricBelongLevel']
        stampTimes = metrics['timeStamps']
        values = metrics['values']
        if len(stampTimes) > 0 and len(stampTimes) == len(values):
            for index, value in enumerate(stampTimes):
                tmp_metric = dict()
                tmp_metric['metricId'] = str(metricId)
                tmp_metric['metricName'] = metricName
                tmp_metric['metricBelongTo'] = metricBelongTo
                tmp_metric['metricBelongLevel'] = metricBelongLevel
                tmp_metric['units'] = units
                tmp_metric['timestamp'] = value
                if is_number(values[index]):
                    tmp_metric['value'] = float(values[index])
                    originalMetricData.append(tmp_metric)
        else:
            continue
    return originalMetricData

def get_exception_metric_data(exception_metric_data):
    """
    将异常指标数据处理成输入数据：每条记录包含startTime、endTime、metricId、metricName、value、units、metricBelongTo、metricBelongLevel等字段
    :param exception_metric_data:
    :return:目标格式List
    """
    exceptionMetricData = list()

    for ex_metric in exception_metric_data:
        metricId = ex_metric['metricId']
        metricName = ex_metric['metricName']
        units = None
        metricBelongTo = ex_metric['belongTo']
        metricBelongLevel = None
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

if __name__ == '__main__':
    exception_metric_data, items, traces, deployment_data = data_collection_process_json()

    deploymentData = get_deployment_data(deployment_data)
    traceData = get_original_trace_data(traces)
    original_metricData = get_original_metric_data(items)
    exception_metricData = get_exception_metric_data(exception_metric_data)
    exception_logData = []
    original_logData = []
    fault_diagmosis(deploymentData, traceData, original_metricData, original_logData, exception_metricData,
                    exception_logData)
    pass
