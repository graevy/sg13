from setuptools import setup, find_packages

setup(
    name='eDnD',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'importlib; python_version == "3.10"',
    ],
)