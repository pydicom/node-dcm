'''
utils.py: utility functions for working with node_dcm

The MIT License (MIT)

Copyright (c) 2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

import collections
import os
import re
import requests

import shutil
import json
import node_dcm.__init__ as hello

from node_dcm.validate import (
    validate_dicoms
)

from .logman import bot
import sys

import subprocess

import tempfile
import zipfile


# Python less than version 3 must import OSError
if sys.version_info[0] < 3:
    from exceptions import OSError


######################################################################################
# Local commands and requests
######################################################################################


def get_installdir():
    '''get_installdir returns the installation directory of the application
    '''
    return os.path.abspath(os.path.dirname(hello.__file__))


def run_command(cmd,error_message=None,sudopw=None,suppress=False):
    '''run_command uses subprocess to send a command to the terminal.
    :param cmd: the command to send, should be a list for subprocess
    :param error_message: the error message to give to user if fails, 
    if none specified, will alert that command failed.
    :param execute: if True, will add `` around command (default is False)
    :param sudopw: if specified (not None) command will be run asking for sudo
    '''
    if sudopw == None:
        sudopw = os.environ.get('pancakes',None)

    if sudopw is not None:
        cmd = ' '.join(["echo", sudopw,"|","sudo","-S"] + cmd)
        if suppress == False:
            output = os.popen(cmd).read().strip('\n')
        else:
            output = cmd
            os.system(cmd)
    else:
        try:
            process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            output, err = process.communicate()
        except OSError as error: 
            if error.errno == os.errno.ENOENT:
                bot.logger.error(error_message)
            else:
                bot.logger.error(error)
            return None
    
    return output


############################################################################
## FILE OPERATIONS #########################################################
############################################################################


def get_dcm_files(contenders,check=True):
    '''get_dcm_files will take a list of single dicom files or directories,
    and return a single list of complete paths to all files
    '''
    if isinstance(contenders,str):
        contenders = [contenders]

    dcm_files = []
    for contender in contenders:
        if os.path.isdir(contender):
            dicom_dir = glob("%s/*.dcm" %contender)
            bot.debug("Found %s dicom files in %s" %(len(dicom_dir),
                                                     os.path.basename(dicom_dir)))
            dcm_files.extend(dicom_dir)
        else:
            if contender.endswith('.dcm'):
                bot.debug("Adding single file %s" %(contender))

    dcm_files = validate_dicoms(dcm_files)
    return dcm_files


def write_file(filename,content,mode="w"):
    '''write_file will open a file, "filename" and write content, "content"
    and properly close the file
    '''
    with open(filename,mode) as filey:
        filey.writelines(content)
    return filename


def write_json(json_obj,filename,mode="w",print_pretty=True):
    '''write_json will (optionally,pretty print) a json object to file
    :param json_obj: the dict to print to json
    :param filename: the output file to write to
    :param pretty_print: if True, will use nicer formatting   
    '''
    with open(filename,mode) as filey:
        if print_pretty == True:
            filey.writelines(json.dumps(json_obj, indent=4, separators=(',', ': ')))
        else:
            filey.writelines(json.dumps(json_obj))
    return filename


def read_file(filename,mode="r"):
    '''write_file will open a file, "filename" and write content, "content"
    and properly close the file
    '''
    with open(filename,mode) as filey:
        content = filey.readlines()
    return content


def read_json(filename,mode='r'):
    '''read_json reads in a json file and returns
    the data structure as dict.
    '''
    with open(filename,mode) as filey:
        data = json.load(filey)
    return data


def download_repo(repo_url,destination,commit=None):
    '''download_repo
    :param repo_url: the url of the repo to clone from
    :param destination: the full path to the destination for the repo
    '''
    command = "git clone %s %s" %(repo_url,destination)
    os.system(command)
    return destination
