# MininetController

## 项目结构
```markdown
MininetContoller/
├── README.md
├── README-CN.md            # 中文README文件
├── run_mininet_env(CN).txt # 中文的Mininet控制命令列表
├── data_handler/           # 实现对JSON数据文件的简单读写操作
│   ├── config.json         # JSON数据文件
│   └── json_handler.py     # 实现对JSON数据的简单读写以及发送到指定IP
├── src/
│   ├── app.py              # 一个简单的Flask应用，将controller.py中的方法封装成HTTP请求供前端访问
│   ├── controller.py       # 主控制类，实现了一系列Mininet控制和访问逻辑，封装了Mininet net类的常用方法
│   └── main_topology.py    # 拓扑类，创建由主机、交换机、控制器和链路组成的拓扑，并返回相应的Mininet net对象
└── logs/                   # 日志文件目录
    ├── app.log
    └── error.log
```

---

## 项目介绍

### 主要内容
该项目主要为网络模拟工具Mininet开发了一个控制器以及相应的Flask服务程序，并记录了Flask服务器的运行过程。

### MininetController是如何工作的？
MininetController使用Mininet进行网络模拟，使用Ryu控制器进行交换机仿真。

### 依赖项
* 运行`sudo pip install --no-cache-dir -r requirements.txt`
* 或者手动安装依赖项
* Python 3.8.10
* Flask 3.0.3
  * `sudo pip install flask`
  * `sudo pip install flask-cors`
* Mininet 2.3.0.dev6
  * `sudo apt-get install mininet`
  * `sudo pip install mininet`                            # Python API

### 快速开始
* 克隆仓库
  * `git clone https://github.com/MemorialAndUnique/MininetController.git`
* 进入克隆的仓库
  * `cd MininetController/src`
* 运行`sudo ryu-manager --verbose ryu.app.simple_switch`   # 启动远程ryu控制器
* 运行`sudo python3 app.py`                                # 运行flask应用，运行在(127.0.0.1:8080)
  * 或者运行`sudo python3 app.py --cli True`                # 在运行flask应用的同时打开mininet命令行（可能会导致bug）
* 使用Ctrl+C停止服务器
* 模拟结束后，运行`sudo mn -c`                       # 清理创建的mininet拓扑

---

## 基本操作
* 启动/停止整个网络
* 启动/停止节点（主机/交换机/控制器）
* 获取运行网络的拓扑（返回格式化的JSON数据）
* 添加主机/交换机
* 添加链路
* 删除主机/交换机
* 删除链路
* 更改节点/交换机/链路的配置参数
* 使用ping工具
  * 主机之间的'Ping/PingFull'（返回完整数据，可选）
  * 'Ping IP (str) on a host'（在主机上ping指定IP）
  * 'PingAll/PingAllFull'（返回完整数据，可选）
* 为交换机S设置一个新的控制器（Controller或RemoteController的实例）

---

## 主要API列表

| 终端 | 方法 | 参数 | 描述 |
| ---- | ---- | ---- | ---- |
| `/api/network/start` | POST | 无 | 启动整个网络 |
| `/api/network/stop` | POST | 无 | 停止整个网络，除非你完成了模拟，否则不要运行此方法 |
| `/api/network/topology` | GET | 无 | 获取网络拓扑 |
| `/api/nodes/ping` | POST | `{ "host1": "h1", "host2": "h2", "get_full": false (可选，默认false), "timeout": "10"(可选，默认None) }` | 测试主机之间的连通性 |
| `/api/nodes/ping/ip` | POST | `{ "host": "h1", "ip": "10.0.0.8" }` | 测试主机到IP的连通性 |
| `/api/network/ping` | POST | `{ "timeout": "10"(可选，字符串), "get_full": false (可选，默认false) }` | 测试整个网络的连通性 |
| `/api/nodes/add/<node_type>` | POST | 对于主机：`{ "name": string, "ip": string,"link_to":string(可选，表示主机初始化时连接到哪个交换机，默认连接s1)}` 对于交换机：`{ "name": string }` | 添加一个节点 | 交换机的名称必须是“s1”或“中国01”这种形式，数字“1”在“s1”中将是交换机的id
| `/api/nodes/del/<node_name>` | DELETE | 无 | 删除一个节点 |
| `/api/links/add` | POST | `{ "fromNode": string, "toNode": string, "params": object }` | 创建一个链路 |
| `/api/links/del` | POST | `{ "fromNode": string, "toNode": string,"intf":string(可选，链路连接的两个网络接口名字之一) }` | 删除一个链路 |
| `/api/config` | PUT | 配置对象 | 应用网络配置 |
| `/api/nodes/start/<node_type>` | POST | `{ "name": string }` | 启动特定节点 |
| `/api/nodes/stop/<node_type>` | POST | `{ "name": string, "keep_config": boolean }`（keep_config是可选的） | 停止特定节点 |

