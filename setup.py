from setuptools import setup, find_packages

setup(
    name='ec2_manager',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'boto3',
        'customtkinter',
    ],
    entry_points={
        'console_scripts': [
            'ec2_manager=ec2_manager.main:main',
        ],
    },
    author='Abdur-Rahman Bilal',
    author_email='aramb@aramservices.com',
    description='A GUI application to manage AWS EC2 instances',
    url='https://github.com/aramb-dev/ec2_manager',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)