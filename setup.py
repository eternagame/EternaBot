import os.path

from setuptools import setup, find_packages

setup(
	name='eternabot',
	version='1.0',
	url='https://github.com/eternagame/eternabot/',
	packages=find_packages(),
	include_package_data=True,
	#python_requires='>2.6,<3',
	install_requires=[
        'scipy>=1.1.0',
        'simplejson>=3.16.0',
        'matplotlib>=2.2.2',
        'networkx>=2.1',
        'numpy>=1.15.0',
	'httplib2>=0.11.3'
    ],
)
