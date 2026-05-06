import unittest
from app import (
    add_appliance_to_db, edit_appliance_in_db, archive_appliance_in_db, search_appliance_in_db
    # ...all your core functions
)

class TestApp(unittest.TestCase):

 def setUp(self):
    self.appliances = [
        {
            'store_name': 'Main', 'item_number': '123', 'brand': 'Whirlpool',
            'model': 'ABC', 'serial': 'SN', 'status': 'In', 'notes': '', 'archived': False
        }
    ]

def test_add_appliance(self):
    # ...as before

 def test_edit_appliance(self):
    # ...as above example

  def test_archive_appliance(self):
    # Test archiving
    result = archive_appliance_in_db(self.appliances, 'Main', '123')
    self.assertTrue(result)
    self.assertTrue(self.appliances[0]['archived'])

def test_search_appliance(self):
    results = search_appliance_in_db(self.appliances, item_number='123')
    self.assertEqual(len(results), 1)

    # ...and so on for other features

if __name__ == '__main__':
    unittest.main()