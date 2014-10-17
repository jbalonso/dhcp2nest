from setuptools import setup, find_packages

setup(
    name="dhcp2nest",
    version = '0.1',
    maintainer='Jason B. Alonso',
    maintainer_email='jalonso@hackorp.com',
    license = "MIT",
    url = 'https://github.com/jbalonso/dhcp2nest',
    platforms = ["any"],
    description = "Update nest presence using dhcp activity",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': []
    }
)
