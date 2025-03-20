from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController, OVSKernelSwitch, Host
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.util import quietRun
import json
import logging


class JsonTopo(Topo):
    def __init__(self, json_data):
        super().__init__()

        nodes = {}
        # 添加主机
        for h in json_data['hosts']:
            name = h['name']
            ip = h['ip']
            if '/' not in ip:
                ip += '/24'
            nodes[name] = self.addHost(name, cls=Host, ip=ip, defaultRoute=None)
        # 添加交换机
        for s in json_data['switches']:
            name = s['name']
            nodes[name] = self.addSwitch(name, cls=OVSKernelSwitch)
        # 添加连接
        for link in json_data['links']:
            self.addLink(nodes[link['from']], nodes[link['to']])


class MininetController:
    def __init__(self, net=None):
        self.net = net
        if self.net is None:
            self._init_network()

    def _init_network(self, topo=None, controller=Controller, switch=OVSKernelSwitch):
        """Initialize network topology while self.net is None"""
        self.net = Mininet(topo=topo,
                           controller=controller,
                           switch=switch,
                           link=TCLink,
                           build=False)
        # 添加初始拓扑
        c0 = self.net.addController(name='c0',
                                    controller=Controller,
                                    protocol='tcp',
                                    port=6633)
        c0.start()

        h1 = self.net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
        h2 = self.net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
        h3 = self.net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
        h4 = self.net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)
        h5 = self.net.addHost('h5', cls=Host, ip='10.0.0.5', defaultRoute=None)
        h6 = self.net.addHost('h6', cls=Host, ip='10.0.0.6', defaultRoute=None)
        h7 = self.net.addHost('h7', cls=Host, ip='10.0.0.7', defaultRoute=None)
        h8 = self.net.addHost('h8', cls=Host, ip='10.0.0.8', defaultRoute=None)

        s1 = self.net.addSwitch('s1', cls=OVSKernelSwitch)
        s2 = self.net.addSwitch('s2', cls=OVSKernelSwitch)
        s3 = self.net.addSwitch('s3', cls=OVSKernelSwitch)
        s4 = self.net.addSwitch('s4', cls=OVSKernelSwitch)

        # 启动switch并手动添加流表规则
        self.net.get('s1').start([c0])
        self.net.get('s2').start([c0])
        self.net.get('s3').start([c0])
        self.net.get('s4').start([c0])
        self.net.get('s1').cmd('sudo ovs-ofctl add-flow s1 actions=NORMAL')
        self.net.get('s2').cmd('sudo ovs-ofctl add-flow s2 actions=NORMAL')
        self.net.get('s3').cmd('sudo ovs-ofctl add-flow s3 actions=NORMAL')
        self.net.get('s4').cmd('sudo ovs-ofctl add-flow s4 actions=NORMAL')

        self.net.addLink(s1, s2)
        self.net.addLink(s2, s3)
        self.net.addLink(s3, s4)
        self.net.addLink(s1, h1)
        self.net.addLink(h2, s1)
        self.net.addLink(h3, s2)
        self.net.addLink(h4, s2)
        self.net.addLink(h5, s3)
        self.net.addLink(h6, s3)
        self.net.addLink(h7, s4)
        self.net.addLink(h8, s4)
        self.net.start()

    # 重新为controller赋新的net值
    def set_net_from_topo(self, data, build=False, ipBase='10.0.0.0/24'):
        try:
            if not data:
                return False, f"error: 无JSON数据", 400
            # 验证数据完整性
            for key in ['hosts', 'switches', 'links']:
                if key not in data:
                    return False, f"缺少必要字段: {key}", 400

            nodes = set()
            # 检查主机
            for host in data['hosts']:
                if 'name' not in host or 'ip' not in host:
                    return False, "error: 主机缺少名称或IP", 400
                nodes.add(host['name'])
            # 检查交换机
            for switch in data['switches']:
                if 'name' not in switch:
                    return False, "error: 交换机缺少名称", 400
                nodes.add(switch['name'])
            # 检查链路
            for link in data['links']:
                if 'from' not in link or 'to' not in link:
                    return False, "error: 链路缺少端点", 400
                if link['from'] not in nodes or link['to'] not in nodes:
                    return False, "error: 链路端点不存在", 400

            # 创建网络拓扑
            topo = JsonTopo(data)
            if self.net is not None:
                self.net.stop()
            self.net = Mininet(topo=topo, build=False, ipBase=ipBase)
            c0 = self.net.addController(name='c0',
                                        controller=OVSController,
                                        protocol='tcp',
                                        port=6633)
            c0.start()
            self.start_network()
            # 将控制器传递给switch，并对OVSController和Controller手动设置流表规则
            for switch in self.net.switches:
                switch.start([c0])
                if isinstance(c0, (Controller, OVSController)):
                    switch.cmd(f'sudo ovs-ofctl add-flow {switch.name} actions=NORMAL')
            
            return True, "status: 网络部署成功", 200
        except Exception as e:
            if self.net:
                self.net.stop()
                self.net = None
            logging.error(f"部署失败: {str(e)}")
            return False, f'error: {e}', 500

    def start_network(self):
        """Start entire network"""
        self.net.build()
        self.net.start()

    def stop_network(self):
        """
        Stop entire network
        which stop all nodes and link and will terminate all interfaces
        Do not run the method unless you finish your simulate
        """
        self.net.stop()

    def get_topology(self):
        """获取网络拓扑信息"""
        topology = {
            'switches': [],
            'hosts': [],
            'links': []
        }

        # 收集switch信息
        for node in self.net.switches:
            params = []
            for intf in node.intfList():
                if intf.name == 'lo': continue
                ip = intf.IP() or ""
                mask = self._prefix_to_netmask(intf.prefixLen) if ip else ""
                if ip and '/' not in ip:
                    # 单独处理未携带掩码的ip
                    ip = f'{ip}/{intf.prefixLen}'
                params.append({
                    'ip': ip,
                    'MAC': intf.MAC() or "",
                    'Mask': mask,
                    'intfName': intf.name
                })

            topology['switches'].append({
                'name': node.name,
                'params': params,
                'status': 'up' if node.isSetup else 'down'
            })

        # 收集host信息
        for node in self.net.hosts:
            interfaces = []
            for intf in node.intfList():
                if intf.name == 'lo': continue
                ip = intf.IP() or ""
                mask = self._prefix_to_netmask(intf.prefixLen) if ip else ""
                if ip and '/' not in ip:
                    # 单独处理未携带掩码的ip
                    ip = f'{ip}/{intf.prefixLen}'
                interfaces.append({
                    'ip': ip,
                    'MAC': intf.MAC() or "",
                    'Mask': mask,
                    'intfName': intf.name
                })

            topology['hosts'].append({
                'name': node.name,
                'params': interfaces,
                'status': 'up' if any(intf.isUp() for intf in node.intfList()) else 'down'
            })

        # 收集link信息
        for link in self.net.links:
            topology['links'].append({
                'from': link.intf1.node.name,
                'to': link.intf2.node.name,
                'params': {
                    'fromIntf': link.intf1.name,
                    'toIntf': link.intf2.name,
                    'bandwidth': link.intf1.params.get('bw', None),
                    'delay': link.intf1.params.get('delay', None),
                    'status': link.intf1.status() and link.intf2.status()

                }
            })

        return topology

    def ping(self, fromNode, toNode, timeout=None):
        """
        Test connectivity between two hosts:fromNode and toNode
        return: ploss packet loss percentage
        """
        hosts = [self.net.get(fromNode), self.net.get(toNode)]
        ploss = self.net.ping(hosts, timeout=timeout)
        result = f"ping {fromNode}->{toNode}, loss: {ploss}"
        return result

    def ping_full(self, fromNode, toNode, timeout=None):
        """Ping between hosts fromNode and toNodeand,then return all data.
            hosts: list of hosts
            timeout: time to wait for a response, as string
            returns: all ping data;"""
        hosts = [self.net.get(fromNode), self.net.get(toNode)]
        result = []
        all_outputs = self.net.pingFull(hosts, timeout=timeout)
        for outputs in all_outputs:
            src, dest, ping_outputs = outputs
            sent, received, rttmin, rttavg, rttmax, rttdev = ping_outputs
            output = f" {src}->{dest}: {sent}/{received}, rttmin rttavg rttmax rttdev:{rttdev} {rttmin} {rttavg} {rttmax}"
            result.append(output)
        return result

    def ping_ip(self, name, ip):
        """test connectivity from host h1 to ip"""
        node = self.net.get(name)
        return node.cmd('ping -c 5 ' + ip)

    def ping_all(self, timeout=None):
        """Ping between all hosts.
           returns: ploss packet loss percentage"""
        result = []
        for node1 in self.net.hosts:
            tmp = ''
            for node2 in self.net.hosts:
                tmp += self.ping(node1.name, node2.name, timeout=timeout) + '\n'
            result.append(tmp)
        return result

    def ping_all_full(self, timeout=None):
        """Ping between all hosts and return all data.
            returns: all ping data;"""
        result = []
        for node1 in self.net.hosts:
            for node2 in self.net.hosts:
                tmp = self.ping_full(node1.name, node2.name, timeout=timeout)
                result.append(tmp)
        return result

    def start_node(self, name, _type=None, controller=None):
        """
        启动指定节点
        :param name: 节点名称 (host/switch)
        :param controller: 可选参数，指定交换机控制器（仅对switch有效）
        """
        try:
            node = self.get_node_by_name(name, _type)
            if node is None:
                return False, f"[Error]Fail to get node by name:{name}"

            if isinstance(node, OVSKernelSwitch):
                # 处理交换机启动
                ctrl = controller if controller is not None else self.net.get('c0')  # 默认使用第一个控制器
                node.start([ctrl])
                
                if isinstance(ctrl, (Controller, OVSController)):
                    for switch in self.net.switches:
                        switch.start([ctrl])
                        switch.cmd(f'sudo ovs-ofctl add-flow {switch.name} actions=NORMAL')
                return True, f"Switch {name} started with controller {ctrl.name}"
            elif isinstance(node, Host):
                # 启动主机网络接口
                node.configDefault()
                for intf in node.intfList():
                    intf.ifconfig('up')
                return True, f"Host {name} interfaces up"
            else:
                return False, f"[Error]Unsupported node type: {type(node)}"
        except:
            return False, f"[KeyError]: {name}"

    def stop_node(self, name, _type, keep_config=True):
        """
        停止指定节点
        :param name: 节点名称
        :param keep_config: 是否保留配置（仅对host有效）（True=仅关闭接口，False=完全移除）
        """
        node = self.get_node_by_name(name, _type)
        if node is None:
            return False, f"[Error]Fail to get node by name:{name}"

        if isinstance(node, OVSKernelSwitch):
            node.stop(deleteIntfs=not keep_config)
            return True, f"Switch {name} stopped"
        elif isinstance(node, Host):
            # 关闭所有接口
            for intf in node.intfList():
                intf.ifconfig('down')
            if not keep_config:
                node.terminate()
            return True, f"Host {name} {'stopped' if keep_config else 'removed'}"
        else:
            return False, f"[Error]Unsupported node type: {type(node)}"

    def get_node_by_name(self, name, _type=None):
        """get node by name,return Node"""
        try:
            if _type == "host":
                nodes = [host for host in self.net.hosts if host.name == name]
                if len(nodes) <= 0:
                    raise KeyError(f'name:{name} 不存在，查找host失败')
                else:
                    node = nodes[0]
            elif _type == "switch":
                nodes = [switch for switch in self.net.switches if switch.name == name]
                if len(nodes) <= 0:
                    raise KeyError(f'name:{name} 不存在，查找switch失败')
                else:
                    node = nodes[0]
            else:
                node = self.net.get(name)
            return node
        except KeyError as e:
            print(f"[Error]Node {name} not found, CallStack:[controller.py/get_node_by_name()")
            return None

    def add_host(self, name, ip, link_to=None):
        # Add to first switch by default
        if link_to is None:
            switch = self.net.switches[0]
        else:
            switch = self.get_node_by_name(link_to)
            if switch is None:
                return False, f"Error occurred, Node:{link_to} not found"

        """Add new host to network"""
        new_host = self.net.addHost(name, cls=Host, ip=ip, defaultRoute=None)

        self.net.addLink(new_host, switch, cls=TCLink, bw=10, delay=5)
        self.start_node(name)
        data = {"name": new_host.name,
                # "ip":new_host.intfList()[0].IP(),
                "status": 'up' if any(intf.isUp() for intf in new_host.intfList()) else 'down'
                }
        return True, data

    def add_switch(self, name, cls=None, **params):
        """params: listenPort,inNamespace"""
        new_switch = self.net.addSwitch(name=name, params=params)
        self.start_node(new_switch.name)
        data = {"name": new_switch.name, "status": 'up' if new_switch.isSetup else 'down'}
        return data

    def del_node(self, name):
        """del node(host/switch/controller) by name"""

        node = self.get_node_by_name(name)
        if node is not None:
            self.net.delNode(node)
            return True, f"successfully delete node{name}"
        else:
            return False, f"[Error]Fail to delete node:{name},callbacks: {info}"

    def add_link(self, fromNode, toNode, fromPort=None, toPort=None, **params):
        """add link between fromNoed and toNode"""
        new_link = self.net.addLink(fromNode, toNode, cls=TCLink, fromPort=fromPort, toPort=toPort, **params)
        return new_link

    def del_link(self, fromNode, toNode, intf=None, index=0, allLinks=False):
        link, node1, node2, index = self.get_link(fromNode, toNode, intf=intf)
        if link is None:
            return False, f'[Error]Link {fromNode}->{toNode} not found'
        else:
            self.net.delLinkBetween(node1, node2, index, allLinks)
            return True, f"successfully remove Link {fromNode}->{toNode},intf matchs:{intf}"

    def get_link(self, fromNode, toNode, intf=None):
        """
        get link fromNode(str)->toNode(str)
        return：link, node1(Node),node2(Node)
        """
        node1 = self.get_node_by_name(fromNode)
        node2 = self.get_node_by_name(toNode)
        if node1 is not None and node2 is not None:
            links = self.net.linksBetween(node1, node2)
            link = links[0]
            index = 0
            if intf is not None:
                #  遍历查找是否有满足intf的link
                for lk in links:
                    if lk.intf1.name == intf or lk.intf2.name == intf:
                        link = lk
                        break
                    index += 1  # 记住查找的link所在index方便删除
            return link, node1, node2, index
        else:
            return None, None, None, 0

    def apply_params(self, config):
        """Apply parameters to network elements
        Example config format:
        config = {
            "links": [
            {
                "from": "s1",
                "to": "s2",
                "params": {
                    "bandwidth": 10,  # 10Mbps
                    "delay": "5ms",
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
                "name": "h1",
                "params": {
                "IP": "192.168.1.2",
                "Mask": "255.255.255.0",
                "MAC": "00:00:00:AA:BB:CC",
                "intfName": "h1-eth0",
                "status": "up"
                }
            }
            ]
	    }"""
        result = []

        if 'hosts' in config:
            for host_conf in config['hosts']:
                result.append(self.update_node_params(host_conf))
        if 'switchs' in config:
            for switch_conf in config['switchs']:
                result.append(self.update_node_params(switch_conf))
        if 'links' in config:
            for link_conf in config['links']:
                result.append(self.update_link_params(link_conf))

        return result

    def update_link_params(self, link_conf):
        """更新链路参数"""
        from_node = link_conf['from']
        to_node = link_conf['to']
        params = link_conf.get('params', {})

        # 遍历所有链路查找匹配项
        link, _, _, _ = self.get_link(from_node, to_node)
        if link is None:
            return False, f"[Error]Link {from_node}->{to_node} not found"
        # 更新带宽参数
        if 'bandwidth' in params:
            bw = params['bandwidth']
            # 设置带宽限制 (单位：Mbps)
            link.intf1.config(bw=bw)
            link.intf2.config(bw=bw)
            # 更新链路参数记录
            link.intf1.params['bw'] = bw
            link.intf2.params['bw'] = bw

        # 更新延迟参数
        if 'delay' in params:
            delay = params['delay']
            # 设置延迟 (格式：'5ms')
            link.intf1.config(delay=delay)
            link.intf2.config(delay=delay)
            link.intf1.params['delay'] = delay
            link.intf2.params['delay'] = delay

        return True, "successfully updata params of Link"

    def update_node_params(self, node_conf):
        """更新host/switch节点的接口参数"""
        node_name = node_conf['name']
        params = node_conf.get('params', {})

        # 获取主机对象
        try:
            node = self.net.get(node_name)
        except:
            return False, f"[Error]node {node_name} not found"

        # 获取指定接口
        intf_name = params.get('intfName', '')
        if not intf_name:
            # 默认使用第一个非lo接口
            intf = [intf for intf in node.intfList() if intf.name != 'lo'][0]
        else:
            try:
                intf = node.intf(intf_name)
            except:
                return False, f"[Error]Interface {intf_name} not found on {node_name}"

        # IP地址配置
        if 'ip' in params:
            mask = params.get('Mask', '255.255.0.0')
            ip = params['ip']
            if '/' in ip:
                _, prefix = ip.split('/')
                mask = self._prefix_to_netmask(prefix)
            prefix_len = self._netmask_to_prefix(mask)
            intf.setIP(ip, prefixLen=prefix_len)

        # MAC地址配置
        if 'MAC' in params:
            mac = params['MAC']
            intf.setMAC(mac)

        # 接口状态管理
        if 'status' in params:
            if params['status'].lower() == 'up':
                intf.ifconfig('up')
            else:
                intf.ifconfig('down')
        return True, "successfully updata params of Nodes"

    def set_controller(self, switch_name, controller, restart=True, keep_links=True):
        """
        修改交换机的控制器
        :param switch_name: 交换机名称 (str)
        :param controller: 控制器对象 (Controller/RemoteController)
        :param restart: 是否立即重启交换机 (默认True)
        :param keep_links: 重启时是否保留链路 (默认True)
        """
        # 获取网关对象
        try:
            sw = self.net.get(switch_name)
            if not isinstance(sw, OVSKernelSwitch):
                raise TypeError("Target node is not a switch")
        except Exception as e:
            return False, f"[Error] Switch lookup failed: {str(e)}"

        # 验证控制器有效性
        if not isinstance(controller, (Controller, RemoteController)):
            return False, f"[Error] Invalid controller type: {type(controller)}"

        # 停止当前交换机
        try:
            sw.stop(deleteIntfs=not keep_links)
        except Exception as e:
            return False, f"[Error] Failed to stop switch: {str(e)}"

        # 更新控制器配置
        try:
            sw.controller = controller
            if restart:
                sw.start([controller])
            return True, f"Switch {switch_name} restarted with controller {controller.name}"
        except Exception as e:
            # 尝试恢复原控制器
            if sw.controller:
                try:
                    sw.start([sw.controller])
                except:
                    print("[Warning] Recovery attempt failed")
            return False, f"[Error] Controller update failed: {str(e)}"

    @staticmethod
    def _netmask_to_prefix(netmask):
        """将子网掩码转换为前缀长度"""
        # 处理CIDR格式 (如 '24')
        if netmask.isdigit():
            return int(netmask)

        # 处理点分十进制格式
        bytes = [int(b) for b in netmask.split('.')]
        binary_str = ''.join([format(b, '08b') for b in bytes])
        return len(binary_str.rstrip('0'))

    @staticmethod
    def _prefix_to_netmask(prefix):
        if isinstance(prefix, str):
            prefix = int(prefix)
        """将前缀长度转换为子网掩码"""
        if prefix < 0 or prefix > 32: return ""
        mask = (0xffffffff << (32 - int(prefix))) & 0xffffffff
        return "%d.%d.%d.%d" % (
            (mask >> 24) & 0xff,
            (mask >> 16) & 0xff,
            (mask >> 8) & 0xff,
            mask & 0xff
        )


if __name__ == '__main__':
    from main_topology import myNetwork

    net = myNetwork(cli=False)
    controller = MininetController(net)
    controller.start_network()
    print(controller.ping_all_full())
    controller.stop_network()
