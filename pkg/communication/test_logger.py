# test_logger.py
import os
import unittest
from unittest.mock import patch
import logger
import logging

class TestLogger(unittest.TestCase):
    @patch.dict(os.environ, {'DEBUG': 'true'})
    def test_getLogger_debug_true(self):
        log = logger.getLogger()
        self.assertEqual(log.level, logging.DEBUG)

    @patch.dict(os.environ, {'DEBUG': 'false'})
    def test_getLogger_debug_false(self):
        log = logger.getLogger()
        self.assertEqual(log.level, logging.INFO)

    @patch.dict(os.environ, clear=True)
    def test_getLogger_debug_not_set(self):
        log = logger.getLogger()
        self.assertEqual(log.level, logging.INFO)

    @patch('logger.getLogger')
    def test_main(self, mock_getLogger):
        mock_logger = mock_getLogger.return_value
        test_message = "test message"
        logger.main(test_message)
        mock_logger.info.assert_called_once_with(test_message)

if __name__ == '__main__':
    unittest.main()
