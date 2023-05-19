# test_main.py
import unittest
from flask_testing import TestCase
from main import app
import json

class TestSearchPapers(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_search_papers(self):
        # Test with limit parameter
        response = self.client.post("/search", data=json.dumps({"query": "quantum computing", "limit": 5}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['papers']), 5)

        # Test without limit parameter (should default to 10)
        response = self.client.post("/search", data=json.dumps({"query": "quantum computing"}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['papers']), 10)

if __name__ == '__main__':
    unittest.main()
