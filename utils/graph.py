class ServiceNode:
    def __init__(self,serviceId, serviceName = None,serviceType = None):
        self.serviceId = serviceId
        self.serviceName = serviceName
        self.serviceType = serviceType
        self.hostName = None
        self.containerName = None
        self.hostId = None
        self.containerId = None
        self.isException = 0
        self.childs = []
    def add_childs(self,service_id):
        self.childs.append(service_id)

class ExceptionDataNode:
    def __init__(self, id, nodeType):
        self.id = id
        self.nodeType = nodeType
        self.name = None
        self.detail = None
        self.belongTo = None
        self.exceptionTime = None
        self.units = None
        self.childs = []

    def add_childs(self, id):
        self.childs.append(id)
class Graph:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.generate_invoke_graph_consturct()

    def generate_invoke_graph_consturct(self):
        """
        生成图遍历算法所需图结构
        :param nodes:{serviceId:ServiceNode,serviceId:ServiceNode}
        :param edges:[[serviceId,serviceId][serviceId,serviceId]]
        :return:graph
        """
        graph = {}
        for edge in self.edges:
            for i in edge:
                if i not in graph.keys():
                    node = self.nodes[i]
                    graph[i] = node
            if edge[1] not in graph[edge[0]].childs:
                graph[edge[0]].add_childs(edge[1])
        # 对图中单点节点补充
        for key, node in self.nodes.items():
            if key not in graph:
                graph[key] = node
        self.nodes = graph