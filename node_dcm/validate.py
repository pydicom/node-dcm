'''
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

from .logman import bot
from pydicom import read_file
import socket
import sys
import os

def validate_port(port):
    if isinstance(port, int):
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        test_socket.bind((os.popen('hostname').read()[:-1], args.port))
    except socket.error:
        bot.error("Cannot listen on port {}, insufficient privileges or "
            "already in use".format(args.port))
        sys.exit()


def validate_dicoms(dcm_files):
    '''validate dicoms will test opening one or more dicom files, and return a list
    of valid files.
    :param dcm_files: one or more dicom files to test'''
    if not isinstance(dcm_files,list):
        dcm_files = [dcm_files]

    valids = []

    bot.debug("Checking %s dicom files for validation." %(len(dcm_files))
    for dcm_file in dcm_files:

        try:
            with open(dcm_file_in, 'rb') as filey:
                dataset = read_file(filey, force=True)
            bot.debug("%s is valid" %(os.path.basename(dcm_file)))
            valids.append(dcm_file)
             
        except IOError:
            bot.error('Cannot read input file {0!s}'.format(dcm_file))
            sys.exit(1)

    bot.info("Found %s valid dicom files" %(len(valids)))
    return valids
