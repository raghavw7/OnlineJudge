import csv
from django.core.management.base import BaseCommand
from compiler.models import Problem

import re
import markdown

def clean_text(text):

    text = re.sub(r'\\le', '≤', text)    # Replace \le with ≤
    text = re.sub(r'\\cdot', '⋅', text)  # Replace \cdot with ⋅s
    text = re.sub(r'\(\s*(\d+)\s*\\le\s*(\w+)\s*\\le\s*(\d+)\s*\)', r'(\1 ≤ \2 ≤ \3)', text)
    text = text.replace('$', '')
    text = text.replace('â€”', '_')
    text = text.replace('“', '"').replace('”', '"')
    text = re.sub(r'(\d+)', r'**\1**', text)

    text = re.sub(r'_', '—', text)
    # text = re.sub(r'(\d+)', r'**\1**', text)
    return text

def extract_input_output(text):

    input_pattern = re.compile(r'-----Input-----\s*(.*?)(?:\nOutput:|$)', re.DOTALL)
    output_pattern = re.compile(r'-----Output-----\s*(.*)', re.DOTALL)

    input_match = input_pattern.search(text)
    output_match = output_pattern.search(text)

    input_text = input_match.group(1).strip() if input_match else ''
    output_text = output_match.group(1).strip() if output_match else ''

    updated_description = re.sub(r'-----Input-----\s*(.*?)(?:\nOutput:|$)', '', text, flags=re.DOTALL)
    updated_description = re.sub(r'-----Output-----\s*(.*)', '', updated_description, flags=re.DOTALL)

    return updated_description, input_text, output_text


class Command(BaseCommand):
    help = 'Seed the database with problems from a csv file.'

    def handle(self, *args, **kwargs):

        csv_file_path = 'D:\Webdev\Projects\Django\Data\problems.csv'

        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames
            print("CSV headers: ", headers)

            i = 0
            for row in reader:
                i = i+1


                description = clean_text(row['question'])
                description = markdown.markdown(description)
                updated_description, inputs, outputs = extract_input_output(description)

                problem, created = Problem.objects.get_or_create(
                    id = row['problem_id'],
                    defaults = {
                        'title': row['problem_name'],
                        'description': updated_description,
                        'difficulty': row['difficulty'],
                        'inputs': inputs,
                        'outputs': outputs
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Problem "{row["problem_id"]}" created'))

                else:
                    self.stdout.write(self.style.WARNING(f'Problem "{row["problem_id"]}" already exists'))

                if i == 31:
                    break