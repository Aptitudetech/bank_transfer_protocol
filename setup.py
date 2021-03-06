# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    from pip._internal.req import parse_requirements
except ImportError:
    from pip.req import parse_requirements

version = '0.0.1'
requirements = parse_requirements("requirements.txt", session="")

setup(
	name='bank_transfer_protocol',
	version=version,
	description='Transfer money from bank to bank using txt file',
	author='CloudGround',
	author_email='info@cloudground.ca',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=[str(ir.req) for ir in requirements],
	dependency_links=[str(ir._link) for ir in requirements if ir._link]
)
