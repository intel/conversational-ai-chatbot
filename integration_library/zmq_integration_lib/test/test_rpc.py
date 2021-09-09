import unittest
from zmq_integration_lib import RPCClient, RPCServer
import unittest.mock as mock


class TestRPCClient(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # @mock.patch('zmq_integration_lib.zmq_integration_lib.zmq')
    @mock.patch("zmq_integration_lib.streaming.zmq")
    def test_verify(self, mock_zmq):
        self.assertTrue(True)

    def test_get_token(self):
        self.assertTrue(True)

    def test_logout(self):
        self.assertTrue(True)


class TestRPCServer(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_set_handler(self):
        self.assertTrue(True)

    def test_run(self):
        self.assertTrue(True)


class TestClientConn(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sync_call(self):
        self.assertTrue(True)
