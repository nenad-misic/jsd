from setuptools import setup, find_packages
setup(
    name="express_generator",
    version="0.1",
    packages=find_packages(),
    namespace_packages=['d_generator'],

    entry_points={
        'backend_generator': [
            'express = d_generator.express_generator:ExpressGenerator'
        ],
    },
    zip_safe=True
)