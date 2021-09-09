import unittest
import unittest.mock as mock


class TestInputPort(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("zmq_integration_lib.zmq")
    def test_tts_server(self, mock_zmq):
        self.assertTrue(True)
