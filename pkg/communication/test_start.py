# test_start.py
import os
import unittest
from unittest.mock import patch
import start
import requests
import json

class TestStart(unittest.TestCase):
    class MockResponse:
        def __init__(self, lines):
            self.lines = lines

        def iter_lines(self):
            for line in self.lines:
                yield line
            return  # Signalisiert das Ende des Streams

    @patch.dict(os.environ, {'LISTEN_TOPIC_test': 'http://localhost:5000/test'})
    def test_get_listen_topics_from_env(self):
        expected = {'test': 'http://localhost:5000/test'}
        self.assertDictEqual(start.get_listen_topics_from_env(), expected)

    @patch('time.sleep', return_value=None)  # Dies verhindert, dass der Test tatsächlich schläft
    def test_wait_for_function(self, _):
        def mock_request(session, endpoint):
            response = requests.Response()
            response.status_code = 200
            return response

        start.wait_for_function('http://localhost:5000/test', request_function=mock_request)

    @patch('start.wait_for_function')
    def test_subscribe_to_topic_and_forward_messages(self, mock_wait_for_function):
        mock_wait_for_function.return_value = None
        test_topic = "test_topic"
        test_endpoint = "http://localhost:5000/test"
        test_message = json.dumps({"message": "test_message"})
        response_lines = [test_message.encode()]

        def mock_get_request(url, **kwargs):
            self.assertEqual(url, f"https://ntfy.sh/{test_topic}/json")
            return self.MockResponse(response_lines)

        def mock_post_request(url, **kwargs):
            self.assertEqual(url, test_endpoint)
            self.assertDictEqual(kwargs["json"], json.loads(test_message))
            return self.MockResponse([])

        start.subscribe_to_topic_and_forward_messages(
            test_topic, 
            test_endpoint, 
            get_request_function=mock_get_request, 
            post_request_function=mock_post_request
        )

if __name__ == '__main__':
    unittest.main()
