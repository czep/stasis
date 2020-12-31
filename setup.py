from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='stasis-ssg',
    version='0.1.0',
    description='A simple static site generator with deployment to S3/Cloudfront',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/czep/stasis',
    author='Scott Czepiel',
    author_email='dev@czep.net',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Text Processing :: Markup :: Markdown'

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='static site generator, web development, blog',
    packages=find_packages(where='stasis'),
    python_requires='>=3.9, <4',
    install_requires=['jinja2', 'boto3', 'python-frontmatter'],

    package_data={
        'stasis': [
            'filters/*',
            'bootstrap/*'
        ],
    },

    entry_points={
        'console_scripts': [
            'stasis=stasis:main',
        ],
    },
)
