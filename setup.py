from setuptools import setup

setup(
   name='libraryApp',
   version='1.0',
   description='CSSE433 homework',
   author='Fred',
   author_email='zhangq2@rose-hulman.com',
   packages=[''],  #same as name
   install_requires=['redis', 'pymongo', 'neo4j-driver', 'python-memcached', 'click'], #external packages as dependencies
   py_modules=['library_cli'],
   entry_points='''
       [console_scripts]
       library_cli=library_app.library_app_cli:safe_cli
   ''',
)