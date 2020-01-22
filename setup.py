from setuptools import setup

# read the contents of the README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='cycontext',
      version='0.1.3',
      description='ConText algorithm using spaCy for clinical NLP',
      author='Alec Chapman',
      author_email='abchapman93@gmail.com',
      packages=['cycontext'],
      install_requires=["spacy>=2.2.2"],
      long_description=long_description,
      long_description_content_type='text/markdown'
      )
