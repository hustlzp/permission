from distutils.core import setup

setup(
    name='permission',
    version='0.4.1',
    author='Zhipeng Liu',
    author_email='hustlzp@qq.com',
    url='https://github.com/hustlzp/permission',
    packages=['permission'],
    license='MIT',
    description='Simple and flexible permission control for Flask app.',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)