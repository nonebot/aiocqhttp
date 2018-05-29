from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aiocqhttp',
    version='0.0.1',
    packages=['aiocqhttp'],
    url='https://github.com/richardchien/python-aiocqhttp',
    license='MIT License',
    author='Richard Chien',
    author_email='richardchienthebest@gmail.com',
    description='CQHttp Python SDK with Asynchronous I/O',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['Quart', 'aiohttp'],
    python_requires='>=3.6',
    platforms='any',
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
