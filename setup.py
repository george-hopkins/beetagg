import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='beetagg',
    version='0.1.0',
    author='George Hopkins',
    author_email='george-hopkins@null.net',
    description='A library to decode Beetaggs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/george-hopkins/beetagg',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'beetagg = beetagg.__main__:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
