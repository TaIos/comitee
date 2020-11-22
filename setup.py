from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = ''.join(f.readlines())

setup(
    name='committee_saframa6',
    version='0.3.7',
    description='An universal tool for checking commits on GitHub',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Martin Šafránek',
    author_email='gismocz@gmail.com',
    keywords='github,commit,git,flask',
    license='MIT License',
    url='https://github.com/TaIos/comitee',
    packages=find_packages(exclude=['test_my']),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Framework :: Flask',
        'Environment :: Console',
        'Environment :: Web Environment'

    ],
    entry_points={
        'console_scripts': [
            'committee=committee.committee:main',
        ],
    },
    install_requires=['Flask', 'click>=6', 'requests>=2.2'],
    extras_require={'test': ['pytest>=5', 'betamax', 'hashlib', 'hmac']},
    zip_safe=False,
    python_requires='>=3.6',
    package_data={'committee': ['templates/*.html', 'static/*.css']},
)
