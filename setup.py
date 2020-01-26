from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aiocqhttp',
    version='0.7.0',
    packages=find_packages(include=('aiocqhttp', 'aiocqhttp.*')),
    url='https://github.com/richardchien/python-aiocqhttp',
    license='MIT License',
    author='Richard Chien',
    author_email='richardchienthebest@gmail.com',
    description='CQHttp Python SDK with Asynchronous I/O',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['Quart~=0.10', 'aiohttp~=3.6'],
    python_requires='>=3.7',
    platforms='any',
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
