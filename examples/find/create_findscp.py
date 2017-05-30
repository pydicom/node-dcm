#!/bin/env python3

# An example of creating an Find Service Provider
# I must admit, I think needing to find, check, and then query over actual files is
# slow and suboptimal, but for a simple service that aims to move/find files to
# move from temporary to more robust cloud storage, I am testing this out.

# dicom_home is the top level directory with dicoms to search
# By default, update_on_find is False, meaning we load the files 
# once and not again.

from node_dcm.providers import Find

findP = Find(name="stanford-find", dicom_home="/data", start=True)

# The same, but update File list on each request
findP = Find(name="stanford-find", 
             dicom_home="/data", 
             update_on_find=True,
             start=True)
