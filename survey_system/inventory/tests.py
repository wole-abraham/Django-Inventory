from django.test import TestCase
from django.contrib.auth.models import User
from inventory.models import Equipment, SurveyorEngineer
from django.urls import reverse

class EquipmentRequestTests(TestCase):

    def setUp(self):
    # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
    
    # Create a SurveyorEngineer if not already existing for the user
        self.surveyor, created = SurveyorEngineer.objects.get_or_create(user=self.user)

    # Create test equipment
        self.equipment = Equipment.objects.create(
        name='Test GNSS',
        equipment_type='GNSS',
        status='In Store'
        )

    def test_equipment_request(self):
        # Log in as the test user
        self.client.login(username='testuser', password='testpassword')

        # Simulate a POST request to request equipment
        response = self.client.post('/inventory/request-equipment/', {
            'equipment_id': self.equipment.id
        })

        # Refresh the equipment object
        self.equipment.refresh_from_db()

        # Assert the equipment's status is updated
        self.assertEqual(self.equipment.status, 'In Field')
        self.assertEqual(self.equipment.requested_by, self.user)

        # Assert that the equipment is added to the surveyor's requested_equipment
        self.assertIn(self.equipment, self.surveyor.requested_equipment.all())

        # Assert redirection to the dashboard
        self.assertRedirects(response, '/dashboard/')


class EquipmentFilterTests(TestCase):
    def setUp(self):
        # Create test equipment
        Equipment.objects.create(name='GNSS A', equipment_type='GNSS', status='In Store')
        Equipment.objects.create(name='GNSS B', equipment_type='GNSS', status='In Field')
        Equipment.objects.create(name='Drone X', equipment_type='Drone', status='In Store')

    def test_filter_equipment_in_store(self):
        # Simulate a GET request to filter equipment by type
        response = self.client.get(reverse('filter_equipment'), {'equipment_type': 'GNSS'})

        # Assert the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Parse the JSON response
        data = response.json()

        # Assert only "In Store" equipment is included
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'GNSS A')
    

  