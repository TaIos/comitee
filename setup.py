from setuptools import setup, find_packages

with open('README.adoc') as f:
    long_description = ''.join(f.readlines())

setup(
    name='committee_saframa6',
    version='0.1',
    description='An universal tool for checking commits on GitHub',
    long_description=long_description,
    author='Martin Šafránek',
    author_email='gismocz@gmail.com',
    keywords='github,commit,git',
    license='MIT License',
    url='https://github.com/TaIos/comitee',
    packages=find_packages(),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'committee=committee.committee:main',
        ],
    },
    install_requires=['Flask', 'click>=6'],
    zip_safe=False,
    python_requires='>=3.6',
    package_data={'committee': ['templates/*.html', 'static/*.css']},
)
