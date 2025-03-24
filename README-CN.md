# MininetController

## 项目结构
```markdown
MininetContoller/
├── README.md
├── README-CN.md            # 中文 README 文件
├── run_mininet_env(CN).txt # 用于 mininet 控制的中文命令列表
├── data_handler/           # 实现对 JSON 数据文件的简单读写操作
│   ├── config.json         # JSON 数据文件
│   └── json_handler.py     # 实现对 JSON 数据的简单读写以及发送到指定 IP
├── src/
│   ├── app.py              # 一个简单的 Flask 应用，将 controller.py 中的方法封装成 HTTP 请求供前端访问
│   ├── controller.py       # 主控制类，实现了一系列 Mininet 控制和访问逻辑，封装了 Mininet net 类的常用方法
│   └── main_topology.py    # 拓扑类，创建由主机、交换机、控制器和链路组成的拓扑，并返回相应的 Mininet net 对象
└── logs/                   # 日志文件目录
    ├── app.log
    └── error.log
```

---

## 项目介绍

### 主要内容
该项目主要开发了网络模拟工具 Mininet 的控制器以及对应的 Flask 服务程序，并记录了 Flask 服务器的运行过程。

### MininetController 是如何工作的？
MininetController 使用 Mininet 进行网络模拟，并使用 Ryu-controller 进行交换机仿真。

### 依赖项
* 运行 `sudo pip install --no-cache-dir -r requirements.txt`
* 或者手动安装依赖项
* Python 3.8.10
* Flask 3.0.3
  * `sudo pip install flask`
  * `sudo pip install flask-cors`
* Mininet 2.3.0.dev6
  * `sudo apt-get install mininet`
  * `sudo pip install mininet`                            # Python API

### 快速上手
* 克隆仓库
  * git clone https://github.com/MemorialAndUnique/MininetController.git
* 进入克隆的仓库
  * `cd MininetController/src`
* 运行 `sudo ryu-manager --verbose ryu.app.simple_switch`   # 启动远程 ryu-controller
* 运行 `sudo python3 app.py`                                # 运行 flask 应用，运行在 (127.0.0.1:8080)
  * 或者运行 `sudo python3 app.py --cli True`                # 在运行 flask 应用的同时打开 mininet cli（可能会导致错误）
* 使用 Ctrl+C 停止服务器
* 模拟结束后，运行 `sudo mn -c`                       # 清理创建的 mininet 拓扑

---

## 基本操作
* 启动/停止整个网络
* 启动/停止节点（主机/交换机/控制器）
* 获取运行中网络的拓扑（返回格式化的 JSON 数据）
* 添加主机/交换机
* 添加链路
* 删除主机/交换机
* 删除链路
* 更改节点/交换机/链路的配置参数
* 使用 ping 工具
  * 主机之间的 'Ping/PingFull'（可选返回完整数据）
  * 主机到 IP 的 'Ping IP (str)'
  * 'PingAll/PingAllFull'（可选返回完整数据）
* 为交换机 S 设置新的控制器（Controller 或 RemoteController 的实例）

---

## 主要 API 列表

| 终端 | 方法 | 参数 | 描述 |
| ---- | ---- | ---- | ---- |
| `/api/network/start` | POST | 无 | 启动整个网络 |
| `/api/network/stop` | POST | 无 | 停止整个网络，除非你已完成模拟，否则不要运行此方法 |
| `/api/network/topology` | GET | 无 | 获取网络拓扑 |
| `/api/network/init` | POST | '{"cli": true,"data":{格式为 config.json}}' | 根据 config.json 重新创建 mininet 网络.<br>cli: 当 cli=true 时打开 mininet-CLI|
| `/api/nodes/ping` | POST | `{ "host1": "h1", "host2": "h2", "get_full": false (可选，默认为 false), "timeout": "10"(可选，默认为 None) }` | 测试主机之间的连通性 |
| `/api/nodes/ping/ip` | POST | `{ "host": "h1", "ip": "10.0.0.8" }` | 测试主机到 IP 的连通性 |
| `/api/network/ping` | POST | `{ "timeout": "10"(可选，字符串), "get_full": false (可选，默认为 false),  }` | 测试整个网络的连通性 |
| `/api/nodes/add/<node_type>` | POST | 对于主机: `{ "name": string, "ip": string,"link_to":string(可选，表示主机初始化时连接到哪个交换机，默认连接到 's1')}` 对于交换机: `{ "name": string }` | 添加节点. <br>注意: 交换机的名称必须是 "s1" 或 "中国01" 的形式，数字 "1" 在 "s1" 中将是交换机的 id。<br>建议: 在添加交换机后运行 "/api/nodes/start/switch"
| `/api/nodes/del/<node_name>` | DELETE | 无 | 删除节点 |
| `/api/links/add` | POST | `{ "fromNode": string, "toNode": string, "params": object }` | 创建链路 |
| `/api/links/del` | POST | `{ "fromNode": string, "toNode": string,"intf":string(通过链路连接的接口之一) }` | 删除链路 |
| `/api/config` | PUT | 配置对象 | 应用网络配置 |
| `/api/nodes/start/<node_type>` | POST | `{ "name": string }` | 启动特定节点 |
| `/api/nodes/stop/<node_type>` | POST | `{ "name": string, "keep_config": boolean }` (keep_config 是可选的) | 停止特定节点 |

