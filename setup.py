from setuptools import setup

setup(name='cycontext',
      version='0.1.1',
      description='ConText algorithm using spaCy for clinical NLP',
      author='Alec Chapman',
      author_email='abchapman93@gmail.com',
      packages=['cycontext'],
      install_requires=["spacy==2.2.2"]
      )
