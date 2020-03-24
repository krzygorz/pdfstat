from setuptools import setup

setup(name='pdfstat',
      version='0.1',
      description="Track progress of reading pdf documents.",
      url='http://github.com/krzygorz/pdfstat',
      author='krzygorz',
      author_email='krzygorz@gmail.com',
      license='MIT',
      packages=['pdfstat'],
      install_requires=[],
      zip_safe=True,
      entry_points = {
        'console_scripts': ['pdfstat=pdfstat.pdfstat:main'],
      },
      )