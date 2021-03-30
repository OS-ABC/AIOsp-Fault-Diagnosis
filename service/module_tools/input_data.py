import json
from typing import List

from bean.input_model import DeploymentDataEntry, TraceDataEntry, OriginalMetricEntry, OriginalLogEntry, \
    ExceptionMetricEntry, ExceptionLogEntry
import pandas as pd


class InputData:
    def __init__(self, deploymentData: List, traceData: List, original_metricData: List, original_logData: List,
                 exception_metricData: List, exception_logData: List):
        self.deploymentObjData = deploymentData_to_obj(deploymentData)
        self.traceObjData = traceData_to_obj(traceData)
        self.original_metricObjData = originalMetricData_to_obj(original_metricData)
        self.original_logObjData = originalLogData_to_obj(original_logData)
        self.exception_metricObjData = exceptionMetricData_to_obj(exception_metricData)
        self.exception_logObjData = exceptionLogData_to_obj(exception_logData)

        # self.traceObjData_by_traceId = None
        # self.deploymentObjData_by_sviid = None
        # self.original_metricObjData_by_metricId = None
        # self.original_logObjData_by_logId = None
        #
        # self.exception_metricObjData_by_metricBelongTo = None
        # self.exception_logObjData_by_logBelongTo = None

    def organization_deploymentObjData_by_sviid(self):
        """
        组织部署数据dict,key为serviceInstanceId
        :param deploymentObjData:
        :return: 以serviceInstanceId为key的dict
        """
        # if deploymentObjData_by_sviid is not None: return self.deploymentObjData_by_sviid
        deploymentObjData_by_sviid = {}
        for i in self.deploymentObjData:
            deploymentObjData_by_sviid[i.serviceInstanceId] = i
        return deploymentObjData_by_sviid

    def organization_traceObjData_by_traceId(self):
        """
        组织调用链数据dict,key为straceId
        :param traceObjData:
        :return: 以traceId为key的dict
        """
        # if self.traceObjData_by_traceId is not None: return self.traceObjData_by_traceId
        traceObjData_by_traceId = {}
        for i in self.traceObjData:
            if i.traceId not in traceObjData_by_traceId:
                traceObjData_by_traceId[i.traceId] = []
                traceObjData_by_traceId[i.traceId].append(i)
            else:
                traceObjData_by_traceId[i.traceId].append(i)
        return traceObjData_by_traceId

    def organization_original_metricObjData_by_metricId(self):
        """
        组织原始指标数据dict,key为metricId
        :param original_metricObjData:
        :return:以metricId为key的dict
        """
        # if self.original_metricObjData_by_metricId is not None: return self.original_metricObjData_by_metricId
        original_metricObjData_by_metricId = {}
        for i in self.original_metricObjData:
            if i.metricId not in original_metricObjData_by_metricId:
                original_metricObjData_by_metricId[i.metricId] = []
                original_metricObjData_by_metricId[i.metricId].append(i)
            else:
                original_metricObjData_by_metricId[i.metricId].append(i)
        return original_metricObjData_by_metricId

    def organization_original_logObjData_by_logId(self):
        """
        组织原始指标数据dict,key为logId
        :param original_logObjData:
        :return: 以logId为key的dict
        """
        # if self.original_logObjData_by_logId is not None: return self.original_logObjData_by_logId
        original_logObjData_by_logId = {}
        for i in self.original_logObjData:
            if i.logId not in original_logObjData_by_logId:
                original_logObjData_by_logId[i.logId] = []
                original_logObjData_by_logId[i.logId].append(i)
            else:
                original_logObjData_by_logId[i.logId].append(i)
        return original_logObjData_by_logId

    def get_target_exception_metric_data(self, exception_metricObjData):
        pass

    def get_target_exception_log_data(self, exception_logObjData):
        pass

    def organization_exception_metricObjData_by_metricBelongTo(self):
        """
        组织异常指标数据dict,key为metricBelongTo
        :param exception_metricObjData:
        :return: 以metricBelongTo为key的dict
        """
        # if self.exception_metricObjData_by_metricBelongTo is not None: return self.exception_metricObjData_by_metricBelongTo
        exception_metricObjData_by_metricBelongTo = {}
        for i in self.exception_metricObjData:
            if i.metricBelongTo not in exception_metricObjData_by_metricBelongTo:
                exception_metricObjData_by_metricBelongTo[i.metricBelongTo] = []
            exception_metricObjData_by_metricBelongTo[i.metricBelongTo].append(i)
        return exception_metricObjData_by_metricBelongTo

    def organization_exception_logObjData_by_logBelongTo(self):
        """
        组织异常日志数据dict,key为logBelongTo
        :param exception_logObjData:
        :return: 以logBelongTo为key的dict
        """
        # if self.exception_logObjData_by_logBelongTo is not None: return self.exception_logObjData_by_logBelongTo
        exception_logObjData_by_logBelongTo = {}
        for i in self.exception_logObjData:
            if i.logBelongTo not in exception_logObjData_by_logBelongTo:
                exception_logObjData_by_logBelongTo[i.logBelongTo] = []
            exception_logObjData_by_logBelongTo[i.logBelongTo].append(i)
        return exception_logObjData_by_logBelongTo

    def get_fault_service_related_log_metric_data(self, serviceId, containerId=None, hostId=None):
        exception_metrics_service_related = dict()
        exception_logs_service_related = dict()
        if serviceId is None: return exception_metrics_service_related, exception_logs_service_related

        if serviceId and serviceId in self.organization_exception_metricObjData_by_metricBelongTo().keys():
            service_exception_metrics_list = self.organization_exception_metricObjData_by_metricBelongTo()[serviceId]
            for i in service_exception_metrics_list:
                if i.metricId not in exception_metrics_service_related:
                    exception_metrics_service_related[i.metricId] = []
                    exception_metrics_service_related[i.metricId].append(i)
                else:
                    exception_metrics_service_related[i.metricId].append(i)
        if hostId and hostId in self.organization_exception_metricObjData_by_metricBelongTo().keys():
            ssss = self.organization_exception_metricObjData_by_metricBelongTo()
            host_exception_metrics_list = self.organization_exception_metricObjData_by_metricBelongTo()[hostId]
            for i in host_exception_metrics_list:
                if i.metricId not in exception_metrics_service_related:
                    exception_metrics_service_related[i.metricId] = []
                    exception_metrics_service_related[i.metricId].append(i)
                else:
                    exception_metrics_service_related[i.metricId].append(i)
        if containerId and containerId in self.organization_exception_metricObjData_by_metricBelongTo().keys():
            docker_exception_metrics_list = self.organization_exception_metricObjData_by_metricBelongTo()[containerId]
            for i in docker_exception_metrics_list:
                if i.metricId not in exception_metrics_service_related:
                    exception_metrics_service_related[i.metricId] = []
                    exception_metrics_service_related[i.metricId].append(i)
                else:
                    exception_metrics_service_related[i.metricId].append(i)
        # 获取相关异常日志列表
        if serviceId and serviceId in self.organization_exception_logObjData_by_logBelongTo().keys():
            service_exception_logs_list = self.organization_exception_logObjData_by_logBelongTo()[serviceId]
            for i in service_exception_logs_list:
                if i.logId not in exception_logs_service_related:
                    exception_logs_service_related[i.logId] = []
                    exception_logs_service_related[i.logId].append(i)
                else:
                    exception_logs_service_related[i.logId].append(i)
        if hostId and hostId in self.organization_exception_logObjData_by_logBelongTo().keys():
            host_exception_logs_list = self.organization_exception_logObjData_by_logBelongTo()[hostId]
            for i in host_exception_logs_list:
                if i.logId not in exception_logs_service_related:
                    exception_logs_service_related[i.logId] = []
                    exception_logs_service_related[i.logId].append(i)
                else:
                    exception_logs_service_related[i.logId].append(i)
        if containerId and containerId in self.organization_exception_logObjData_by_logBelongTo().keys():
            docker_exception_logs_list = self.organization_exception_logObjData_by_logBelongTo()[containerId]
            for i in docker_exception_logs_list:
                if i.logId not in exception_logs_service_related:
                    exception_logs_service_related[i.logId] = []
                    exception_logs_service_related[i.logId].append(i)
                else:
                    exception_logs_service_related[i.logId].append(i)
        return exception_metrics_service_related, exception_logs_service_related

    def get_PC_input_data(self, exception_metrics, exception_logs):
        """
        原始数据预处理，得到PC算法输入格式
        :param exception_metrics:
        :param exception_logs:
        :return:
        """
        metric_input = None
        for key, value in exception_metrics.items():
            metric_data = [i.__dict__ for i in self.organization_original_metricObjData_by_metricId()[key]]
            # df = pd.DataFrame(metric_data)
            df = pd.read_json(json.dumps(metric_data), orient='records')
            if df.empty == False:
                metric_input_tmp = df[['metricId', 'timestamp', 'value']].groupby(
                    ['metricId', 'timestamp']).agg('mean')
                metric_input_tmp = metric_input_tmp.pivot_table(index='timestamp', columns='metricId', values='value')
                if metric_input is None:
                    metric_input = metric_input_tmp
                else:
                    metric_input = pd.concat([metric_input, metric_input_tmp], axis=1, sort=True)
        log_input = None
        for key, value in exception_logs.items():
            log_data = self.organization_original_logObjData_by_logId()
            log_data = self.organization_original_logObjData_by_logId()[key]
            log_data = [i.__dict__ for i in self.organization_original_logObjData_by_logId()[key]]
            # df = pd.DataFrame(log_data)
            df = pd.read_json(json.dumps(log_data), orient='records')
            if df.empty == False:
                log_input_tmp = df[['logId', 'timestamp', 'logMessage']].groupby(
                    ['logId', 'timestamp']).agg('count')
                log_input_tmp = log_input_tmp.pivot_table(index='timestamp', columns='logId', values='logMessage')
                if log_input is None:
                    log_input = log_input_tmp
                else:
                    log_input = pd.concat([log_input, log_input_tmp], axis=1)
        pc_input = pd.concat([metric_input, log_input], axis=1)
        pc_input.fillna(method='pad', axis=0, inplace=True)
        pc_input.fillna(method='backfill', axis=0, inplace=True)
        pc_input[pc_input == 0] = 0.00001
        return pc_input


