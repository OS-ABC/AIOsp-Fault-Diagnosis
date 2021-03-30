import logging
from copy import deepcopy

from flask import Flask, request, json, jsonify,make_response

from service.web_service import get_fault_service_list, get_service_invoke_graph, get_exception_data_dependency_graph, \
    get_solutions_by_log

app = Flask(__name__, static_folder='static', template_folder='templates')

# @app.route("/fault_diagnosis", methods=['POST'])  #请求方式为post
# def fault_diagnosis():
#     data = request.data
#     j_data = json.loads(data)
#     sys_rca(j_data)

result_response = {'code': 1, 'message': 'success', 'data': None}

@app.route("/fault_service_list", methods=['GET'])  # 请求方式为get
def fault_service_list():
    response = deepcopy(result_response)
    try:
        fault_list_unprocess, fault_list_process = get_fault_service_list()
        response['data'] = {'fault_list_unprocess': fault_list_unprocess, 'fault_list_process': fault_list_process}
    except Exception as  e:
        response['code'] = 0
        response['message'] = str(e)
    res = make_response(jsonify(response))  # 设置响应体
    # res.status = '200'  # 设置状态码
    res.headers['Access-Control-Allow-Origin'] = "*"  # 设置允许跨域
    res.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    return res


@app.route("/fault_service_invoke_graph", methods=['GET'])  # 请求方式为get
def fault_service_invoke_graph():
    response = deepcopy(result_response)
    try:
        fault_id = request.args['fault_id']
        # input_data = json.loads(data)
        service_invoke_graph_json = get_service_invoke_graph(fault_id)
        # service_invoke_graph = json.loads(service_invoke_graph_json)
        response['data'] = {'service_invoke_graph': service_invoke_graph_json}
    except Exception as  e:
        response['code'] = 0
        response['message'] = str(e)
    return jsonify(response)


@app.route("/exception_data_dependency_graph", methods=['GET'])  # 请求方式为get
def exception_data_dependency_graph():
    response = deepcopy(result_response)
    try:
        fault_id = request.args['fault_id']
        service_id = request.args['service_id']
        # input_data = json.loads(data)
        log_metric_graph_json = get_exception_data_dependency_graph(fault_id, service_id)
        # log_metric_graph = json.loads(log_metric_graph_json)
        response['data'] = {'log_metric_graph': log_metric_graph_json}
    except Exception as e:
        response['code'] = 0
        response['message'] = str(e)
    res = make_response(jsonify(response))  # 设置响应体
    # res.status = '200'  # 设置状态码
    res.headers['Access-Control-Allow-Origin'] = "*"  # 设置允许跨域
    res.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    return res


@app.route("/root_log_solutions", methods=['POST'])  # 请求方式为get
def fault_logDetail_solutions():
    response = deepcopy(result_response)
    try:
        fault_id = request.form['fault_id']
        log_id = request.form['log_id']
        log_detail = request.form['log_detail']
        solutions = get_solutions_by_log(fault_id,log_id,log_detail)
        response['data'] = {'fault_id': fault_id, 'log_id': log_id,'log_detail':log_detail,'solutions':solutions}
    except Exception as e:
        response['code'] = 0
        response['message'] = str(e)
    res = make_response(jsonify(response))  # 设置响应体
    # res.status = '200'  # 设置状态码
    res.headers['Access-Control-Allow-Origin'] = "*"  # 设置允许跨域
    res.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    return res


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    # 跨域支持
    # def after_request(response):
    #     # JS前端跨域支持
    #     response.headers['Cache-Control'] = 'no-cache'
    #     response.headers['Access-Control-Allow-Origin'] = '*'
    #     return response
    #
    # app.after_request(after_request)
