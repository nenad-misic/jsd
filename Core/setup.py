from setuptools import setup, find_packages
setup(
    name="d_generator_core",
    version="0.1",
    packages=find_packages(),
    namespace_packages=['d_generator'],
    provides=['d_generator.core'],
    entry_points = {
        'console_scripts':
            ['generate_main=d_generator.core.dgenerate:main']
    },
    include_package_data=True,
    package_data={'': ['metamodel/grammar.tx']}
)