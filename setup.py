from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aiocqhttp',
    version='1.0.1',
    packages=find_packages(include=('aiocqhttp', 'aiocqhttp.*')),
    url='https://github.com/cqmoe/python-aiocqhttp',
    license='MIT License',
    author='Richard Chien',
    author_email='richardchienthebest@gmail.com',
    description='A Python SDK with async I/O for CQHTTP.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['Quart>=0.10,<1.0', 'aiohttp>=3.6'],
    extras_require={
        'all': ['ujson'],
    },
    package_data={
        "": ["*.pyi"],
    },
    python_requires='>=3.7',
    platforms='any',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Robot Framework',
    ],
)
