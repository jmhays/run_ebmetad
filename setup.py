import setuptools


if __name__ == "__main__":
    setuptools.setup(
        name='run_ebmetad',
        version='0.0.1',
        description='Package to run EBMetaD simulations',
        author='Jennifer Hays',
        author_email='jmh5sf@virginia.edu',
        url="https://github.com/jmhays/run_ebmetad",
        license='BSD-3-Clause',
        packages=setuptools.find_packages(),
        install_requires=[],
        extras_require={
            'docs': [
                'sphinx',
                'sphinxcontrib-napoleon',
                'sphinx_rtd_theme',
                'numpydoc',
            ],
            'tests': [
                'pytest',
                'pytest-cov',
                'pytest-pep8',
                'tox',
            ],
        },
        tests_require=[
            'pytest',
            'pytest-cov',
            'pytest-pep8',
            'tox',
        ],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3',
        ],
        zip_safe=False,
    )
