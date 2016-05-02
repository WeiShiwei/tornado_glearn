#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os , glob
import hashlib
BLOCKSIZE = 65536

from os import environ
from os.path import dirname
from os.path import join
from os.path import exists
from os.path import expanduser
from os.path import isdir
from os import listdir
from os import makedirs

GLDJC_IDENTITY = 'gldjc'
AUTHENTICATED_IDENTITIS = ["gldjc",'gldzb']
# ---------------------------------------------------------
dependence_path = os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../../dependence')
jarpath = os.path.join(dependence_path, "ansj_seg/lib")

# ---------------------------------------------------------
crfpp_dependence_path = os.path.join( os.path.abspath(os.path.dirname(__file__)) , 'dependence')
templates_path = os.path.join( crfpp_dependence_path , 'templates' )
conlleval_path = os.path.join(crfpp_dependence_path,'conlleval')
perl_path = os.path.join(crfpp_dependence_path, 'ActivePerl-5.18.2.1802-i686-linux-64int-glibc-2.5-298023/perl/bin')
  
# models_path = os.path.join( os.path.abspath(os.path.dirname(__file__)) , 'models' )
# if not os.path.exists(models_path):
#     os.makedirs(models_path)
# train_corpus_path = os.path.join( os.path.abspath(os.path.dirname(__file__)) , 'train_corpus' )
# if not os.path.exists(train_corpus_path): 
#     os.makedirs(train_corpus_path)

validate_models_path = os.path.join( os.path.abspath(os.path.dirname(__file__)) , 'validate_models' )
if not os.path.exists(validate_models_path):
    os.makedirs(validate_models_path)

ixx_glodon_path = os.path.join( os.path.abspath(os.path.dirname(__file__)) , 'ixx_glodon' )

def sha1_file( source ):
  hasher = hashlib.md5()
  with open(source, 'rb') as afile:
    buf = afile.read(BLOCKSIZE)
    while len(buf) > 0:
      hasher.update(buf)
      buf = afile.read(BLOCKSIZE)
  hasher.update( source )
  return hasher.hexdigest()

pprocess_limit = 5


# ---------------------------------------------------------
def get_data_home( data_home=None):
    """Return the path of the scikit-learn data dir.

    This folder is used by some large dataset loaders to avoid
    downloading the data several times.

    By default the data dir is set to a folder named 'scikit_learn_data'
    in the user home folder.

    Alternatively, it can be set by the 'SCIKIT_LEARN_DATA' environment
    variable or programmatically by giving an explit folder path. The
    '~' symbol is expanded to the user home folder.

    If the folder does not already exist, it is automatically created.
    """
    if data_home is None:
        data_home = environ.get('SCIKIT_LEARN_DATA',
                                join('~', 'crf_learn_data'))
    data_home = expanduser(data_home)
    if not exists(data_home):
        makedirs(data_home)
    return data_home

def get_model_home( model_home=None):
    """Return the path of the scikit-learn data dir.

    This folder is used by some large dataset loaders to avoid
    downloading the data several times.

    By default the data dir is set to a folder named 'scikit_learn_data'
    in the user home folder.

    Alternatively, it can be set by the 'SCIKIT_LEARN_DATA' environment
    variable or programmatically by giving an explit folder path. The
    '~' symbol is expanded to the user home folder.

    If the folder does not already exist, it is automatically created.
    """
    if model_home is None:
        model_home = environ.get('SCIKIT_LEARN_MODEL',
                                join('~', 'crf_learn_model'))
    model_home = expanduser(model_home)
    if not exists(model_home):
        makedirs(model_home)
    return model_home
