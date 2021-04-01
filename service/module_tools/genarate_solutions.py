import re

from dao.neo4j_dao import GraphDao
from utils.jaccard_api import log_preprocess, generate_cidian_jaccard

paramregex = [r'blk_-?\d+', r'(\d+\.){3}\d+(:\d+)?', r'(\d+\.){3}\d+', r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)',
              r'(?<=[^A-Za-z0-9])(\-?\+?\d+)(?=[^A-Za-z0-9])|[0-9]+$']
stopkeyword = [line.strip() for line in open('config/stop.txt').readlines()]
eraseRex = [r'(\d+\-){2}\d+\s\d+\:\d+\:\d+\,\d+', r'INFO', r'ERROR', r'DEBUG', r'WARN', r'FATAL']

class GenetateSolutuons:
    @staticmethod
    def get_solutions_by_logDetail(log_detail):
        """
        生成异常日志片段对应的解决方案列表
        :param log_detail:
        :return: 排好序的解决方案列表
        """
        logs_dictionaries = GenetateSolutuons.get_fault_repair_graph_dictionary_log()
        logs_with_jaccard = GenetateSolutuons.logDetail_graph_cache_jaccard(log_detail, logs_dictionaries)

        # jaccard 日志按相似度大小进行排序
        logs_with_jaccard_sort = sorted(logs_with_jaccard.items(), key=lambda x: x[1]['jaccard'], reverse=True)
        # 取前 5 name
        top_name = [item[1]['name'] for item in logs_with_jaccard_sort[:5]]
        solutions = {}

        graph_dao = GraphDao()
        for name in top_name:
            if len(solutions) < 5:
                solutions_tmp = {}
                faults = graph_dao.get_fault_entity_by_log(name)
                for fault in faults:
                    solutions_zhijie = graph_dao.get_solutions_by_fault(fault['name'])
                    reasons = graph_dao.get_reasons_by_fault(fault['name'])
                    for reason in reasons:
                        solutions_jianjie = graph_dao.get_solutions_by_reason(reason['name'])
                        for solution_jianjie in solutions_jianjie:
                            solutions_tmp[solution_jianjie['name']] = {}
                            solutions_tmp[solution_jianjie['name']]['reason'] = reason['content']
                            solutions_tmp[solution_jianjie['name']]['html_content'] = solution_jianjie['html_content']
                            solutions_tmp[solution_jianjie['name']]['json_content'] = solution_jianjie['json_content']
                            solutions_tmp[solution_jianjie['name']]['vote'] = solution_jianjie['vote']
                        pass
                    for solution_zhijie in solutions_zhijie:
                        solutions_tmp[solution_zhijie['name']] = {}
                        solutions_tmp[solution_zhijie['name']]['reason'] = "暂无"
                        solutions_tmp[solution_zhijie['name']]['html_content'] = solution_zhijie['html_content']
                        solutions_tmp[solution_zhijie['name']]['json_content'] = solution_zhijie['json_content']
                        solutions_tmp[solution_zhijie['name']]['vote'] = solution_zhijie['vote']
                # 根据投票数排序
                solutions_tmp_sort = sorted(solutions_tmp.items(), key=lambda x: x[1]['vote'], reverse=True)
                for solution_tmp in solutions_tmp_sort:
                    if len(solutions) < 5:
                        solutions[solution_tmp[0]] = {}
                        solutions[solution_tmp[0]]['reason'] = solution_tmp[1]['reason']
                        solutions[solution_tmp[0]]['html_content'] = solution_tmp[1]['html_content']
                        solutions[solution_tmp[0]]['json_content'] = solution_tmp[1]['json_content']
                        solutions[solution_tmp[0]]['vote'] = solution_tmp[1]['vote']
                        solutions[solution_tmp[0]]['serial_number'] = len(solutions)
            else:
                break
        solutions_sort = sorted(solutions.items(), key=lambda x: x[1]['serial_number'])
        result_solutions = []
        for solution_sort in solutions_sort:
            result_solution = {}
            result_solution['reason'] = solution_sort[1]['reason']
            result_solution['html_content'] = solution_sort[1]['html_content']
            result_solution['json_content'] = solution_sort[1]['json_content']
            result_solution['vote'] = solution_sort[1]['vote']
            result_solution['serial_number'] = solution_sort[1]['serial_number']
            result_solutions.append(result_solution)
        return result_solutions

    @staticmethod
    def logDetail_graph_cache_jaccard(yichanglog, graph_cache):
        """
        根因日志异常片段与图谱中全部日志相似度计算
        :param yichanglog:
        :param graph_cache:
        :return: dict {图谱中日志名称:相似度值}
        """
        result_dict = {}
        log_ = log_preprocess(yichanglog, paramregex, eraseRex)
        log1_dic = generate_cidian_jaccard(log_, stopkeyword)

        for name, log2_dic in graph_cache.items():
            dict = {}
            bingji = list(set(log1_dic).union(set(log2_dic)))
            jiaoji = list(set(log1_dic).intersection(set(log2_dic)))
            jiaquan = 0
            for word in jiaoji:
                if re.search(r'[a-zA-Z0-9]+.[a-zA-Z0-9]+.[a-zA-Z0-9]+Exception', word):
                    jiaquan += 5
            jaccard = (len(jiaoji) + jiaquan) / len(bingji)
            dict['name'] = name
            dict['dict'] = log2_dic
            dict['jaccard'] = jaccard
            result_dict[name] = dict
        return result_dict

    @staticmethod
    def get_fault_repair_graph_dictionary_log():
        """
        获取图谱中所有日志的分词结果
        :return:
        """
        graph_dao = GraphDao()
        logs = graph_dao.get_all_log_entities()
        graph_cache_jaccard = GenetateSolutuons.generate_graph_cache_jaccard(logs, paramregex, eraseRex, stopkeyword)
        return graph_cache_jaccard

    @staticmethod
    def generate_graph_cache_jaccard(graph_logs, paramregex, eraseRex, stopkeyword):
        """
        生成图谱中所有日志的分词结果
        :param graph_logs:
        :param paramregex:
        :param eraseRex:
        :param stopkeyword:
        :return:
        """
        graph_cache_jaccard = {}
        for log in graph_logs:
            log_ = log_preprocess(log['n']['content'], paramregex, eraseRex)
            log_dict = generate_cidian_jaccard(log_, stopkeyword)
            graph_cache_jaccard[log['n']['name']] = log_dict
        return graph_cache_jaccard