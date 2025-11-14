from setuptools import setup, find_packages

setup(
    name='task-cli',
    version='1.0.0',
    py_modules=['task_cli'],
    entry_points={
        'console_scripts': [
            'task-cli=task_cli:main',
        ],
    },
    python_requires='>=3.7',
    description='Simple CLI task manager with SQLite storage',
    author='kimi-bot',
)