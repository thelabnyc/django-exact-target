#!/usr/bin/env python
from setuptools import setup, find_packages, Distribution
import codecs
import os.path

# Make sure versiontag exists before going any further
Distribution().fetch_build_eggs('versiontag')

from versiontag import get_version, cache_git_tag  # NOQA


packages = find_packages('src')

install_requires = [
    'Django>=2.2',
    'sentry-sdk>=0.5.5',
    'requests>=2.9.1',
    'simplejson>=3.8.2',
]

extras_require = {
    'development': [
        'flake8>=3.2.1',
        'requests_mock>=0.7.0',
        'mock>=2.0.0',
    ],
}


def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return codecs.open(fpath(fname), encoding='utf-8').read()


cache_git_tag()

setup(
    name='django-exact-target',
    description="Integration between django and the SalesForce ExactTarget REST API",
    version=get_version(pypi=True),
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    author='Craig Weber',
    author_email='crgwbr@gmail.com',
    url='https://gitlab.com/thelabnyc/django-exact-target',
    license='ISC',
    package_dir={'': 'src'},
    packages=packages,
    include_package_data=True,
    install_requires=install_requires,
    extras_require=extras_require
)
