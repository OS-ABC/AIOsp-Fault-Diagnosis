from bean.output_model import FaultServiceDetail
from dao.db_dao import DBDao
from service.module_tools.genarate_solutions import GenetateSolutuons
from service.module_tools.save_result import SaveResult


def get_fault_service_list():
    """
    查询所有故障服务数据，按时间从高到底排序，分为已处理和未处理两列
    :return:
    """
    dbDao = DBDao()
    fault_service_list_unprocess = dbDao.select_all_fault_service_detail_by_processState(0)
    fault_service_list_process = dbDao.select_all_fault_service_detail_by_processState(1)
    fault_service_detail_list_unprocess = list()
    fault_service_detail_list_process = list()
    for fault_service in fault_service_list_unprocess:
        root = dbDao.select_rank1_faultserviceroot_by_faultid(fault_service.id)
        if root:
            faultServiceDetail = FaultServiceDetail(fault_service.id, fault_service.fault_service_name,
                                                    fault_service.host_name, root.causeName,
                                                    fault_service.exception_time)
            fault_service_detail_list_unprocess.append(faultServiceDetail)

    for fault_service in fault_service_list_process:
        root = dbDao.select_rank1_faultserviceroot_by_faultid(fault_service.id)
        if root:
            faultServiceDetail = FaultServiceDetail(fault_service.id, fault_service.fault_service_name,
                                                    fault_service.host_name, root.causeName,
                                                    fault_service.exception_time)
            fault_service_detail_list_process.append(faultServiceDetail)
    dbDao.db_close()
    return [dict(i) for i in fault_service_detail_list_unprocess], [dict(i) for i in fault_service_detail_list_process]


# def get_fault_service_detail(fault_id):
#     """
#     查询某一故障服务诊断详情，此接口返回数据包含诊断时的服务依赖图、故障服务对应详细信息
#     :param fault_id:
#     :return:
#     """

# """
# 按faultId查询故障详细内容
# """
#
#
# def get_fault_id(fault_id):
#     fault = None
#     db = get_session()
#     if fault_id:
#         fault = db.query(Fault).filter(Fault.id == fault_id).one()
#     db.close()
#     return fault.to_dict()


def get_service_invoke_graph(fault_id):
    """
    根据故障服务编号查询对应的服务依赖图
    :param fault_id:
    :return:
    """
    service_invoke_graph_json = None
    dbDao = DBDao()
    if fault_id:
        service_invoke_graph_json = dbDao.select_service_invoke_graph_by_faultid(fault_id)
    dbDao.db_close()
    if service_invoke_graph_json == None:
        return None
    return service_invoke_graph_json.to_dict()


def get_exception_data_dependency_graph(fault_id, service_id):
    """
    根据fault_id查询服务异常数据依赖图
    :param fault_id:
    :param service_id:
    :return:
    """
    exception_data_dependency_graph_json = None
    dbDao = DBDao()
    if fault_id and service_id:
        exception_data_dependency_graph_json = dbDao.select_exception_data_dependency_graph_by_faultid(fault_id)
    dbDao.db_close()
    return exception_data_dependency_graph_json.to_dict()


def get_solutions_by_log(fault_id, log_id, log_detail):
    """
    获取根因日志的解决方案
    :param fault_id:
    :param log_id:
    :param logDetail:
    :return:
    """
    dbDao = DBDao()
    root_log = dbDao.get_root_log_by_logid_and_faultid(fault_id,log_id)
    if root_log.has_solution == 0:
        sorted_solutions = GenetateSolutuons.get_solutions_by_logDetail(log_detail)
        result = SaveResult.save_solutions(root_log.fault_id, root_log.causeOfFault, sorted_solutions)
    solutions = dbDao.select_solutions_by_logid_and_faultid(fault_id,log_id)
    dbDao.db_close()
    return [i.to_dict() for i in solutions]
