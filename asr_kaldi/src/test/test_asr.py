import unittest
import unittest.mock as mock


class TestSpeechLibrary(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("zmq_integration_lib.zmq")
    def test_speech_manager(self, mock_zmq):
        pass
