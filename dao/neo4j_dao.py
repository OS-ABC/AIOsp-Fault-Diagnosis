import logging

from py2neo import Graph


class GraphDao:

    def __init__(self):
        self.g = Graph(
            host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            http_port=7474,  # neo4j 服务器监听的端口号
            user="neo4j",  # 数据库user name，如果没有更改过，应该是neo4j
            password="neo4j")
        # self.num_limit = 20

    def execute_sql(self, sql):
        answer = None
        try:
            answer = self.g.run(sql).data()
        except:
            logging.error("execute sql failed, sql: {0}".format(sql))
        return answer

    def get_all__entities(self):
        sql = 'MATCH (n) return n'
        result = self.execute_sql(sql)
        return [i['n'] for i in result]

    ##故障修复知识图谱

    # def get_all_log_entities(self):
    #     sql = 'MATCH (n:log) return n'
    #     result = self.execute_sql(sql)
    #     return [i['n'] for i in result]

    #获取图谱log节点
    def get_all_log_entities(self):
        result = self.g.run("match (n:log) return n").data()
        return result

    #根据log获取故障节点列表
    def get_fault_entity_by_log(self, log_name):
        sql = 'MATCH (x:fault)-[r:has_log]->(y:log) where y.name = "{0}" return x'.format(
            log_name)
        result = self.execute_sql(sql)
        return [i['x'] for i in result]
    #根据falut获取解决方案列表
    def get_solutions_by_fault(self, fault_name):
        sql = 'MATCH (x:fault)-[r:has_solution]->(y:solution) where x.name = "{0}" return y'.format(
            fault_name)
        result = self.execute_sql(sql)
        return [i['y'] for i in result]

    #根据falut获取原因列表
    def get_reasons_by_fault(self, fault_name):
        sql = 'MATCH (x:fault)-[r:has_reason]->(y:reason) where x.name = "{0}" return y'.format(
            fault_name)
        result = self.execute_sql(sql)
        return [i['y'] for i in result]

    #根据原因获取解决方案列表
    def get_solutions_by_reason(self, reason_name):
        sql = 'MATCH (x:reason)-[r:has_solution]->(y:solution) where x.name = "{0}" return y'.format(
            reason_name)
        result = self.execute_sql(sql)
        return [i['y'] for i in result]