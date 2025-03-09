import unittest
from mininet.node import Controller, RemoteController, OVSKernelSwitch, Host
from controller import MininetController


class TestMininetController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
    	from main_topology import myNetwork
    	cls.net = myNetwork(cli=False)
    	cls.controller = MininetController(cls.net)
    	cls.controller.start_network()

    @classmethod
    def tearDownClass(cls):
    	from mininet.cli import CLI
    	CLI(cls.net)
    	cls.controller.stop_network()

    def test_1_network_operations(self):
        # 测试网络拓扑获取
        topology = self.controller.get_topology()
        self.assertIsInstance(topology, dict)
        self.assertIn('switches', topology)
        self.assertIn('hosts', topology)
        self.assertIn('links', topology)

    def test_2_node_operations(self):
        # 测试节点启停
        # 测试交换机操作
        success, msg = self.controller.stop_node('s1')
        self.assertTrue(success)
        self.assertIn('stopped', msg)
        
        success, msg = self.controller.start_node('s1')
        self.assertTrue(success)
        self.assertIn('started', msg)
        
        # 测试主机操作
        success, msg = self.controller.stop_node('h1', keep_config=True)
        self.assertTrue(success)
        self.assertIn('stopped', msg)
        
        success, msg = self.controller.start_node('h1')
        self.assertTrue(success)
        self.assertIn('interfaces up', msg)       

    def test_3_add_remove_elements(self):
        # 测试添加删除元素
        # 添加新主机
        new_host = self.controller.add_host('h9', cls=Host, ip='10.0.0.9', defaultRoute=None)
        self.assertIsNotNone(new_host)

        # 添加新交换机
        new_switch = self.controller.add_switch('s5',cls=OVSKernelSwitch)
        self.assertIsNotNone(new_switch)

        # 添加新链路
        link = self.controller.add_link('s5', 'h9')
        self.assertIsNotNone(link)

        # 验证拓扑更新
        topology = self.controller.get_topology()
        self.assertIn('h9', [h['name'] for h in topology['hosts']])
        self.assertIn('s5', [s['name'] for s in topology['switches']])

        # 删除链路
        success, msg = self.controller.del_link('s5', 'h9')
        self.assertTrue(success)

        # 删除节点
        self.controller.del_node('h9')
        self.controller.del_node('s5')

    def test_4_parameter_configuration(self):
        # 测试参数配置
        config = {
            "links": [{
                "from": "s1",
                "to": "s2",
                "params": {
                    "bandwidth": 10,
                    "delay": "5ms"
                }
            }],
            "hosts": [{
                "name": "h1",
                "params": {
                    "IP": "192.168.1.100",
                    "Mask": "24",
                    "MAC": "00:00:00:AA:BB:CC"
                }
            }]
        }

        results = self.controller.apply_params(config)
        for result in results:
            self.assertTrue(result[1])

        # 验证链路参数
        links = self.controller.get_link('s1', 's2')
        self.assertGreater(len(links), 0)
        self.assertEqual(links[0].intf1.params.get('bw'), 10)

        # 验证主机参数
        h1 = self.controller.get_node_by_name('h1')
        intf = h1.intfList()[0]
        self.assertEqual(intf.IP(), '192.168.1.100')
        self.assertEqual(intf.MAC().lower(), '00:00:00:aa:bb:cc')

    def test_5_controller_management(self):
        # 测试控制器管理
        # 创建远程控制器
        ryu_ctrl = RemoteController('ryu', ip='127.0.0.1', port=6633)

        # 设置控制器
        success, msg = self.controller.set_controller('s1', ryu_ctrl)
        self.assertTrue(success)
        self.assertIn('ryu', msg)

        # 验证控制器状态
        s1 = self.controller.get_node_by_name('s1')
        self.assertEqual(s1.controller.name, 'ryu')

    def test_6_connectivity_test(self):
        # 测试连通性
        # 启动所有节点
        self.controller.start_node('s1')
        self.controller.start_node('h1')
        self.controller.start_node('h2')

        # 测试ping
        result = self.controller.ping('h1', 'h2')
        # self.assertIn('0% packet loss', result)

        # 测试全量ping
        result = self.controller.ping_all()
        self.assertLess(result, 100)  # 允许部分丢包

    def test_7_error_handling(self):
        # 测试异常处理
        # 不存在的节点
        self.assertIsNone(self.controller.get_node_by_name('nonexist'))

        # 无效的链路配置
        invalid_config = {
            "links": [{
                "from": "s1",
                "to": "invalid_node",
                "params": {"bandwidth": 10}
            }]
        }
        results = self.controller.apply_params(invalid_config)
        for i in range(len(results)):
            self.assertFalse(results[i][0])

        # 无效的控制器类型
        invalid_ctrl = Host('h0')
        success, msg = self.controller.set_controller('s1', invalid_ctrl)
        self.assertFalse(success)
     


if __name__ == '__main__':
    unittest.main(
        verbosity=2,
        testRunner=unittest.TextTestRunner(),
        failfast=True
    )
    
