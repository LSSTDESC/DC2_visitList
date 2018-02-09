#!/usr/bin/env python
import distutils
from distutils.core import setup
import os

description = "Code for generating the list of visits to simulate in DC2."

PACKAGENAME = 'DC2visitGen'
packageDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), PACKAGENAME)+'/code'

setup(name= "DC2visitGen",
      version= "0.1",
      description= description,
      packages=[PACKAGENAME],
      package_dir={PACKAGENAME: packageDir},
      url= "https://github.com/LSSTDESC/DC2_visitList",
      author= "Humna Awan for DESC",
      author_email= "humna.awan@rutgers.edu"
     )