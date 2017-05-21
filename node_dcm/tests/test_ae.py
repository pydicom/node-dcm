'''

test_ae.py: Testing different AE bases (and learning about them too)

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

from node_dcm.logman import bot
import os
import signal
import threading
import time

from pydicom import read_file
from pydicom.dataset import Dataset
from pydicom.uid import (
    UID, 
    ImplicitVRLittleEndian
)

from node_dcm.base import (
    VerificationSCP, 
    StorageSCP, 
    FindSCP, 
    GetSCP, 
    MoveSCP
)

from pynetdicom3 import AE
from pynetdicom3 import (
    VerificationSOPClass, 
    StorageSOPClassList
)

from pynetdicom3.sop_class import (
    RTImageStorage,
    PatientRootQueryRetrieveInformationModelFind,
    PatientRootQueryRetrieveInformationModelGet,
    PatientRootQueryRetrieveInformationModelMove
)

from node_dcm.utils import get_installdir
install_dir = get_installdir()

from unittest import TestCase
import shutil
import sys
import tempfile

VERSION = sys.version_info[0]

'''
Service-Object-Pair (SOP) Classes and Service Class User/Service 
Class Provider are terms that define the DICOM Services and their 
role, either as client or server.

 - Service Class Provider (SCP) means a device functioning as a server (listening)
 - Service Class User (SCU) is a device that initiates communication.
 - An application entity (AE) can be one or more of these things.

'''

print("*** PYTHON VERSION %s APPLICATION ENTITY TESTING START ***" %(VERSION))


class TestApplicationEntity(TestCase):

    def setUp(self):
        dataset_base = os.path.join(install_dir, 'tests','dicom_files')
        self.dataset = read_file(os.path.join(dataset_base, 'RTImageStorage.dcm'))
        self.comp_dataset = read_file(os.path.join(dataset_base,
                                      'MRImageStorage_JPG2000_Lossless.dcm'))
        self.ae = None
        self.scp = None
        self.assoc = None

        print("\n---START----------------------------------------------")

    def tearDown(self):
        print("Stopping all Application Entities")
        if self.assoc is not None: self.assoc.release()
        if self.ae is not None: self.ae.stop()
        if self.scp is not None: self.scp.stop()

        print("---END--------------------------------------------------")
         

    def release_association(self):
        '''create association will create an association for the ae
        defined for the object, with an optional port and ipaddress.
        '''
        if self.assoc is not None:
            print("Releasing association") 
            self.assoc.release()
            print("Association is established? %s" %self.assoc.is_established)        
            self.assertTrue(self.assoc.is_established == False)


    def create_association(self,port=None,ipaddress=None):
        '''create association will create an association for the ae
        defined for the object, with an optional port and ipaddress.
        '''
        if ipaddress is None:
            ipaddress = 'localhost'
        if port is None:
            port = 11112
        if self.ae is not None:
            self.assoc = self.ae.associate(ipaddress, port)
            print("Association is established? %s" %self.assoc.is_established)        
            self.assertTrue(self.assoc.is_established)


    def test_verification_scp(self):
        '''test the verification scp
        '''
        print("Generating a verification SCP, and starting.")
        self.scp = VerificationSCP()
        self.scp.start()

        print("Generating a service class user (ae) to send echo.")
        self.ae = AE(scu_sop_class=[VerificationSOPClass])
        self.create_association()

        print("Sending an echo.")
        echo = self.assoc.send_c_echo()
        print(echo.__dict__)

        self.release_association()
        self.assertTrue(self.assoc.is_established == False)
        

    def test_storage_scp(self):
        '''test the storage scp
        '''

        print("Generating a Storage SCP, and starting.")
        self.scp = StorageSCP()
        self.scp.start()

        print("Generating a service class user to send dataset.")
        self.ae = AE(scu_sop_class=[RTImageStorage])
        self.create_association()

        print("Sending dataset %s" %os.path.basename(self.dataset.filename))
        response = self.assoc.send_c_store(self.dataset)
        print(response.__dict__)
        

    def test_find_scp(self):
        '''test the find scp
        '''

        print("Generating a Find SCP, and starting.")
        self.scp = FindSCP()
        self.scp.status = self.scp.success
        self.scp.start()
        ds = get_patient()

        print("Generating a service class user to query.")
        self.ae = AE(scu_sop_class=[PatientRootQueryRetrieveInformationModelFind])
        self.create_association()

        print("Running queries, checking for status 0 (success)")
        for (status, ds) in self.assoc.send_c_find(ds, query_model='P'):
            self.assertEqual(int(status), 0x0000)


    def test_get_scp(self):
        '''test the Get scp
        '''
        self.scp = GetSCP()
        self.scp.start()
        ds = get_patient()

        print("Generating a service class user to retrieve.")
        self.ae = AE(scu_sop_class=[PatientRootQueryRetrieveInformationModelGet])
        self.create_association()

        print("Running retrieval, checking for status 0 (success)")
        for (status, ds) in self.assoc.send_c_get(ds, query_model='P'):
            self.assertEqual(int(status), 0x0000)


def get_patient():
    '''get_patient is a helper function to return a query patient
    '''
    print("Generating a dataset query")
    ds = Dataset()
    ds.PatientName = '*'
    ds.QueryRetrieveLevel = "PATIENT"
    print(ds)
    return ds


if __name__ == '__main__':
    unittest.main()
