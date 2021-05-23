from setuptools import setup, find_packages
setup(
    name="sqlite_generator",
    version="0.1",
    packages=find_packages(),
    namespace_packages=['d_generator'],

    entry_points={
        'database_generator': [
            'sqlite = d_generator.sqlite_generator:SQLiteGenerator'
        ],
    },
    zip_safe=True
)