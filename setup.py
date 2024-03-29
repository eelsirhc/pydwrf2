from setuptools import setup
import versioneer

requirements = [
    'palettable',
    'numpy',
    'pandas',
    'xarray',
    'matplotlib',
    'netcdf4',
    'boto3'
    # package requirements go here
]

setup(
    name='pydwrf2',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Python for DART/WRF",
    author="Christopher Lee",
    author_email='lee@foldmountain.com',
    url='https://github.com/eelsirhc/pydwrf2',
    packages=['pydwrf2'],
    entry_points={
        'console_scripts': [
            'pydwrf2=pydwrf2.cli:main',
            'pydwrf2_database=pydwrf2.cli:database_cli',
        ]
    },
    install_requires=requirements,
    keywords='pydwrf2',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ]
)