def deploymentData_to_obj(deploymentData):
    deploymentObjData = list()
    if deploymentData is None: return deploymentObjData
    for data in deploymentData:
        tmp_obj = DeploymentDataEntry(data['serviceInstanceId'], data['serviceName'], data['hostId'], data['hostName'],
                                      data['containerId'], data['containerName'])
        deploymentObjData.append(tmp_obj)
    return deploymentObjData


def traceData_to_obj(traceData):
    traceObjData = list()
    if traceData is None: return traceObjData
    for data in traceData:
        tmp_obj = TraceDataEntry(data['id'], data['pid'], data['serviceId'], data['traceId'], data['serviceName'],
                                 data['serviceType'], data['startTime'])
        traceObjData.append(tmp_obj)
    return traceObjData


def originalMetricData_to_obj(original_metricData):
    original_metricObjData = list()
    if original_metricData is None: return original_metricObjData
    for data in original_metricData:
        tmp_obj = OriginalMetricEntry(data['metricId'], data['metricName'], data['timestamp'], data['value'],
                                      data['metricBelongTo'], data['units'], data['metricBelongLevel'])
        original_metricObjData.append(tmp_obj)
    return original_metricObjData


def originalLogData_to_obj(original_logData):
    original_logObjData = list()
    if original_logData is None: return original_logObjData
    for data in original_logData:
        tmp_obj = OriginalLogEntry(data['logId'], data['timestamp'], data['logMessage'], data['logBelongTo'],
                                      data['logLevel'], data['logBelongLevel'])
        original_logObjData.append(tmp_obj)
    return original_logObjData


def exceptionMetricData_to_obj(exception_metricData):
    exception_metricObjData = list()
    if exception_metricData is None: return exception_metricObjData
    for data in exception_metricData:
        tmp_obj = ExceptionMetricEntry(data['startTime'], data['endTime'], data['metricId'], data['metricName'],
                                       data['value'], data['metricBelongTo'], data['units'], data['metricBelongLevel'])
        exception_metricObjData.append(tmp_obj)
    return exception_metricObjData


def exceptionLogData_to_obj(exception_logData):
    exception_logObjData = list()
    if exception_logData is None: return exception_logObjData
    for data in exception_logData:
        tmp_obj = ExceptionLogEntry(data['startTime'], data['endTime'], data['logId'], data['logBelongTo'],
                                    data['logExceptionSegment'], data['logBelongLevel'])
        exception_logObjData.append(tmp_obj)
    return exception_logObjData


if __name__ == '__main__':
    metric1 = OriginalMetricEntry("1", "1", "1", 1.0, "1", "1", "1")
    metric2 = OriginalMetricEntry("2", "2", "2", 1.0, "2", "2", "2")
    list = [metric1.__dict__, metric2.__dict__]
    a = json.dumps(list)
    df = pd.read_json(a, orient='records')
    pass
