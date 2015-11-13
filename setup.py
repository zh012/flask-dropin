#!/usr/bin/env python
from setuptools import setup


options = dict(
    name='Flask-DropIn',
    version='0.0.1',
    description='Flask-DropIn let you easily organize larger project.',
    author='Jerry Zhang',
    author_email='hui.calife@gmail.com',
    url='https://github.com/zh012/flask-dropin.git',
    packages=['flask_dropin'],
    license='MIT',
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask>=0.10',
        'click>=2.0'
    ],
    tests_require=[
        'pytest>=2.7.1'
    ],
    entry_points={
        'console_scripts': [
            'dropin = flask_dropin.cli:main'
        ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
)

setup(**options)
