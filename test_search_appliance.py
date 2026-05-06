import unittest
from app import search_appliance_in_db  # or wherever your function lives

class TestSearchAppliance(unittest.TestCase):
    def setUp(self):
        # Each test gets a fresh appliance list.
        self.appliances = [
            {'store_name': 'Main', 'item_number': '1001', 'brand': 'A', 'archived': False},
            {'store_name': 'Main', 'item_number': '2002', 'brand': 'B', 'archived': True},
            {'store_name': 'Branch', 'item_number': '3003', 'brand': 'C', 'archived': False}
        ]

    def test_search_by_store_and_item(self):
        # Should find the non-archived item from Main with item_number 1001
        result = search_appliance_in_db(self.appliances, store_name='Main', item_number='1001')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['brand'], 'A')

    def test_search_by_store_only(self):
        # Should find both Main appliances, but only the non-archived one
        result = search_appliance_in_db(self.appliances, store_name='Main')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['item_number'], '1001')

    def test_search_by_item_number_only(self):
        # Should find only one item in Branch with item_number 3003
        result = search_appliance_in_db(self.appliances, item_number='3003')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['brand'], 'C')

    def test_search_returns_all_non_archived(self):
        # If no parameters, return all non-archived
        result = search_appliance_in_db(self.appliances)
        self.assertEqual(len(result), 2)  # Should be Main 1001 and Branch 3003

    def test_search_no_result(self):
        result = search_appliance_in_db(self.appliances, store_name='Unknown')
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()