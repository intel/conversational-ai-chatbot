import unittest
from asr.transcriber import SpeechTranscriber
from asr.configparser import find, parser, parse_config


class TestTranscriber(unittest.TestCase):
    def setUp(self):
        self.ts = SpeechTranscriber()

    def tearDown(self):
        pass

    def test_push_data(self):
        self.assertTrue(True)

    def test_get_result(self):
        self.assertTrue(True)


class TestConfigparser(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_config(self):
        self.assertTrue(True)

    def test_parser(self):
        self.assertTrue(True)

    def test_find(self):
        data = "device: CPU"
        ret = find(data, "device")
        self.assertEqual(ret, "CPU", "device is not CPU")

    def test_find_2(self):
        data = "devvice: CPU"
        ret = find(data, "device")
        self.assertEqual(ret, False, "return value is incorrect")
