# !/usr/bin/env python
# python setup.py bdist_wheel
import setuptools
setuptools.setup(
    name='mystock',
    packages=setuptools.find_packages(),
    version='0.0.0',
    description='Provides updates and information on select financial instruments',
    author='Ryan D. Batt',
    license='MIT',
    author_email='battrd@gmail.com',
    url='https://github.com/rBatt/mystock',
    keywords=['finance', 'schedule', 'package', ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
)