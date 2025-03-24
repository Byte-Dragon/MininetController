import requests

def req(url, data=None, headers=None):
    data = data if data is not None else {}
    if headers is None:
        headers = {
            "Content-Type": "application/json"
        }
    response = requests.post(url, json=data, headers=headers)
    return response.status_code, response.text

def req_add_link(n):
    result = []
    for i in range(n):
        data = {"fromNode":f"h-{i}", "toNode":"s1","params":{"delay":5,"bw": 10}}
        code, mes = req("http://localhost:8080/api/links/add", data=data)
        result.append(f"req_add_link_{i}: return:[ {code}, {mes} ]")
    return result
    
def req_del_link(n):
    result = []
    for i in range(n):
        data = {"fromNode":f"h-{i}", "toNode":"s1"}
        code, mes = req("http://localhost:8080/api/links/del", data=data)
        result.append(f"req_del_link_{i}: return:[ {code}, {mes} ]")
    return result
    
def ping():
    result = []

    data1 = {"host1":"h1","host2":"h-1","get_full":False}
    data2 = {"host1":"h-1","host2":"h-2","get_full":False}
    code, mes = req("http://localhost:8080/api/nodes/ping", data=data1)
    result.append(f"req_ping_1: return:[ {code}, {mes} ]")
        
    code, mes = req("http://localhost:8080/api/nodes/ping", data=data2)
    result.append(f"req_ping_2: return:[ {code}, {mes} ]")
    return result

def req_add_host(n):
    result = []
    for i in range(n):
        data = {"name":f"h-{i}", "ip":f"10.0.1.{i}/24"} 
        code, mes = req("http://localhost:8080/api/nodes/add/host", data=data)
        result.append(f"req_add_host_{i}: return:[ {code}, {mes} ]")
    return result
    
def req_del_host(n):
    result = []
    for i in range(n):
        resp = requests.delete(f"http://localhost:8080/api/nodes/del/h-{i}")
        result.append(f"req_del_host_{i}: return:[{resp.status_code} {resp.text} ]")
    return result
    
def req_stop_host(n):
    result = []
    for i in range(n):
        data = {"name":f"h-{i}","keep_config":True}
        code, mes = req("http://localhost:8080/api/nodes/stop/host", data=data)
        result.append(f"req_stop_host_{i}: return:[ {code}, {mes} ]")
    return result
    
def req_start_host(n):
    result = []
    for i in range(n):
        data = {"name":f"h-{i}"}
        code, mes = req("http://localhost:8080/api/nodes/start/host", data=data)
        result.append(f"req_start_host_{i}: return:[ {code}, {mes} ]")
    return result  
    
def req_config(n):
    result = []
    headers = {
            "Content-Type": "application/json"
    }
    for i in range(n):
        data = {"links": [{"from": f"h-{i}","to": "s1","params": {"delay":5+i, "bandwidth":100+i}}]}
        req= requests.put("http://localhost:8080/api/config", json=data, headers=headers)
        result.append(f"req_config_{i}: return:[ {req.status_code}, {req.text} ]")
    return result  
    
def main(n):
    while True:
        # 获取用户输入
        user_input = input("请输入数字（0、1、2、3）选择方法，输入-1退出：\n0、启动节点，1、添加节点，2、删除节点，3、停止节点，4、添加链路，5、删除链路，6、config，7、ping\n")
        
        # 判断输入是否为数字
        if user_input.lstrip('-').isdigit():
            choice = int(user_input)
            
            # 根据输入执行对应的方法
            if choice == 0:
                print(req_start_host(n))
            elif choice == 1:
                print(req_add_host(n))
            elif choice == 2:
                print(req_del_host(n))
            elif choice == 3:
                print(req_stop_host(n))
            elif choice == 4:
                print(req_add_link(n))
            elif choice == 5:
                print(req_del_link(n))
            elif choice == 6:
                print(req_config(n))
            elif choice == 7:
                print(ping())
            
            elif choice == -1:
                print("退出程序")
                break
            else:
                print("无效的输入，请重新输入")
        else:
            print("无效的输入，请输入数字")
if __name__ == "__main__":
    n = 10
    main(n)
    #print(req_add_host(n))
    #print(req_add_link(n))
    #print(req("http://localhost:8080/api/network/ping"))
    #print(req_del_host(n))
    #print(req_del_link(n))
    #print(req("http://localhost:8080/api/network/ping"))
    #print(req_stop_host(n))


