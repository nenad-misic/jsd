from setuptools import setup, find_packages
setup(
    name="react_generator",
    version="0.1",
    packages=find_packages(),
    namespace_packages=['d_generator'],

    entry_points={
        'frontend_generator': [
            'react = d_generator.react_generator:ReactGenerator'
        ],
    },
    zip_safe=True
)