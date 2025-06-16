import csv
import os
import openai
import pickle
from django.core.management.base import BaseCommand
from bot.models import Intention, Tone
from django.conf import settings
from openai.embeddings_utils import get_embedding


class Command(BaseCommand):
    help = 'Load multiple CSV files into the database'

    def handle(self, *args, **kwargs):
        # Define the models and their CSV file names
        models = {
            'Intention': 'intentions_tree.csv',
            'Tone': 'tone_tree.csv'
        }

        for model_name, file_name in models.items():
            model = globals()[model_name]  # Get the model class dynamically by its name
            if self.data_exists(model):
                self.stdout.write(self.style.SUCCESS(f'Data for {model_name} already exists.'))
            else:
                self.load_csv(file_name, model, ['machine_name', 'context'])

    def data_exists(self, model):
        """ Check if data already exists in the model's table """
        # Checks if any record exists in the given model's table
        return model.objects.exists()

    def load_csv(self, file_name, model, fields):
        """ Load a CSV file into the database for the given model """
        BASE_DIR = settings.BASE_DIR
        self.path_csv = os.path.join(BASE_DIR, 'bot', 'assets', file_name)
        
        if not os.path.exists(self.path_csv):
            self.stdout.write(self.style.ERROR(f'File {file_name} does not exist.'))
            return
            
        openai.api_key = settings.OPEN_IA['API_KEY']
        with open(self.path_csv, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                # Assuming the second column of the CSV is the context, and we need an embedding for it
                embedding = get_embedding(row[1], engine='text-embedding-ada-002')

                # Convert embedding to bytes using pickle
                embedding_bytes = pickle.dumps(embedding)

                # Create a model instance dynamically
                model_instance = model(
                    machine_name=row[0],  # Assuming the first column is machine_name
                    context=row[1],       # Assuming the second column is context
                    embedding=embedding_bytes  # Save the embedding in binary format
                )

                # Save the instance to the database
                model_instance.save()

                self.stdout.write(self.style.SUCCESS(f'Inserted {model.__name__} record: {row[0]}'))
