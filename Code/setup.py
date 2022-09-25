from distutils.core import setup
import py2exe

from distutils.core import setup # Need this to handle modules
import py2exe 
import math # We have to import all modules used in our program
import os
import PySimpleGUI as sg
import string
from tkinter import messagebox
from ast import literal_eval
import shutil

import database_functions as dbfunc
import functions as func
 
import random
import serial

import sqlite3
from sqlite3 import Error

from configparser import ConfigParser 

setup(console=['main.py'])