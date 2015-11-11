import pypandoc

with open('README.rst', 'w+') as f:
    f.write(pypandoc.convert('README.md', 'rst'))
