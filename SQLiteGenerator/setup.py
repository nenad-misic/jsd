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
    include_package_data=True,
    package_data={'': ['template/*.jinja']}
)