from setuptools import setup

setup(
    name='aiocqhttp',
    version='0.0.1',
    packages=['aiocqhttp'],
    url='https://github.com/richardchien/python-aiocqhttp',
    license='MIT License',
    author='Richard Chien',
    author_email='richardchienthebest@gmail.com',
    description='CQHttp Python SDK with Asynchronous I/O',
    install_requires=['aiohttp', 'Quart'],
    python_requires='3.6',
    platforms='any'
)
