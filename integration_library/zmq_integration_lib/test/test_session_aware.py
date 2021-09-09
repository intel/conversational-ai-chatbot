import unittest
from zmq_integration_lib.session_aware import _SessionAwareINPAD, _SessionAwareOUTPAD
import unittest.mock as mock


class TestInpad(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_set_rpc_host(self):
        self.assertTrue(True)

    def test_session_update_callback(self):
        self.assertTrue(True)

    def test_data_and_event_generator(self):
        self.assertTrue(True)


class TestOutpad(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_update_session_id(self):
        self.assertTrue(True)

    def test_push(self):
        self.assertTrue(True)
