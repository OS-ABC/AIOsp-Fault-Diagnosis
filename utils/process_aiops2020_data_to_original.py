import pandas as pd
import numpy as np
import csv
import json

def get_original_trace_data():
    trace_csf_path = '../data/aiops_data_2020/2020_04_11/调用链指标/trace_csf.csv'
    trace_fly_remote_path = '../data/aiops_data_2020/2020_04_11/调用链指标/trace_fly_remote.csv'
    trace_jdbc_path = '../data/aiops_data_2020/2020_04_11/调用链指标/trace_jdbc.csv'
    trace_local_path = '../data/aiops_data_2020/2020_04_11/调用链指标/trace_local.csv'
    trace_osb_path = '../data/aiops_data_2020/2020_04_11/调用链指标/trace_osb.csv'
    trace_remote_process_path = '../data/aiops_data_2020/2020_04_11/调用链指标/trace_remote_process.csv'

    result = {}
    with open(trace_csf_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tmp = {}
            traceId = row['traceId']
            id = row['id']
            pid = row['pid']
            # serviceId = row['cmdb_id'] + ':' + row['serviceName']
            serviceType = row['callType']
            tmp['id'] = id
            tmp['pid'] = pid
            tmp['serviceId'] = None
            tmp['cmdb_id'] = row['cmdb_id']
            tmp['serviceType'] = serviceType
            tmp['serviceName'] = row['serviceName']
            tmp['startTime'] = row['startTime']
            if traceId not in result:
                result[traceId] = []
                result[traceId].append(tmp)
            else:
                result[traceId].append(tmp)

    with open(trace_jdbc_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tmp = {}
            traceId = row['traceId']
            id = row['id']
            pid = row['pid']
            # serviceId = row['cmdb_id'] + ':' + row['dsName']
            serviceType = row['callType']
            tmp['id'] = id
            tmp['pid'] = pid
            tmp['serviceId'] = row['dsName']
            tmp['cmdb_id'] = row['cmdb_id']
            tmp['serviceType'] = serviceType
            tmp['serviceName'] = row['dsName']
            tmp['startTime'] = row['startTime']
            if traceId not in result:
                result[traceId] = []
                result[traceId].append(tmp)
            else:
                result[traceId].append(tmp)

    with open(trace_local_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tmp = {}
            traceId = row['traceId']
            id = row['id']
            pid = row['pid']
            # serviceId = row['cmdb_id'] + ':' + row['dsName']
            serviceType = row['callType']
            tmp['id'] = id
            tmp['pid'] = pid
            tmp['serviceId'] = row['dsName']
            tmp['cmdb_id'] = row['cmdb_id']
            tmp['serviceType'] = serviceType
            tmp['serviceName'] = row['dsName']
            tmp['startTime'] = row['startTime']
            if traceId not in result:
                result[traceId] = []
                tmp['startTime'] = row['startTime']
            else:
                result[traceId].append(tmp)

    with open(trace_osb_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tmp = {}
            traceId = row['traceId']
            id = row['id']
            pid = row['pid']
            serviceId = row['cmdb_id'] + ':' + row['serviceName']
            serviceType = row['callType']
            tmp['id'] = id
            tmp['pid'] = pid
            tmp['serviceId'] = serviceId
            tmp['cmdb_id'] = row['cmdb_id']
            tmp['serviceType'] = serviceType
            tmp['serviceName'] = row['serviceName']
            tmp['startTime'] = row['startTime']
            if traceId not in result:
                result[traceId] = []
                result[traceId].append(tmp)
            else:
                result[traceId].append(tmp)

    with open(trace_fly_remote_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tmp = {}
            traceId = row['traceId']
            id = row['id']
            pid = row['pid']
            serviceId = row['cmdb_id'] + ':' + row['serviceName']
            serviceType = row['callType']
            tmp['id'] = id
            tmp['pid'] = pid
            tmp['serviceId'] = serviceId
            tmp['cmdb_id'] = row['cmdb_id']
            tmp['serviceType'] = serviceType
            tmp['serviceName'] = row['serviceName']
            tmp['startTime'] = row['startTime']
            if traceId not in result:
                result[traceId] = []
                result[traceId].append(tmp)
            else:
                result[traceId].append(tmp)

    with open(trace_remote_process_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tmp = {}
            traceId = row['traceId']
            id = row['id']
            pid = row['pid']
            serviceId = row['cmdb_id'] + ':' + row['serviceName']
            serviceType = row['callType']
            tmp['id'] = id
            tmp['pid'] = pid
            tmp['serviceId'] = serviceId
            tmp['cmdb_id'] = row['cmdb_id']
            tmp['serviceType'] = serviceType
            tmp['serviceName'] = row['serviceName']
            tmp['startTime'] = row['startTime']
            if traceId not in result:
                result[traceId] = []
                result[traceId].append(tmp)
            else:
                result[traceId].append(tmp)
    for k,value in result.items():
        tmp_pid_dict = {}
        for i in value:
            if i['pid'] != 'None':
                tmp_pid_dict[i['pid']] = i['cmdb_id']
        del_values = list()
        for i in value:
            if i['serviceType'] == "CSF":
                if i['id'] in tmp_pid_dict:
                    cmdb_id = tmp_pid_dict[i['id']]
                    serviceId = cmdb_id +":"+i['serviceName']
                    i['serviceId'] = serviceId
                    i['cmdb_id'] = cmdb_id
                else:
                    del_values.append(i)
        for del_i in del_values:
            value.remove(del_i)

    save_path = '../data/aiops_data_2020/2020_04_11/origina_traces.json'
    with open(save_path, 'w') as f:
        json.dump(result, f, indent=2, sort_keys=True, ensure_ascii=False)

def get_target_deployment_data(original_deployment_data):
    """
        原始部署数据处理为接入目标格式
        Args:
            original_metric_data: 原始部署数据

        Returns: 原始部署数据的目标接入格式{ serviceInstanceId:{ serviceInstanceId:””, serviceName:””, hostId:””, hostname:””, containerId:””, containerName:””},{},{}}
    """
    # original_deployment_data = [{"serviceInstanceId":"os_021:osb_001","serviceName":"osb_001", "containerId":None, "containerName":None,"hostId":"os_021","hostName":"os_021"},{"serviceInstanceId":"os_022:osb_002","serviceName":"osb_002", "containerId":None, "containerName":None,"hostId":"os_022", "hostName":"os_022"},{"serviceInstanceId":"docker_001:csf_001","serviceName":"csf_001", "containerId":"docker_001", "containerName":"docker_001","hostId":"os_017", "hostName":"os_017"},{"serviceInstanceId":"docker_002:csf_001","serviceName":"csf_001", "containerId":"docker_002", "containerName":"docker_002","hostId":"os_018", "hostName":"os_018"},{"serviceInstanceId":"docker_003:csf_001","serviceName":"csf_001", "containerId":"docker_003", "containerName":"docker_003","hostId":"os_019", "hostName":"os_019"},{"serviceInstanceId":"docker_004:csf_001","serviceName":"csf_001", "containerId":"docker_004", "containerName":"docker_004","hostId":"os_020", "hostName":"os_020"},{"serviceInstanceId":"docker_005:csf_002","serviceName":"csf_002","containerId":"docker_005","containerName":"docker_005","hostId":"os_017","hostName":"os_017"},{"serviceInstanceId":"docker_006:csf_002","serviceName":"csf_002", "containerId":"docker_006", "containerName":"docker_006","hostId":"os_018","hostName":"os_018"},{"serviceInstanceId":"docker_007:csf_002","serviceName":"csf_002","containerId":"docker_007","containerName":"docker_007","hostId":"os_019","hostName":"os_019"},{"serviceInstanceId":"docker_008:csf_002","serviceName":"csf_002","containerId":"docker_008","containerName":"docker_008","hostId":"os_020","hostName":"os_020"},{"serviceInstanceId":"docker_005:csf_003","serviceName":"csf_003","containerId":"docker_005","containerName":"docker_005","hostId":"os_017","hostName":"os_017"},{"serviceInstanceId":"docker_006:csf_003","serviceName":"csf_003","containerId":"docker_006","containerName":"docker_006","hostId":"os_018","hostName":"os_018"},{"serviceInstanceId":"docker_007:csf_003","serviceName":"csf_003","containerId":"docker_007","containerName":"docker_007","hostId":"os_019","hostName":"os_019"},{"serviceInstanceId":"docker_008:csf_003","serviceName":"csf_003","containerId":"docker_008","containerName":"docker_008","hostId":"os_020","hostName":"os_020"},{"serviceInstanceId":"docker_005:csf_004","serviceName":"csf_004","containerId":"docker_005","containerName":"docker_005","hostId":"os_017","hostName":"os_017"},{"serviceInstanceId":"docker_006:csf_004","serviceName":"csf_004","containerId":"docker_006","containerName":"docker_006","hostId":"os_018","hostName":"os_018"},{"serviceInstanceId":"docker_007:csf_004","serviceName":"csf_004","containerId":"docker_007","containerName":"docker_007","hostId":"os_019","hostName":"os_019"},{"serviceInstanceId":"docker_008:csf_004","serviceName":"csf_004","containerId":"docker_008","containerName":"docker_008","hostId":"os_020","hostName":"os_020"},{"serviceInstanceId":"docker_005:csf_005","serviceName":"csf_005","containerId":"docker_005","containerName":"docker_005","hostId":"os_017","hostName":"os_017"},{"serviceInstanceId":"docker_006:csf_005","serviceName":"csf_005","containerId":"docker_006","containerName":"docker_006","hostId":"os_018","hostName":"os_018"},{"serviceInstanceId":"docker_007:csf_005","serviceName":"csf_005", "containerId":"docker_007", "containerName":"docker_007","hostId":"os_019","hostName":"os_019"},{"serviceInstanceId":"docker_008:csf_005","serviceName":"csf_005","containerId":"docker_008","containerName":"docker_008","hostId":"os_020","hostName":"os_020"},{"serviceInstanceId":"db_001","serviceName":"db_001", "containerId":None, "containerName":None,"hostId":None,"hostName":None},{"serviceInstanceId":"db_002","serviceName":"db_001", "containerId":None, "containerName":None,"hostId":None,"hostName":None},{"serviceInstanceId":"db_003","serviceName":"db_003","containerId":None,"containerName":None,"hostId":None,"hostName":None},{"serviceInstanceId":"db_004","serviceName":"db_004","containerId":None, "containerName":None,"hostId":None,"hostName":None},{"serviceInstanceId":"db_005","serviceName":"db_005","containerId":None,"containerName":None,"hostId":None,"hostName":None},{"serviceInstanceId":"db_006","serviceName":"db_006","containerId":None,"containerName":None,"hostId":None,"hostName":None},{"serviceInstanceId":"db_007","serviceName":"db_007","containerId":None,"containerName":None,"hostId":None,"hostName":None},{"serviceInstanceId":"db_008","serviceName":"db_008","containerId":None,"containerName":None,"hostId":None,"hostName":None},{"serviceInstanceId":"db_009","serviceName":"db_009","containerId":None,"containerName":None,"hostId":None,"hostName":None},{"serviceInstanceId":"db_010","serviceName":"db_010","containerId":None, "containerName":None,"hostId":None,"hostName":None},{"serviceInstanceId":"db_011","serviceName":"db_011","containerId":None,"containerName":None,"hostId":None,"hostName":None},{"serviceInstanceId":"db_012","serviceName":"db_012","containerId":None,"containerName":None,"hostId":None,"hostName":None},{"serviceInstanceId":"db_013","serviceName":"db_013","containerId":None,"containerName":None,"hostId":None,"hostName":None},{"serviceInstanceId":":docker_001:fly_remote_001","serviceName":"fly_remote_001","containerId":"docker_001","containerName":"docker_001","hostId":None,"hostName":None},{"serviceInstanceId":"docker_002:fly_remote_001","serviceName":"fly_remote_001","containerId":"docker_002","containerName":"docker_002","hostId":None,"hostName":None},{"serviceInstanceId":"docker_003:fly_remote_001","serviceName":"fly_remote_001","containerId":"docker_003","containerName":"docker_003","hostId":None,"hostName":None},{"serviceInstanceId":"docker_004:fly_remote_001","serviceName":"fly_remote_001","containerId":"docker_004","containerName":"docker_004","hostId":None,"hostName":None}]
    # target_deployment_data = {}
    # for i in original_deployment_data:
    #     target_deployment_data[i['serviceInstanceId']]= i
    # return target_deployment_data


# f = open('../../../data/aiops_data_2020/2020_05_22/original_deployment_data.json', 'r')
# # deployment_data = json.load(f)
# get_original_trace_data()
def get_original_items_data():
    """
    拆分指标文件
    :param :
    :return: json
    """
    result = {}
    db_oracle_11g_path = '../data/aiops_data_2020/2020_04_11/平台指标/db_oracle_11g.csv'
    dcos_docker_path = '../data/aiops_data_2020/2020_04_11/平台指标/dcos_docker.csv'
    os_linux_path = '../data/aiops_data_2020/2020_04_11/平台指标/os_linux.csv'
    with open(db_oracle_11g_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            curveId = row['itemid']+":"+row['name']+":"+row['bomc_id']
            if curveId not in result:
                result[curveId] = {}
                result[curveId]['metricId'] = row['itemid']
                result[curveId]['metricName'] = row['name']
                result[curveId]['metricBelongTo'] = row['cmdb_id']
                result[curveId]['metricBelongLevel'] = "service"
                result[curveId]['values'] = []
                result[curveId]['timeStamps'] = []
                result[curveId]['values'].append(row['value'])
                result[curveId]['timeStamps'].append(row['timestamp'])
            else:
                result[curveId]['values'].append(row['value'])
                result[curveId]['timeStamps'].append(row['timestamp'])
    with open(dcos_docker_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            curveId = row['itemid']+":"+row['name']+":"+row['bomc_id']
            if curveId not in result:
                result[curveId] = {}
                result[curveId]['metricId'] = row['itemid']
                result[curveId]['metricName'] = row['name']
                result[curveId]['metricBelongTo'] = row['cmdb_id']
                result[curveId]['metricBelongLevel'] = "docker"
                result[curveId]['values'] = []
                result[curveId]['timeStamps'] = []
                result[curveId]['values'].append(row['value'])
                result[curveId]['timeStamps'].append(row['timestamp'])
            else:
                result[curveId]['values'].append(row['value'])
                result[curveId]['timeStamps'].append(row['timestamp'])

    with open(os_linux_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            curveId = row['itemid']+":"+row['name']+":"+row['bomc_id']
            if curveId not in result:
                result[curveId] = {}
                result[curveId]['metricId'] = row['itemid']
                result[curveId]['metricName'] = row['name']
                result[curveId]['metricBelongTo'] = row['cmdb_id']
                result[curveId]['metricBelongLevel'] = "host"
                result[curveId]['values'] = []
                result[curveId]['timeStamps'] = []
                result[curveId]['values'].append(row['value'])
                result[curveId]['timeStamps'].append(row['timestamp'])
            else:
                result[curveId]['values'].append(row['value'])
                result[curveId]['timeStamps'].append(row['timestamp'])
    save_path = '../data/aiops_data_2020/2020_04_11/origina_items.json'
    with open(save_path, 'w') as f:
        json.dump(result, f, indent=2, sort_keys=True, ensure_ascii=False)
    pass

if __name__ == '__main__':
    # get_original_items_data()
    get_original_trace_data()