import os
import setuptools 

def read(*paths):
    with open(os.path.join(*paths), "r") as filename:
        return filename.read()


setuptools.setup(
    name                = 'SpotSync',
    version             = '0.1.0',
    description         = 'spotify last added favorite songs synced with playlist',
    long_description    = (read('README.md')),
    url                 = 'https://github.com/freeek3/SpotSync',
    author              = 'Lars Mueller',
    author_email        = 'me@larsmueller.me',
    license             = '',
    py_modules          = ['spotsync'],
    install_requires=[
        'spotipy==2.19.0',
    ],
    entry_points        ='''
        [console_scripts]
        spotsync=spotsync:spotsync
    '''
)
