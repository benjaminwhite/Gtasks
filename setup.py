import gtasks

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = 'gtasks',
    version = gtasks.__version__,
    description = 'A better Google Tasks Python module',
    author = 'Benjamin White',
    author_email = 'ben.white@berkeley.edu',
    url = 'https://github.com/benjaminwhite/Gtasks',
    license = 'MIT',
    packages = ['gtasks'],
    install_requires = ['keyring', 'requests_oauthlib'],
    package_data = {'':['*.json']},
    keywords = ['google', 'tasks', 'task', 'gtasks', 'gtask']
)