### 使用 Curl 测试 API
```bash
* curl -X POST http://127.0.0.1:8080/api/network/start
* curl -X POST http://127.0.0.1:8080/api/network/stop
* curl -X GET http://127.0.0.1:8080/api/network/topology
* curl -X POST http://localhost:8080/api/network/init -H "Content-Type: application/json" -d '{
    "cli": true,
    "data":{
        "links": [
            {"from": "s1", "to": "h1"},
            {"from": "s2", "to": "h2"},
            {"from": "s2", "to": "s1"}
        ],
        "hosts": [
            {"name": "h1", "ip": "192.168.1.2/16"},
            {"name": "h2", "ip": "192.168.1.3"}
        ],
        "switches": [
            {"name": "s1"},
            {"name": "s2"}
        ]
    }}'    
    
* curl -X POST -H "Content-Type: application/json" -d '{"host1":"h1","host2":"h9","get_full":true}' http://localhost:8080/api/nodes/ping
* curl -X POST -H "Content-Type: application/json" -d '{"host":"h1", "ip":"10.0.0.8"}' http://localhost:8080/api/nodes/ping/ip
* curl -X POST -H "Content-Type: application/json" -d '{"get_full":false,"timeout":"10"}' http://localhost:8080/api/network/ping

* curl -X POST -H "Content-Type: application/json" -d '{"name":"祖国01"}' http://localhost:8080/api/nodes/add/switch
* curl -X POST -H "Content-Type: application/json" -d '{"name":"中国", "ip":"10.0.0.9"}' http://localhost:8080/api/nodes/add/host
* curl -X POST -H "Content-Type: application/json" -d '{"name":"h9", "ip":"10.0.0.9","link_to":"祖国01"}' http://localhost:8080/api/nodes/add/host
* curl -X DELETE http://localhost:8080/api/nodes/del/h9

* curl -X POST -H "Content-Type: application/json" -d '{"name":"祖国01"}' http://localhost:8080/api/nodes/start/switch
* curl -X POST -H "Content-Type: application/json" -d '{"name":"h9"}' http://localhost:8080/api/nodes/start/host
* curl -X POST -H "Content-Type: application/json" -d '{"name":"祖国01","keep_config":true}' http://localhost:8080/api/nodes/stop/switch

* curl -X POST -H "Content-Type: application/json" -d '{"fromNode":"祖国01", "toNode":"s2","params":{"delay":5,"bw": 10}}' http://localhost:8080/api/links/add
* curl -X POST -H "Content-Type: application/json" -d '{"fromNode":"h2", "toNode":"s4","intf":"h5-eth1"}' http://localhost:8080/api/links/del

* curl -X PUT -H "Content-Type: application/json" -d '{"hosts": [
    {
      "name": "h1",
      "params": {
        "ip": "192.168.1.4/24"
      }
    }
  ]}' http://localhost:8080/api/config

```

### 补充说明
* 如果遇到“400 Bad Request”问题，请确保你的请求方法（POST 或 PUT）和参数（true/false，而不是 True/False 或 "True"/"False"）是正确的。

* 访问 `/api/config` 时所需的数据格式：
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
        "ip": "192.168.1.2",
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
        "ip": "",
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
日志文件存储在 `logs/` 目录中，具体如下：
- `app.log`: 当前应用程序日志。
- `app.log.2023-07-19`: 历史日志（按日期命名）。
- `error.log`: 当前错误日志。
- `error.log.1`: 历史错误日志备份。
