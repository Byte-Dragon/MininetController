from flask import Flask, request, jsonify
from controller import MininetController
from main_topology import myNetwork
import traceback
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import argparse
from datetime import datetime
import time


# 配置日志相关设置
# 创建日志目录
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def configure_logging(app):
    # 基础日志配置
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    
    # 1. 应用程序日志（按天滚动）
    app_log_handler = TimedRotatingFileHandler(
        filename=os.path.join(LOG_DIR, 'app.log'),
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    app_log_handler.setFormatter(formatter)
    app_log_handler.setLevel(logging.INFO)

    # 2. 错误日志（按文件大小滚动）
    error_log_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(LOG_DIR, 'error.log'),
        maxBytes=1024*1024*10,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_log_handler.setFormatter(formatter)
    error_log_handler.setLevel(logging.ERROR)

    # 3. 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    # 获取Flask的logger并配置
    logger = logging.getLogger('werkzeug')
    logger.handlers.clear()  # 移除默认handler
    logger.addHandler(app_log_handler)
    logger.addHandler(error_log_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

    # 添加自定义应用logger
    app.logger.handlers.clear()
    app.logger.addHandler(app_log_handler)
    app.logger.addHandler(error_log_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)

app = Flask(__name__)
configure_logging(app)
#app.config['JSON_AS_ASCII'] = False

# 配置跨域请求
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 配置日志输出
@app.before_request
def log_request_start():
    request.start_time = time.time()
    app.logger.info(
        f"Request Started | {request.method} {request.path} "
        f"| Client: {request.remote_addr} "
        f"| Params: {dict(request.args)} "
        f"| JSON: {request.json if request.content_type == 'application/json' else None}"
    )

@app.after_request
def log_request_end(response):
    duration = round((time.time() - request.start_time) * 1000, 2)  # 毫秒
    app.logger.info(
        f"Request Completed | {request.method} {request.path} "
        f"| Status: {response.status_code} "
        f"| Duration: {duration}ms"
    )
    return response

# 定义一个统一的响应格式
def format_response(success, message=None, data=None, status_code=200):
    response = {
        "success": success,
        "code": status_code,
        "message": message,
        "data": data
    }
    import json
    json_response = json.dumps(response, ensure_ascii=False)
    return json_response, status_code

# 异常处理装饰器
def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            app.logger.error(
                f"API Exception: {str(e)}\n"
                f"Request: {request.method} {request.path}\n"
                f"Traceback:\n{tb}"
            )
            return format_response(False, f"Internal Server Error: {str(e)}", None, 500)
    wrapper.__name__ = func.__name__
    return wrapper


# app running 
controller = None

@app.route('/api/network/init', methods=['POST'])
def init_network():
    global controller
    current_net = controller.net
    data = request.get_json()
    success, mes, code = controller.set_net_from_topo(data, build=False)
    return format_response(success, mes, None, code)


@app.route('/api/network/start', methods=['POST'])
@handle_exceptions
def start_network():
    global controller
    controller.start_network()
    success = "Network started successfully"
    return format_response(True, success)

@app.route('/api/network/stop', methods=['POST'])
@handle_exceptions
def stop_network():
    controller.stop_network()
    success = "Network stopped successfully"
    return format_response(True, success)

@app.route('/api/network/topology', methods=['GET'])
@handle_exceptions
def get_topology():
    topology = controller.get_topology()
    success = "Topology retrieved"
    return format_response(True, success, topology)

@app.route('/api/nodes/ping', methods=['POST'])
@handle_exceptions
def ping_between_hosts():
    data = request.json
    if 'host1' not in data or 'host2' not in data:
        failed = "Missing required parameters: host1 and host2"
        app.logger.debug(failed)
        return format_response(False, failed, None, 400)
    timeout = data['timeout'] if 'timeout' in data else None
    get_full = data['get_full'] if 'get_full' in data else False
    
    # 是否返回完整的ping信息
    if get_full:
        result = controller.ping_full(data['host1'], data['host2'], timeout=timeout)
    else:
        result = controller.ping(data['host1'], data['host2'], timeout=timeout)
    return format_response(True, "Ping test completed",
        {
            'type': 'host-between-hosts',
            'get_full': get_full,
            'result': result
        })

@app.route('/api/nodes/ping/ip', methods=['POST'])
@handle_exceptions
def ping_to_ip():
    """测试主机到外部IP的连通性"""
    data = request.json
    required = ['host', 'ip']
    
    if not all(k in data for k in required):
        msg = f"Missing required parameters: {required}"
        app.logger.debug(msg)
        return format_response(False, msg, None, 400)
    result = controller.ping_ip(data['host'], data['ip'])
    return format_response(
        True, 
        "Host-to-IP ping completed", 
        {
            'type': 'host-to-ip',
            'result': result
        })

@app.route('/api/network/ping', methods=['POST'])
@handle_exceptions
def ping_all_hosts():
    """测试所有主机间的连通性"""
    data = request.json or {}
    
    params = {
        'timeout': data.get('timeout',None),
        'get_full': data.get('get_full', False)
    }

    if params['get_full']:
        result = controller.ping_all_full(params['timeout'])
    else:
        result = controller.ping_all(params['timeout'])      
    return format_response(True, "Full network ping completed", {
            'type': 'all-hosts',
            'full_data': params['get_full'],
            'result': result
        })
    
@app.route('/api/nodes/start/<node_type>', methods=['POST'])
@handle_exceptions
def start_node(node_type):
    # node_type = None
    data = request.json
    node_name = data.get('name',None)
    success, message = controller.start_node(node_name, node_type)
    if success:
        return format_response(True, message)
    app.logger.debug(message)
    return format_response(False, message, None, 400)

@app.route('/api/nodes/stop/<node_type>', methods=['POST'])
@handle_exceptions
def stop_node(node_type):
    data = request.json
    keep_config = data.get('keep_config', True)
    node_name = data.get('name', None)
    success, message = controller.stop_node(node_name, node_type, keep_config)
    if success:
        return format_response(True, message)
    app.logger.debug(message)
    return format_response(False, message, None, 400)

@app.route('/api/nodes/add/<node_type>', methods=['POST'])
@handle_exceptions
def add_node(node_type):
    data = request.json
    if 'name' not in data:
        failed = "Missing required parameters: name"
        app.logger.debug(failed)
        return format_response(False, failed, None, 400)
    node_name = data['name']
    # 先验证该名字是否存在，不允许重复的名字
    node = controller.get_node_by_name(node_name)
    if node is not None:
        # 重复直接返回
        failed = "Duplicate names are not allowed, please re-request"
        app.logger.debug(failed)
        return format_response(False, failed, None, 400)
    if node_type == 'host':
        if 'ip' not in data:
            failed = "Missing required parameters:ip"
            app.logger.debug(failed)
            return format_response(False, failed, None, 400)
        link_to = data['link_to'] if 'link_to' in data else None
        success, data = controller.add_host(data['name'], data['ip'], link_to = link_to)
        code = 200 if success else 400
        mes = "Host added successfully" if success else "Fail to add Host"
        return format_response(success, mes, data, code)
    
    elif node_type == 'switch':
        out = "Switch added successfully! "
        if 'ip' in data:
            out += f"Invalid payload:'ip'={data['ip']},which will not be applied"
        data = controller.add_switch(data['name'], **data.get('params', {}))
        return format_response(True, out, data=data)
    app.logger.debug("Invalid node type")
    return format_response(False, "Invalid node type", None, 400)

@app.route('/api/nodes/del/<node_name>', methods=['DELETE'])
@handle_exceptions
def delete_node(node_name):
    success, message = controller.del_node(node_name)
    if success:
        return format_response(True, message)
    app.logger.debug(message)
    return format_response(False, message, None, 404)

@app.route('/api/links/add', methods=['POST'])
@handle_exceptions
def create_link():
    data = request.json
    required = ['fromNode', 'toNode']
    if not all(k in data for k in required):
        app.logger.debug("Create link failed: Missing required parameters<fromNode, toNode>")
        return format_response(False, "Create link failed: Missing required parameters<fromNode, toNode>", None, 400)
    new_link = controller.add_link(data['fromNode'], data['toNode'], **data.get('params'))
    if new_link is not None:
        return format_response(True, "Link created successfully")
    else:
        app.logger.debug("Create link failed: Unexpected error accured")
        return format_response(False, "Create link failed: Unexpected error accured", None, 500)

@app.route('/api/links/del', methods=['POST'])
@handle_exceptions
def remove_link():
    data = request.json
    required = ['fromNode', 'toNode']
    if not all(k in data for k in required):
        app.logger.debug("Remove link failed: Missing required parameters<fromNode, toNode>")
        return format_response(False, "Remove link failed: Missing required parameters<fromNode, toNode>", None, 400)
    
    success, message = controller.del_link(data['fromNode'], data['toNode'], data.get('intf', None))
    if success:
        return format_response(True, message)
    app.logger.debug(message)
    return format_response(False, message, None, 404)

@app.route('/api/config', methods=['PUT'])
@handle_exceptions
def apply_config():
    # 有可能出现只成功更新部分参数的情况，这里简要记录一下，暂不做事务处理功能
    config = request.json
    results = controller.apply_params(config)
    for result in results:
        success, message = result
        if not success:
            app.logger.debug(message)
    return format_response(True, "Configuration applied", {"results": results})

@app.route('/api/controllers', methods=['PUT'])
@handle_exceptions
def update_controller():
    data = request.json
    required = ['switch', 'controller']
    if not all(k in data for k in required):
        app.logger.debug("Set controller for Switch failed: Missing required parameters<switch, controller>")
        return format_response(False, "Set controller for Switch failed: Missing required parameters<switch, controller>", None, 400)
    
    success, message = controller.set_controller(
        data['switch'], 
        data['controller'],
        restart=data.get('restart', True),
        keep_links=data.get('keep_links', True)
    )
    if success:
        return format_response(True, message)
    app.logger.debug(message)
    return format_response(False, message, None, 400)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Flask app with custom arguments')
    parser.add_argument('--cli', type=bool, help='run with param --CLI will open a mininet CLI window')
    args = parser.parse_args()

    cli = args.cli if args.cli else False
    net = myNetwork(cli=cli)
    controller = MininetController(net)
    app.run(host='127.0.0.1', port=8080)
    controller.stop_network()
    
