import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bean.save_model import FaultServiceRoot, FaultService, ServiceDependencyGraph, ExceptionDataDependencyGraph, \
    FaultServiceSolution

class DBDao:
    def __init__(self):
        self.engine = create_engine('mysql+pymysql://root:root1234@127.0.0.1:3306/fault_result_solution')
        self.session = self.get_session()

    def get_session(self):
        # 创建DBSession类型:
        DBSession = sessionmaker(bind=self.engine)
        session = DBSession()
        return session

    def db_close(self):
        self.session.close()

    def db_commit(self):
        self.session.commit()

    def get_all_root_logs_noSolution(self):
        """
        获取未生成修复方案的全部根因日志
        :return:
        """
        root_logs = self.session.query(FaultServiceRoot).filter(FaultServiceRoot.type == 1,
                                                      FaultServiceRoot.has_solution == 0).all()
        return root_logs

    def update_root_detail_table_has_solutuon(self,fault_id,log_id):
        """
        将已经生成修复方案的根因日志的has_solution字段更新为1
        :return:
        """
        result = self.session.query(FaultServiceRoot).filter(FaultServiceRoot.fault_id == fault_id,
                                                   FaultServiceRoot.causeOfFault == log_id).update(
            FaultServiceRoot.has_solution == 1)
        return result

    def insert_fault_service_into_fault_service_table(self,serviceId,serviceName,serviceType,hostName):
        """
        插入新的故障服务在故障服务详情表
        :param serviceId:
        :param serviceName:
        :param serviceType:
        :param hostName:
        :return:
        """
        fault_service = FaultService(fault_service_id = serviceId, fault_service_name = serviceName,
                                     fault_service_type = serviceType, host_name = hostName,
                                     exception_time=datetime.datetime.now(), process_state=0)
        self.session.add(fault_service)
        self.db_commit()
        return fault_service

    def insert_fault_service_root_into_fault_service_root_table(self, fault_id, root_id, name, detail,type,rank):
        service_falut_root = FaultServiceRoot(fault_id=fault_id, causeOfFault=root_id, causeName=name,
                                              detail=detail, has_solution=0, type=type,
                                              rank=rank)
        self.session.add(service_falut_root)
        return service_falut_root

    def insert_service_dependency_graph_into_service_dependency_graph_table(self, fault_id, fault_service_dependency_graph_json):
        service_dependency_graph = ServiceDependencyGraph(fault_id=fault_id,
                                                          graph_json=fault_service_dependency_graph_json)
        self.session.add(service_dependency_graph)
        return service_dependency_graph

    def insert_exception_data_dependency_graphh_into_exception_data_dependency_graph_table(self, fault_id, service_exception_data_dependency_graph_json):
        exception_data_dependency_graph = ExceptionDataDependencyGraph(fault_id=fault_id,
                                                                       graph_json=service_exception_data_dependency_graph_json)
        self.session.add(exception_data_dependency_graph)
        return exception_data_dependency_graph
    def insert_fault_service_solution_insert_fault_service_solution_table(self,fault_id,log_id,fault_reason,fault_solution,rank):
        faultServiceSolution = FaultServiceSolution(fault_id=fault_id, root_log_id=log_id, fault_reason=fault_reason,
                                                fault_solution=fault_solution, rank=rank)
        self.session.add(faultServiceSolution)
        return faultServiceSolution

    def select_all_fault_service_detail_by_processState(self,process_state):
        fault_service_list =  self.session.query(FaultService).filter(FaultService.process_state == process_state).all()
        return fault_service_list

    def select_rank1_faultserviceroot_by_faultid(self,fault_id):
        root = self.session.query(FaultServiceRoot).filter(FaultServiceRoot.fault_id == fault_id).order_by(
            FaultServiceRoot.rank.desc()).first()
        return root
    def select_service_invoke_graph_by_faultid(self,fault_id):
        service_invoke_graph_json = self.session.query(ServiceDependencyGraph).filter(
            ServiceDependencyGraph.fault_id == fault_id).first()
        return service_invoke_graph_json

    def select_exception_data_dependency_graph_by_faultid(self,fault_id):
        exception_data_dependency_graph_json = self.session.query(ExceptionDataDependencyGraph).filter(
            ExceptionDataDependencyGraph.fault_id == fault_id).one()
        return exception_data_dependency_graph_json
    def get_root_log_by_logid_and_faultid(self,fault_id,log_id):
        root_log = self.session.query(FaultServiceRoot).filter(FaultServiceRoot.fault_id == fault_id,
                                                   FaultServiceRoot.causeOfFault == log_id).first()
        return root_log

    def select_solutions_by_logid_and_faultid(self,fault_id,log_id):
        solutions = self.session.query(FaultServiceSolution).filter(FaultServiceSolution.fault_id == fault_id,FaultServiceSolution.root_log_id == log_id).order_by(FaultServiceSolution.rank.asc()).all()
        return solutions
