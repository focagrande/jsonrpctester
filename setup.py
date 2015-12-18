from setuptools import setup

setup(
    name='jsonrpctester',
    version='0.1',
    py_modules=['jsonrpc'],
    install_requires=[
        'requests',
        'click',
        'pygments'
    ],
    entry_points='''
        [console_scripts]
        jsonrpc=jsonrpc:cli
    ''',
)