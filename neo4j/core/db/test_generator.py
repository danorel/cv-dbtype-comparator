from unittest import TestCase

from generator import Neo4jGenerator


class TestNeo4jGenerator(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = Neo4jGenerator()

    def test_random_plain_schema(self):
        data = self.generator.random({
            'name': 'Root',
            'properties': [
                {
                    'name': 'User',
                    'min_items': 1000,
                    'max_items': 1000,
                    'properties': [
                        {
                            'name': 'login',
                            'instance': 'str',
                            'range_from': 8,
                            'range_to': 8
                        },
                        {
                            'name': 'password',
                            'instance': 'str',
                            'range_from': 8,
                            'range_to': 16
                        }
                    ]
                }
            ]
        })
        self.failUnlessEqual(len(data.get('User')), 1000)

    def test_random_deep_schema(self):
        data = self.generator.random({
            'name': 'Root',
            'properties': [
                {
                    'name': 'User',
                    'min_items': 1000,
                    'max_items': 1000,
                    'properties': [
                        {
                            'name': 'login',
                            'instance': 'str',
                            'range_from': 8,
                            'range_to': 8
                        },
                        {
                            'name': 'password',
                            'instance': 'str',
                            'range_from': 8,
                            'range_to': 16
                        },
                        {
                            'name': 'CV',
                            'min_items': 0,
                            'max_items': 3,
                            'properties': [
                                {
                                    'name': 'title',
                                    'instance': 'str',
                                    'range_from': 5,
                                    'range_to': 15
                                }
                            ]
                        }
                    ]
                }
            ]
        })
        self.failUnlessEqual(len(data.get('User')), 1000)
