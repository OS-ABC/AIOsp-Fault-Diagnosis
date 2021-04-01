import networkx as nx

from utils.graph import ServiceNode
from utils.pageRank import PRIterator


class IdentifyFaultService:
    @staticmethod
    def generate_service_invoke_graph(traceObjData_by_traceId):
        """
        根据调用链数据
        :param traceObjData_by_traceId:
        :return: nodes、edges一种服务调用图的表现形式；traverse_initial_list所有的调用发起节点
        """
        num_nodes = {} #{spanId:ServiceNode，spanId:ServiceNode}
        num_edges = [] #[[spanId,spanId],[spanId,spanId]]
        traverse_initial_list = []#[serviceId,serviceId]
        for key, value in traceObjData_by_traceId.items():
            for i in value:
                id = i.id
                pid = i.pid
                serviceId = i.serviceId
                serviceName = i.serviceName
                serviceType = i.serviceType
                if id not in num_nodes:
                    num_nodes[id] = ServiceNode(serviceId,serviceName,serviceType)
                if pid and id and pid != -1:
                    if [pid, id] not in num_edges:
                        num_edges.append([pid, id])
                elif pid == -1:
                    if serviceId not in traverse_initial_list:
                        traverse_initial_list.append(serviceId)

        #转换为真正调用图数据
        nodes = {} #{serviceId:ServiceNode，serviceId:ServiceNode}
        edges = [] #[[serviceId,serviceId],[serviceId,serviceId]]
        # 将编号边替换为具体的服务ID
        for num_edge in num_edges:
            if num_edge[0] in num_nodes and num_edge[1] in num_nodes:
                p_servceId = num_nodes[num_edge[0]].serviceId
                c_serviceId = num_nodes[num_edge[1]].serviceId
                if p_servceId!= c_serviceId and [p_servceId,c_serviceId] not in edges:
                    edges.append([p_servceId,c_serviceId])
        # 将编号节点替换为具体的服务ID
        for key, value in num_nodes.items():
            if value.serviceId not in nodes:
                nodes[value.serviceId] = value
        return nodes,edges,traverse_initial_list

    @staticmethod
    def completion_serviceNode_deploymentData(deploymentObjData_by_sviid,nodes):
        """
        对服务依赖图中的节点补充部署信息
        :param deployment_data: 接入的部署数据
        :param nodes: 图中节点dict
        :return:nodes
        """
        for key, value in nodes.items():
            if key in deploymentObjData_by_sviid.keys():
                value.hostId = deploymentObjData_by_sviid[key].hostId
                value.hostName = deploymentObjData_by_sviid[key].hostName
                value.dockerName = deploymentObjData_by_sviid[key].containerName
                value.dockerId = deploymentObjData_by_sviid[key].containerId
        return nodes

    @staticmethod
    def set_service_exception_info(nodes, data):
        """
        识别出异常服务，并在nodes中补充异常信息
        :param nodes: 服务依赖图节点dict ServiceNode
        :param data: input_data实例
        :return: nodes 补充上是否异常信息
        """
        if nodes is None:
            return None
        exception_list_metric_belongTo = data.organization_exception_metricObjData_by_metricBelongTo()
        exception_list_log_belongTo = data.organization_exception_logObjData_by_logBelongTo()
        for key, serviceNode in nodes.items():
            if serviceNode.serviceId in (
                    exception_list_metric_belongTo or exception_list_log_belongTo) or serviceNode.hostId in (
                    exception_list_metric_belongTo or exception_list_log_belongTo) or serviceNode.containerId in (
                    exception_list_metric_belongTo or exception_list_log_belongTo):
                serviceNode.isException = 1
        return nodes

    @staticmethod
    def location_root_service(graph, start_service_id, root_services):
        """
        定位根因服务，某个节点为初始遍历节点
        :param graph:
        :param start_service_id:
        :param root_services:
        :return:root_services 本次遍历后的根因列表
        """
        queue = []
        queue.append(start_service_id)
        while (len(queue) > 0):
            cur_node_id = queue.pop(0)
            if IdentifyFaultService.is_root_service(graph, cur_node_id):
                if cur_node_id not in root_services:
                    root_services[cur_node_id] = 1
                else:
                    root_services[cur_node_id] = root_services[cur_node_id] + 1
            else:
                for chirld_id in graph[cur_node_id].childs:
                    if graph[chirld_id].isException == 1:
                        queue.append(chirld_id)
        return root_services

    @staticmethod
    def is_root_service(graph, service_id):
        is_root = True
        chirlds = graph[service_id].childs
        for chirld_id in chirlds:
            if graph[chirld_id].isException == 1:
                is_root = False
        if graph[service_id].isException == 0:
            is_root = False
        return is_root

    @staticmethod
    def get_fault_services_list_PR(graph, traverse_initial_list):
        """
        识别故障服务列表 PR方法
        :param graph:
        :param traverse_initial_list:
        :return: final_root_services 故障服务列表 {serviceId:数值，serviceId:数值}
        """
        if len(graph.nodes) == 0:
            return None
        dg = nx.DiGraph()
        for key, node in graph.nodes.items():
            dg.add_node(key)
        for edge in graph.edges:
            dg.add_edge(edge[0], edge[1])
        pr = PRIterator(dg)
        page_ranks = pr.page_rank()
        node_pr_sorted = sorted(page_ranks.items(), key=lambda x: x[1], reverse=True)
        root_services = {}
        for index, serviceId in enumerate(node_pr_sorted):
            if index < 3:
                root_services[serviceId[0]] = serviceId[1]
        return root_services

    @staticmethod
    def get_fault_services_list(graph, traverse_initial_list):
        """
        识别故障服务 使用图广度优先搜索算法
        :param graph:
        :param traverse_initial_list:
        :return: final_root_services 故障服务列表 {serviceId:数值，serviceId:数值}
        """
        construct_graph = graph.generate_invoke_graph_consturct()
        if len(construct_graph) == 0 or len(traverse_initial_list) == 0:
            return None
        root_services = {}  # {serviceId:数值，serviceId:数值}
        # 遍历图初始遍历列表
        for i in traverse_initial_list:
            root_services = IdentifyFaultService.location_root_service(construct_graph, i, root_services)
        return root_services