from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aiocqhttp',
    version='1.4.2',
    url='https://github.com/nonebot/aiocqhttp',
    license='MIT License',
    author='Richard Chien',
    author_email='richardchienthebest@gmail.com',
    maintainer='NoneBot Team',
    description='A Python SDK with async I/O for OneBot (CQHTTP).',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=('aiocqhttp', 'aiocqhttp.*')),
    package_data={
        '': ['*.pyi'],
    },
    install_requires=['Quart>=0.14,<0.15', 'httpx>=0.11,<1.0'],
    extras_require={
        'all': ['ujson'],
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
