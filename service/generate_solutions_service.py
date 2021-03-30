from dao.db_dao import DBDao
from service.module_tools.genarate_solutions import GenetateSolutuons
from service.module_tools.save_result import SaveResult


def time_generate_logs_solutions():
    """
    为根因详情列表中未生成修复方案的所有根因日志生成解决方案
    :return:
    """
    dbDao = DBDao()
    root_logs = dbDao.get_all_root_logs_noSolution()
    dbDao.db_close()
    result = None
    for root_log in root_logs:
        sorted_solutions = GenetateSolutuons.get_solutions_by_logDetail(root_log.detail)
        result = SaveResult.save_solutions(root_log.fault_id, root_log.causeOfFault, sorted_solutions)
    return result



