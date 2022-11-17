import math
import string
import random

Schema = {
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
                    'min_items': 1,
                    'max_items': 5,
                    'properties': [
                        {
                            'name': 'title',
                            'instance': 'str',
                            'range_from': 5,
                            'range_to': 15
                        },
                        {
                            'name': 'Hobby',
                            'min_items': 1,
                            'max_items': 5,
                            'properties': [
                                {
                                    'name': 'title',
                                    'instance': 'str',
                                    'range_from': 3,
                                    'range_to': 15
                                }
                            ]
                        },
                        {
                            'name': 'Company',
                            'min_items': 1,
                            'max_items': 3,
                            'properties': [
                                {
                                    'name': 'title',
                                    'instance': 'str',
                                    'range_from': 3,
                                    'range_to': 15
                                },
                                {
                                    'name': 'City',
                                    'min_items': 0,
                                    'max_items': 1,
                                    'properties': [
                                        {
                                            'name': 'title',
                                            'instance': 'str',
                                            'range_from': 5,
                                            'range_to': 15,
                                            'cache': True
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}


class Neo4jGenerator:
    def __init__(self, cache_probability: float = .75):
        self.__cache_probability = cache_probability

    def __random_primitive(self,
                           range_from: int = 0,
                           range_to: int = 1,
                           **kwargs):
        instance = kwargs.get('instance')
        if instance == "list":
            string_values = []
            count_from = kwargs.get('count_from', 0)
            count_to = kwargs.get('count_to', 0)
            for _ in range((count_to - count_from) + 1):
                float_value = range_from + (random.random() * (range_to - range_from))
                string_value = ''.join(
                    random.choice(string.ascii_uppercase + string.digits) for _ in range(round(float_value)))
                string_values.append(string_value)
            return string_values
        value = range_from + (random.random() * (range_to - range_from))
        if instance == "str":
            return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(round(value)))
        if instance == "int":
            return round(value)
        return value

    def __random_children(self,
                          min_items: int = 0,
                          max_items: int = 0,
                          **kwargs):
        children = []

        name = kwargs.get('name')
        properties = kwargs.get('properties')
        size = min_items + math.floor(random.random() * (max_items - min_items))

        for _ in range(size):
            child = {}
            cache = {}

            for property in properties:
                child_name = property.get('name')
                child_properties = property.get('properties')

                is_primitive = child_properties is None

                if is_primitive:
                    primitive = self.__random_primitive(**property)
                    if kwargs.get('cache'):
                        cache_property = cache.get(name)
                        is_cache_active = cache_property is not None and len(cache_property) > 0
                        if not is_cache_active:
                            child[child_name] = primitive
                            cache[child_name] = [primitive]
                        else:
                            if random.random() > self.__cache_probability:
                                primitive_cache_index = round(random.random() * (len(cache_property) - 1))
                                primitive_cache = cache_property[primitive_cache_index]
                                child[child_name] = primitive_cache
                            else:
                                child[child_name] = primitive
                                cache_property.append(primitive)
                    else:
                        child[child_name] = primitive
                else:
                    child_min_items = property.get('min_items')
                    child_max_items = property.get('max_items')
                    child_size = child_min_items + math.floor(random.random() * (child_max_items - child_min_items))
                    for _ in range(child_size):
                        child_children = self.__random_children(**property)
                        child[child_name] = child_children
            children.append(child)

        return children

    def random(self, schema: dict) -> dict:
        root_obj = {}
        root_properties = schema.get('properties')
        if root_properties is None:
            raise RuntimeError("Property in Root schema doesn't exist")
        for root_property in root_properties:
            children_name = root_property.get('name')
            children_property = self.__random_children(**root_property)
            root_obj[children_name] = children_property
        return root_obj

    def __repr__(self):
        return f"Neo4j probability: {self.__cache_probability}"

