from setuptools import setup

version_info = {}
with open('risk_salon_tools/_version.py') as version_file:
    exec(version_file.read(), version_info)

setup(
    name="risk_salon_tools",

    version=version_info['__version__'],

    author=version_info['__author__'],
    author_email=version_info['__author_email__'],

    description="Risk Salon Tools",

    install_requires=[
        "pandas",
        "pyyaml",
        "keyring",
        "gspread",
        "oauth2client",
        "six"
    ]
)
