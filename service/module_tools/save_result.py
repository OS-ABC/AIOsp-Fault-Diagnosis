import json

from dao.db_dao import DBDao


class SaveResult:
    @staticmethod
    def save(service_invoke_graph,final_root_services,services_diagnisis_results):
        dbDao = DBDao()
        fault_ids = dict()
        # 存储识别出的故障服务到故障服务表
        for fault_service_id in final_root_services:
            serviceNode = service_invoke_graph.nodes[fault_service_id]
            fault_service = dbDao.insert_fault_service_into_fault_service_table(serviceNode.serviceId,serviceNode.serviceName,serviceNode.serviceType,serviceNode.hostName)
            fault_ids[fault_service.id] = fault_service.fault_service_id
        # 生成存储结果的服务依赖图Json
        fault_service_dependency_graph_json = SaveResult.generate_save_fault_service_dependency_graph_json(service_invoke_graph,fault_ids)
        for fault_id, fault_service_id in fault_ids.items():
            fault_service_roots = services_diagnisis_results[fault_service_id]['falut_root_dict']
            final_exception_data_graph = services_diagnisis_results[fault_service_id]['final_exception_data_graph']
            for index, root_id in enumerate(fault_service_roots.keys()):
                rootNode = final_exception_data_graph.nodes[root_id]
                if rootNode.nodeType == "metric":
                    rootNode.nodeType = 0
                else:
                    rootNode.nodeType = 1
                service_falut_root = dbDao.insert_fault_service_root_into_fault_service_root_table(fault_id,root_id,rootNode.name,rootNode.detail,rootNode.nodeType,index)
            service_dependency_graph = dbDao.insert_service_dependency_graph_into_service_dependency_graph_table(fault_id,fault_service_dependency_graph_json)
            # 生成存储结果的服务异常数据依赖图Json
            service_exception_data_dependency_graph_json =  SaveResult.generate_save_service_exception_data_dependency_graph_json(final_exception_data_graph,fault_service_roots)
            exception_data_dependency_graph = dbDao.insert_exception_data_dependency_graphh_into_exception_data_dependency_graph_table(fault_id,service_exception_data_dependency_graph_json)
            dbDao.db_commit()
        dbDao.db_close()

    @staticmethod
    def generate_save_fault_service_dependency_graph_json(service_invoke_graph,fault_ids):
        storage_graph_json = dict()
        nodes = list()
        edges = list()
        for node_id, node in service_invoke_graph.nodes.items():
            save_node_dict = {}
            save_node_dict['id'] = node_id
            save_node_dict['label'] = node.serviceName
            save_node_dict['data'] = {}
            save_node_dict['data']['name'] = node.serviceName
            save_node_dict['data']['type'] = node.serviceType
            save_node_dict['data']['type'] = node.hostName
            save_node_dict['data']['fault_id'] = None
            if node_id in fault_ids.values():
                save_node_dict['data']['health_level'] = 2
                for key, value in fault_ids.items():
                    if value == node_id:
                        save_node_dict['data']['fault_id'] = key
            elif node.isException == 1:
                save_node_dict['data']['health_level'] = 1
            else:
                save_node_dict['data']['health_level'] = 0

            nodes.append(save_node_dict)
        for i in service_invoke_graph.edges:
            edge = {}
            edge['source'] = i[0]
            edge['target'] = i[1]
            edges.append(edge)
        storage_graph_json['nodes'] = nodes
        storage_graph_json['edges'] = edges
        graph_json = json.dumps(storage_graph_json)
        # graph_json = storage_graph_json
        return graph_json

    @staticmethod
    def generate_save_service_exception_data_dependency_graph_json(final_exception_data_graph, fault_service_roots):
        storage_graph_json = dict()
        nodes = list()
        edges = list()
        for node_id, node in final_exception_data_graph.nodes.items():
            save_node_dict = {}
            save_node_dict['id'] = node.id
            save_node_dict['label'] = node.name
            save_node_dict['data'] = dict()
            save_node_dict['data']['name'] = node.name
            save_node_dict['data']['type'] = node.nodeType
            save_node_dict['data']['detail'] = node.detail
            save_node_dict['data']['belongTo'] = node.belongTo
            save_node_dict['data']['exceptionTime'] = node.exceptionTime
            save_node_dict['data']['units'] = node.units
            if node_id in fault_service_roots.keys():
                save_node_dict['data']['import'] = 1
            else:
                save_node_dict['data']['import'] = 0
            nodes.append(save_node_dict)
        for i in final_exception_data_graph.edges:
            edge = {}
            edge['source'] = i[0]
            edge['target'] = i[1]
            edges.append(edge)
        storage_graph_json['nodes'] = nodes
        storage_graph_json['edges'] = edges
        graph_json_result = json.dumps(storage_graph_json)
        # graph_json_result = storage_graph_json
        return graph_json_result

    @staticmethod
    def save_solutions(fault_id,log_id,sorted_solutions):
        dbDao = DBDao()
        for index,solution in enumerate(sorted_solutions):
            faultServiceSolution = dbDao.insert_fault_service_solution_insert_fault_service_solution_table(fault_id,log_id,solution['reason'],solution['html_content'],index)
        result = dbDao.update_root_detail_table_has_solutuon(fault_id,log_id)
        if result:
            dbDao.db_commit()
        dbDao.db_close()
        return result