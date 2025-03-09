# MininetController
## 项目结构
``` markdown
MininetContoller/
├── README.md
├── README-CN.md            # README file in Chinese
├── run_mininet_env(CN).txt # linux系统下控制mininet运行的一系列命令合集
├── data_hanlder/           # 实现了json数据文件的简单读写
│   ├── config.json         # json数据文件
│   └── json_handler.py     # 实现了简单的json数据读写和发送至指定ip的功能
├── src/
│   ├── app.py              # 一个简单的flask应用，封装controller.py中的方法为Ｈttp请求，供前端访问
│   ├── controller.py       # 主控制类，实现了对mininet的一系列控制和访问逻辑，基本封装了mininet.net类中常见的方法
│   └── main_topology.py    # 拓扑类，创建一个包含由Host、Switch、Controller和Links组成的拓扑及对应的mininet.net对象，返回mininet.net对象
└── logs/                   # 日志文件所在目录
    ├── app.log
    └── error.log
```
-------------------------------------------------------------------------------------------------
## 项目简介
### 主要内容
本项目主要开发实现了对网络模拟工具mininet的控制器和相应的Flask服务程序，并对Flask服务器的运行过程进行了日志记录
### MininetController的工作机理
MininetController使用 mininet 进行网络模拟，使用 Ryu-controller 进行交换机模拟
### 安装依赖
* Python 3.8.10
* Flask 3.0.3
  * `sudo pip install flask`
* Mininet 2.3.0.dev6
  * `sudo apt-get install mininet`
  * `sudo pip install mininet`                            # Python API
### 快速部署
* Clone repo
  * git clone https://github.com/Sirozha1337/NetworkSimulator.git
* cd to cloned repo
  * `cd MininetController/src`
* Run `sudo ryu-manager --verbose ryu.app.simple_switch`   # 先启动一个ryu控制器
* Run `sudo python3 app.py`                                # 启动Flask应用, 运行在127.0.0.1:8080
  * or Run `sudo python3 app.py --cli True`                # 启动Flask应用的同时，打开一个mininet命令行窗口
* Use Ctrl+C to stop the server
* Run `sudo mn -c`                                         # 清除所有以创建的mininet网络，发生冲突时也可以使用该命令先清除已有网络再运行
-------------------------------------------------------------------------------------------------
## 支持的操作
* Start/Stop network
* Start/Stop a node(Host/Switch/Controller)
* Get topology of the running network(return a fommatted json data)
* Adding hosts/switches
* Adding links
* Removing hosts/switches
* Removing links
* Changing node/switch/links configuration params
* Use ping tool
  * 'Ping/PingFull' betweent hosts(return full data,optional)
  * 'Ping ip(str) on a host'
  * 'PingAll/PingAllFull'(return full data,optional)
* Set a new controller(instance of Controller or RemoteController) for switch S
-------------------------------------------------------------------------------------------------
## 主要接口列表

| 端点 | 方法 | 参数 | 说明 |
| ---- | ---- | ---- | ---- |
| `/api/network/start` | POST | 无 | 启动整个网络 |
| `/api/network/stop` | POST | 无 | 停止整个网络 |
| `/api/network/topology` | GET | 无 | 获取网络拓扑 |
| `/api/network/ping/hosts` | POST | `{ "host1": string, "host2": string, "get_full": False(可选，默认Ｆasle), "timeout": string(可选,'10'ms) }` | 测试主机间的连通性 |
| `/api/network/ping/ip`    | POST | `{ "host": str, "ip": str }` | 主机到IP的连通性测试 |
| `/api/network/ping/all`   | POST | `{ "timeout": int, "get_full": False(可选，默认Ｆasle), "timeout": string(可选,'10'ms) }` | 全网连通性测试 |
| `/api/nodes/<node_type>` | POST | Host: `{ "name": string, "ip": string }`<br>Switch: `{ "name": string }` | 添加节点 |
| `/api/nodes/del/<node_name>` | DELETE | 无 | 删除节点 |
| `/api/links` | POST | `{ "fromNode": string, "toNode": string, "params": object }` | 创建链路 |
| `/api/links` | DELETE | `{ "fromNode": string, "toNode": string }` | 删除链路 |
| `/api/config` | PUT | 配置对象 | 应用网络配置 |
| `/api/nodes/<name>/start` | POST | `{ "controller": string }` (可选) | 启动指定节点 |
| `/api/nodes/<name>/stop` | POST | `{ "keep_config": boolean }` (可选) | 停止指定节点 |

### 补充说明
访问/api/config时需要传入的数据格式 :
```json
{
  "links": [
    {
      "from": "s1",
      "to": "s2",
      "params": {
        "bandwidth": 10,
        "delay": "5ms"
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
  "switchs": [
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
-------------------------------------------------------------------------------------------------
## 日志说明
日志文件存储在 `logs/` 目录下，具体说明如下：
- `app.log`：当前应用程序日志。
- `app.log.2023-07-19`：历史日志（按日期命名）。
- `error.log`：当前错误日志。
- `error.log.1`：历史错误日志备份。
-------------------------------------------------------------------------------------------------
