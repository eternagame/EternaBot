import os.path

from setuptools import setup

root_path = os.path.abspath(os.path.join(__file__, '..'))

setup(
	name='eternabot',
	version='1.0',
	url='https://github.com/eternagame/eternabot/',
	packages=['eternabot'],
	package_dir={'eternabot': os.path.join(root_path, 'eternabot')},
	#python_requires='>2.6,<3',
	install_requires=[
        'scipy>=1.1.0',
        'simplejson>=3.16.0',
        'matplotlib>=2.2.2',
        'networkx>=2.1',
        'numpy>=1.15.0'
    ],
)