### 使用Curl测试API
```bash
* curl -X POST http://127.0.0.1:8080/api/network/start
* curl -X POST http://127.0.0.1:8080/api/network/stop
* curl -X GET http://127.0.0.1:8080/api/network/topology

* curl -X POST -H "Content-Type: application/json" -d '{"host1":"h1", "host2":"h8","get_full":true}' http://localhost:8080/api/nodes/ping
* curl -X POST -H "Content-Type: application/json" -d '{"host":"h1", "ip":"10.0.0.8"}' http://localhost:8080/api/nodes/ping/ip
* curl -X POST -H "Content-Type: application/json" -d '{"get_full":false,"timeout":"10"}' http://localhost:8080/api/network/ping

* curl -X POST -H "Content-Type: application/json" -d '{"name":"祖国01"}' http://localhost:8080/api/nodes/add/switch
* curl -X POST -H "Content-Type: application/json" -d '{"name":"中国", "ip":"10.0.0.9"}' http://localhost:8080/api/nodes/add/host
* curl -X POST -H "Content-Type: application/json" -d '{"name":"h9", "ip":"10.0.0.9","link_to":"s2"}' http://localhost:8080/api/nodes/add/host
* curl -X DELETE http://localhost:8080/api/nodes/del/h9

* curl -X POST -H "Content-Type: application/json" -d '{"name":"h9"}' http://localhost:8080/api/nodes/start/host
* curl -X POST -H "Content-Type: application/json" -d '{"name":"s1","keep_config":true}' http://localhost:8080/api/nodes/stop/switch

* curl -X POST -H "Content-Type: application/json" -d '{"fromNode":"h9", "toNode":"s4","params":{"delay":5,"bw": 10}}' http://localhost:8080/api/links/add
* curl -X DELETE -H "Content-Type: application/json" -d '{"fromNode":"h2", "toNode":"s4","intf":"h5-eth1"}' http://localhost:8080/api/links/del
```

### 补充说明
* 如果遇到“400 Bad Request”问题，请确保你的请求方法（POST或PUT）和参数（true/false，而不是True/False或"True"/"False"）是正确的。

* 访问`/api/config`时所需的数据格式：
```json
{
  "links": [
    {
      "from": "s1",
      "to": "s2",
      "params": {
        "bandwidth": 10,
        "delay": 5
      }
    }
  ],
  "hosts": [
    {
      "name": "h1",
      "params": {
        "IP": "192.168.1.2",
        "Mask": "255.255.255.0",
        "MAC": "00:00:00:AA:BB:CC",
        "intfName": "h1-eth0",
        "status": "up"
      }
    }
  ],
  "switches": [
    {
      "name": "s1",
      "params": {
        "IP": "192.168.1.2",
        "Mask": "255.255.255.0",
        "MAC": "00:00:00:AA:BB:CC",
        "intfName": "s1-eth0",
        "status": "up"
      }
    }
  ]
}
```

---

## 日志说明
日志文件存储在`logs/`目录中，具体如下：
- `app.log`: 当前应用程序日志。
- `app.log.2023-07-19`: 历史日志（按日期命名）。
- `error.log`: 当前错误日志。
- `error.log.1`: 历史错误日志备份。
