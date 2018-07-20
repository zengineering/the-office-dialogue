from setuptools import setup

setup(
    name='officequotes',
    version='0.2',
    py_modules=['officequotes'],
    packages=find_packages(),
    install_requires=[
        'sqlalchemy',
        'beautifulsoup4',
        'lxml',
        'attrs',
        'click',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        officequotes=officequotes:cli
    ''',
)
