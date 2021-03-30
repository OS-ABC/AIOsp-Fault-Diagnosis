
from service.module_tools.diagnosis_faultservice import DiagnosisFaultService
from service.module_tools.identify_faultservice import IdentifyFaultService
from service.module_tools.input_data import InputData
from service.module_tools.save_result import SaveResult
from utils.graph import Graph


def fault_diagmosis(deploymentData, traceData, original_metricData, original_logData, exception_metricData,
                    exception_logData):
    #输入数据
    data = InputData(deploymentData, traceData, original_metricData, original_logData, exception_metricData,
                    exception_logData)
    #识别故障服务
    final_root_services, service_invoke_graph =  get_root_services(data)
    #对故障服务诊断
    services_diagnisis_results = get_fault_services_roots(data,final_root_services,service_invoke_graph)
    #存储诊断结果
    save_fault_root_cause_diagnosis_result(service_invoke_graph,final_root_services,services_diagnisis_results)
    pass

def get_root_services(data):
    """
    故障服务识别子模块主入口
    :param data: input_data实例
    :return: 故障服务列表（{serviceId:数值}）、服务依赖图（graph实例，nodes:{serviceId:ServiceNode,serviceId:ServiceNode},edges[[serviceId,serviceId],[serviceId,serviceId]]）
    """
    nodes, edges, traverse_initial_list = IdentifyFaultService.generate_service_invoke_graph(data.organization_traceObjData_by_traceId())
    nodes = IdentifyFaultService.completion_serviceNode_deploymentData(data.organization_deploymentObjData_by_sviid(), nodes)
    nodes = IdentifyFaultService.set_service_exception_info(nodes,data)
    service_invoke_graph = Graph(nodes, edges)
    # final_root_services =  get_fault_services_list(service_invoke_graph,traverse_initial_list)
    final_root_services = IdentifyFaultService.get_fault_services_list_PR(service_invoke_graph,traverse_initial_list)
    print('故障服务列表为：{}'.format(final_root_services))
    return final_root_services, service_invoke_graph

def get_fault_services_roots(data,final_root_services,service_invoke_graph):
    """
    对所有故障服务进行诊断入口
    :param data:input_data实例
    :param final_root_services:{serviceId:数值,serviceId:数值}
    :param service_invoke_graph:nodes:{},egdes:[]
    :return:
    """
    services_diagnisis_results = dict()
    for i in final_root_services:
        serviceNode = service_invoke_graph.nodes[i]
        services_diagnisis_results[serviceNode.serviceId] = dict()
        falut_root_dict, final_exception_data_graph = DiagnosisFaultService.get_servcie_fault_causes(serviceNode, data)
        # 打印结果
        falut_root_dict_name = dict()
        for root_id,rootValue in falut_root_dict.items():
            rootNode = final_exception_data_graph.nodes[root_id]
            falut_root_dict_name[rootNode.name] = rootValue
        print('{0} 服务故障根因为：{1}'.format(serviceNode.serviceName, falut_root_dict_name))

        services_diagnisis_results[serviceNode.serviceId]['falut_root_dict'] = falut_root_dict
        services_diagnisis_results[serviceNode.serviceId]['final_exception_data_graph'] = final_exception_data_graph
    return services_diagnisis_results

def save_fault_root_cause_diagnosis_result(service_invoke_graph,final_root_services,services_diagnisis_results):
    SaveResult.save(service_invoke_graph,final_root_services,services_diagnisis_results)




