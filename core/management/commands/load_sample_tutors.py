from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Profile
import json
import os

class Command(BaseCommand):
    help = 'Loads sample tutors data from JSON file'

    def handle(self, *args, **kwargs):
        json_file = os.path.join('core', 'fixtures', 'sample_tutors.json')
        
        try:
            with open(json_file, 'r') as f:
                tutors_data = json.load(f)
                
            for tutor_data in tutors_data:
                if not User.objects.filter(username=tutor_data['name']).exists():
                    user = User.objects.create_user(
                        username=tutor_data['name'],
                        password='tutor123'  # Default password for sample tutors
                    )
                    Profile.objects.create(
                        user=user,
                        user_type='tutor',
                        subjects=tutor_data['subject'],
                        availability=tutor_data['availability'],
                        hourly_rate=tutor_data['hourly_rate']
                    )
                    self.stdout.write(self.style.SUCCESS(f'Successfully created tutor: {tutor_data["name"]}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Tutor already exists: {tutor_data["name"]}'))
                    
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Invalid JSON file: {json_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading tutors: {str(e)}')) 