from setuptools import setup, find_packages
setup(
    name="d_generator_core",
    version="0.1",
    packages=find_packages(),
    namespace_packages=['d_generator'],
    provides=['d_generator.core'],
    entry_points = {
        'console_scripts':
            [
                'degenerate=d_generator.core.dgenerate:main'
            ],
        'textx_languages':
            [
                'dgenerate_language = d_generator.core.dgenerate:dgenerate_lang'
            ],
        'textx_generators' : 
            [
                'dgenerator = d_generator.core.dgenerate:webapp_dgenerator',
            ],
    },
    include_package_data=True,
    package_data={'': ['metamodel/grammar.tx']}
)