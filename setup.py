from setuptools import setup, find_packages

setup(
    name='rvm',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'SQLAlchemy',
        'PyYAML',
        'tabulate',
        'psycopg2',
        ],
    entry_points={
        'console_scripts':[
            'rvm = rvm.scripts.cli:cli',
            ],
        },
    )


