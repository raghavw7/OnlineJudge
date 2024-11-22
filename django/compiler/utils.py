import json
import os
from django.templatetags.static import static
from django.conf import settings

def get_react_file(file_type, filename):

    try:
        manifest_path = os.path.join(settings.BASE_DIR, 'frontend', 'build', 'asset-manifest.json')
        with open(manifest_path, 'r') as manifest_file:
            manifest = json.load(manifest_file)

        # file = manifest['files']['main.js']
        return manifest['files']['main.js']
    except (FileNotFoundError, KeyError):
        return static(filename)
