# Copyright (C) 2008 Devin Venable 
import os
import sys

# Expand the file path
path_component = os.path.abspath(__file__).split(os.sep)

# Add the project to sys.path so it's importable.
project_name = path_component[-3]
project_directory = os.sep.join(path_component[:-2])
sys.path.append(os.path.join(project_directory, '..'))
project_module = __import__(project_name, {}, {}, [''])
sys.path.pop()

# Set DJANGO_SETTINGS_MODULE
os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % project_name
    