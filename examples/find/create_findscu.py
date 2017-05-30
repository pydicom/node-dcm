#!/bin/env python3

# An example of creating an Find Service User

from node_dcm.users import Find

# The default sets a port of 0, which will find an open one
findU = Find(name="stanford-find")

# We are going to cheat, and get the names of all of our cookies from here:
# https://github.com/pydicom/dicom-cookies/blob/master/scripts/cookie_manifest.json

# Let's look for this patient
patient_name = "summer fog"

# The default find uses a model P (PATIENT) 
findU.find(to_port=11112,
           to_address='localhost',
           patient_name=patient_name)
