from setuptools import setup

setup(
   name='libraryApp',
   version='1.0',
   description='CSSE433 homework',
   author='Fred',
   author_email='zhangq2@rose-hulman.com',
   packages=[''],  #same as name
   install_requires=['redis'], #external packages as dependencies
)