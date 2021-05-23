from setuptools import setup, find_packages
setup(
    name="d_generator_core",
    version="0.1",
    packages=find_packages(),
    namespace_packages=['d_generator'],
    provides=['d_generator.core',
              ],
    entry_points = {
        'console_scripts':
            ['frontend_generator=d_generator.core.generate:generate_frontend',
            'backend_generator=d_generator.core.generate:generate_backend',
            'database_generator=d_generator.core.generate:generate_database']
    },
    zip_safe=True
)