import unittest
from app import add_appliance_to_db  # adjust if your function is in another module

class TestAddAppliance(unittest.TestCase):
    def setUp(self):
        # Reset a fresh database for each test
        self.appliances = []

    def test_add_new_appliance(self):
        appliance = {
            'store_name': 'Main',
            'item_number': '1234',
            'brand': 'Whirlpool',
            'model': 'ABC1000',
            'serial': 'SN1234',
            'status': 'In',
            'notes': ''
        }
        result = add_appliance_to_db(appliance, self.appliances)
        self.assertTrue(result)
        self.assertEqual(len(self.appliances), 1)
        self.assertEqual(self.appliances[0]['item_number'], '1234')

    def test_add_duplicate_appliance(self):
        appliance = {
            'store_name': 'Main',
            'item_number': '1234',
            'brand': 'Whirlpool',
            'model': 'ABC1000',
            'serial': 'SN1234',
            'status': 'In',
            'notes': ''
        }
        add_appliance_to_db(appliance, self.appliances)  # Add first time
        result = add_appliance_to_db(appliance, self.appliances)  # Try to add duplicate
        self.assertFalse(result)
        self.assertEqual(len(self.appliances), 1)

if __name__ == '__main__':
    unittest.main()