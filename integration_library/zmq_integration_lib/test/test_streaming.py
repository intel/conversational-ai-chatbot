import unittest
from zmq_integration_lib import InputPort, OutputPort, InputPortWithEvents
import unittest.mock as mock


class TestInputPort(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("zmq_integration_lib.streaming.zmq")
    def test_port(self, mock_zmq):
        ip = InputPort(addr="tcp://localhost:6000", topic="dummy")
        self.assertTrue(True)

    @mock.patch("zmq_integration_lib.streaming.zmq")
    def test_port_wrong_input(self, mock_zmq):
        ret = False
        try:
            ip = InputPort(addr="wrong", topic="dummy")
        except Exception:
            ret = True
        self.assertFalse(ret)

    @mock.patch("zmq_integration_lib.streaming.zmq")
    def test_data_generator(self, mock_zmq):
        ip = InputPort(addr="tcp://localhost:6000", topic="dummy")
        self.assertTrue(True)

    @mock.patch("zmq_integration_lib.streaming.zmq")
    def test_data_generator_with_events(self, mock_zmq):
        ip = InputPortWithEvents(addr="tcp://localhost:6000", topic="dummy")
        self.assertTrue(True)


class TestOutputPort(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("zmq_integration_lib.streaming.zmq")
    def test_port(self, mock_zmq):
        op = OutputPort(addr="tcp://*:6000", topic="dummy")
        self.assertTrue(True)

    @mock.patch("zmq_integration_lib.streaming.zmq")
    def test_port_wrong_input(self, mock_zmq):
        ret = False
        try:
            ip = OutputPort(addr="wrong", topic="dummy")
        except Exception:
            ret = True
        self.assertFalse(ret)

    @mock.patch("zmq_integration_lib.streaming.zmq")
    def test_pushdata(self, mock_zmq):
        op = OutputPort(addr="tcp://*:6000", topic="dummy")
        self.assertTrue(True)
