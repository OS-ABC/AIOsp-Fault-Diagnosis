import networkx as nx

from utils.graph import ExceptionDataNode, Graph
from utils.pageRank import PRIterator
from utils.pcalg import construct_service_dependency_diagram


class DiagnosisFaultService:
    @staticmethod
    def get_servcie_fault_causes(serviceNode,data):
        """
        对某一故障服务进行细粒度诊断
        :param serviceNode:
        :param data: input_data实例
        :return:
        """
        # 确定与故障服务相关的异常指标
        serviceId = serviceNode.serviceId
        hostId = serviceNode.hostId
        containerId = serviceNode.containerId
        exception_metrics, exception_logs = data.get_fault_service_related_log_metric_data(serviceId,containerId,hostId)
        # 处理原始数据，得到PC算法输入格式，原始数据预处理
        pc_input = data.get_PC_input_data(exception_metrics, exception_logs)
        # 利用PC算法生成图,g的节点为输入数据的Index
        g, columns_mapping = construct_service_dependency_diagram(pc_input)
        #生成的g,替换节点为metricId和logId
        g_new = DiagnosisFaultService.get_g_dataId(g, columns_mapping)
        # 识别图中的根因节点
        falut_root_dict = DiagnosisFaultService.get_root_cause(g_new)
        # 生成返回图结构
        final_exception_data_graph = DiagnosisFaultService.geneate_final_return_graph(g_new,exception_metrics, exception_logs)
        return falut_root_dict,final_exception_data_graph

    @staticmethod
    def get_g_dataId(g,columns_mapping):
        g_new = nx.DiGraph()
        for node in g.nodes:
            g_new.add_node(columns_mapping[node])
        for edge in g.edges:
            g_new.add_edge(columns_mapping[edge[0]],columns_mapping[edge[1]])
        return  g_new

    @staticmethod
    def get_root_cause(g):
        """
        通过关系图获取根因列表，获取故障服务根因列表
        Args:
            g: 关系图

        Returns: 根因列表

        """
        result = list()
        # 获取Pr值最高的点
        begin_node_id, begin_node_pr = None, 0
        # for node_id in node_ids:
        #     if len(list(g.predecessors(node_id))) > max_pre_size:
        #         max_pre_node = node_id
        #         max_pre_size = len(list(g.predecessors(node_id)))
        pr = PRIterator(g)
        page_ranks = pr.page_rank()
        node_pr_sorted = sorted(page_ranks.items(), key=lambda x: x[1], reverse=True)
        begin_node_id = node_pr_sorted[0][0]
        # 层次遍历
        node_filter, node_queue = {begin_node_id}, list([begin_node_id])
        while node_queue:
            node_now = node_queue.pop(0)
            if not g.predecessors(node_now):
                if node_now not in result:
                    result.append(node_now)
                continue
            is_pre_not_filter = False
            for k in g.predecessors(node_now):
                if k not in node_filter:
                    is_pre_not_filter = True
                    node_filter.add(k)
                    node_queue.append(k)
            # 如果所有的上游节点都在 filter 中，将当前节点加入 result，避免 result 为空的情况
            if not is_pre_not_filter:
                for k in g.predecessors(node_now):
                    if k not in result:
                        result.append(k)
                if node_now not in result:
                    result.append(node_now)

        g_reverse = g.reverse(copy=True)
        pr_reverse = PRIterator(g_reverse)
        page_ranks_reverse = pr_reverse.page_rank()
        for key, value in page_ranks_reverse.items():
            if key in result:
                value += 0.5
        node_pr_reverse_sorted = sorted(page_ranks.items(), key=lambda x: x[1], reverse=True)
        result_final = {}
        for index, i in enumerate(node_pr_reverse_sorted):
            if index < 3:
                result_final[i[0]]= i[1]
        return result_final

    @staticmethod
    def geneate_final_return_graph(g_new,exception_metrics, exception_logs):
        """
        生成返回的图结构
        :param g_new:
        :param data:
        :param exception_metrics: 与服务相关的异常指标
        :param exception_logs: 与服务相关的异常日志
        :return:
        """
        nodes = {}
        for node_id in g_new.nodes:
            id = node_id
            if id in exception_metrics:
                nodeType = "metric"
                tmpExceptionDataNode = ExceptionDataNode(id, nodeType)
                tmpExceptionDataNode.name = exception_metrics[id][0].metricName
                tmpExceptionDataNode.detail = exception_metrics[id][0].value
                tmpExceptionDataNode.units = exception_metrics[id][0].units
                tmpExceptionDataNode.belongTo = exception_metrics[id][0].metricBelongTo
                tmpExceptionDataNode.exceptionTime = exception_metrics[id][0].startTime
                nodes[id] = tmpExceptionDataNode
            elif id in exception_logs:
                nodeType = "log"
                tmpExceptionDataNode = ExceptionDataNode(id, nodeType)
                tmpExceptionDataNode.belongTo = exception_logs[id][0].logBelongTo
                tmpExceptionDataNode.exceptionTime = exception_logs[id][0].startTime
                tmpExceptionDataNode.detail = exception_logs[id][0].logExceptionSegment
                nodes[id] = tmpExceptionDataNode
            else:
                continue
        edges = g_new.edges()
        final_return_graph = Graph(nodes,edges)
        return final_return_graph
