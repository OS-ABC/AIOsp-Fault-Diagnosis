from elasticsearch import Elasticsearch


class ESConnection:
    def __init__(self, hosts):
        self.hosts = hosts
        self.es = Elasticsearch(hosts=hosts)

    def query(self, index, query):
        data = self.es.search(body=query, index=index, params={"scroll": "10m", "size": 10000})
        result = data['hits']['hits']
        total = data['hits']['total']['value']
        scroll_id = data['_scroll_id']

        for i in range(0, int(total / 10000) + 1):
            query_scroll = self.es.scroll(scroll_id=scroll_id, params={"scroll": "1m"})['hits']['hits']
            result += query_scroll

        return result