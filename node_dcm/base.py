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

from logman import bot
import os
import socket
import time
import threading

from pydicom import read_file
from pydicom.dataset import Dataset
from pydicom.uid import (
    UID, 
    ImplicitVRLittleEndian
)

from pynetdicom3 import (
    AE, 
    VerificationSOPClass
)

from pynetdicom3.sop_class import (
    CTImageStorage, 
    MRImageStorage,
    RTImageStorage,
    PatientRootQueryRetrieveInformationModelFind,                                   
    StudyRootQueryRetrieveInformationModelFind,
    ModalityWorklistInformationFind,
    PatientStudyOnlyQueryRetrieveInformationModelFind,
    PatientRootQueryRetrieveInformationModelGet,
    StudyRootQueryRetrieveInformationModelGet,
    PatientStudyOnlyQueryRetrieveInformationModelGet,
    PatientRootQueryRetrieveInformationModelMove,
    StudyRootQueryRetrieveInformationModelMove,
    PatientStudyOnlyQueryRetrieveInformationModelMove,
    Status
)

from .status import (
    success,
    failure,
    pending,
    testing,
    cancel,
    warning
)

class BaseSCP(threading.Thread):
    '''Base class for the SCP classes'''

    bad_status = testing.test

    def __init__(self,ae=None):

        self.ae = ae
        if self.ae is None:
            bot.logger.error("The BaseSCP must be instantiated with an Application Entity (AE).")
            sys.exit(1)

        self.ae.on_c_echo = self.on_c_echo
        self.ae.on_c_store = self.on_c_store
        self.ae.on_c_find = self.on_c_find
        self.ae.on_c_get = self.on_c_get
        self.ae.on_c_move = self.on_c_move
        threading.Thread.__init__(self)
        self.daemon = True
        self.delay = 0
        self.send_abort = False

    def run(self):
        '''The thread run method'''
        self.ae.start()

    def stop(self):
        '''Stop the SCP thread'''
        self.ae.stop()

    def abort(self):
        '''Abort any associations'''
        for assoc in self.ae.active_associations:
            assoc.abort()

    def release(self):
        '''Release any associations'''
        for assoc in self.ae.active_associations:
            assoc.release()

    def on_c_echo(self):
        '''Callback for ae.on_c_echo'''
        return self.raise_not_implemented('on_c_echo')

    def on_c_store(self, ds):
        '''Callback for ae.on_c_store'''
        return self.raise_not_implemented('on_c_store')

    def on_c_find(self, ds):
        '''Callback for ae.on_c_find'''
        return self.raise_not_implemented('on_c_find')

    def on_c_cancel_find(self):
        '''Callback for ae.on_c_cancel_find'''
        return self.raise_not_implemented('on_c_cancel_find')

    def on_c_get(self, ds):
        '''Callback for ae.on_c_get'''
        return self.raise_not_implemented('on_c_get')

    def on_c_cancel_get(self):
        '''Callback for ae.on_c_cancel_get'''
        return self.raise_not_implemented('on_c_cancel_get')

    def on_c_move(self, ds, move_aet):
        '''Callback for ae.on_c_move'''
        return self.raise_not_implemented('on_c_move')

    def on_c_cancel_move(self):
        '''Callback for ae.on_c_cancel_move'''
        return self.raise_not_implemented('on_c_cancel_move')

    def raise_not_implemented(self,name):
        return raise RuntimeError("%s is not implemented for this application entity." %name)


class VerificationSCP(BaseSCP):
    '''A threaded verification SCP used for testing'''

    def __init__(self, port=None):

        if port is None:
            port = 11112
        ae = AE(scp_sop_class=[VerificationSOPClass], port=port)
        BaseSCP.__init__(self,ae=ae)


    def on_c_echo(self,delay=None):
        '''Callback for ae.on_c_echo
        :param delay: Wait (delay) in seconds before sending response (int/float)
        '''
        if delay is None:
            delay = self.delay
        time.sleep(delay)
        
        if self.send_abort:
            self.ae.active_associations[0].abort()



class StorageSCP(BaseSCP):
    '''A threaded storage SCP used for testing'''

    out_of_resources = failure.out_of_resources
    ds_doesnt_match_sop_fail = failure.ds_doesnt_match_sop
    cant_understand = failure.cant_understand
    coercion_of_elements = failure.coercion_of_elements
    ds_doesnt_match_sop_warn = warning.ds_doesnt_match
    elem_discard = warning.element_discard
    success = success.empty

    def __init__(self, port=None):

        if port is None:
            port = 11112
        ae = AE(scp_sop_class=[PatientRootQueryRetrieveInformationModelMove,
                               StudyRootQueryRetrieveInformationModelMove,
                               PatientStudyOnlyQueryRetrieveInformationModelMove,
                               CTImageStorage,
                               RTImageStorage, MRImageStorage], port=port)
        BaseSCP.__init__(self,ae=ae)
        self.status = self.success

    def on_c_store(self, ds):
        '''Callback for ae.on_c_store'''
        time.sleep(self.delay)
        return self.status


class FindSCP(BaseSCP):
    '''A threaded dummy storage SCP used for testing'''

    out_of_resources = failure.out_of_resources
    identifier_doesnt_match_sop = failure.identifier_doesnt_match_sop
    unable_to_process = failure.unable_to_process
    matching_terminated_cancel = cancel.matching_terminated
    success = success.matching
    pending = pending.matches
    pending_warning = pending.matches_warning

    def __init__(self, port=None):

        if port is None:
            port = 11112
        ae = AE(scp_sop_class=[PatientRootQueryRetrieveInformationModelFind,
                               StudyRootQueryRetrieveInformationModelFind,
                               ModalityWorklistInformationFind,
                               PatientStudyOnlyQueryRetrieveInformationModelFind],
                               port=port)
        BaseSCP.__init__(self,ae=ae)
        self.status = self.pending
        self.cancel = False

    def on_c_find(self, ds):

        '''Callback for ae.on_c_find'''
        time.sleep(self.delay)
        ds = Dataset()
        ds.PatientName = '*'
        ds.QueryRetrieveLevel = "PATIENT"
        if not isinstance(self.status, Status):
            yield self.status, None
            return
        
        if self.status.status_type != 'Pending':
            yield self.status, None

        if self.cancel:
            yield self.matching_terminated_cancel, None

        yield self.status, ds

    def on_c_cancel_find(self):
        '''Callback for ae.on_c_cancel_find'''
        self.cancel = True


class GetSCP(BaseSCP):
    '''A threaded dummy storage SCP used for testing'''

    out_of_resources_match = failure.out_of_resources_match
    out_of_resources_unable = failure.out_of_resources_unable
    identifier_doesnt_match_sop = failure.identifier_doesnt_match_sop
    unable = failure.unable_to_process
    cancel_status = cancel.suboperation

    warning = warning.suboperation
    success = success.suboperation
    pending = pending.suboperation
 
    def __init__(self, port=None):
 
        if port is None:
            port = 11112

        ae = AE(scp_sop_class=[PatientRootQueryRetrieveInformationModelGet,
                                    StudyRootQueryRetrieveInformationModelGet,
                                    PatientStudyOnlyQueryRetrieveInformationModelGet,
                                    CTImageStorage],
                     scu_sop_class=[CTImageStorage],
                     port=port)

        BaseSCP.__init__(self,ae=ae)
        self.status = self.success
        self.cancel = False

    def on_c_get(self, ds):
        '''Callback for ae.on_c_get'''
        time.sleep(self.delay)
        ds = Dataset()
        ds.PatientName = '*'
        ds.QueryRetrieveLevel = "PATIENT"
        if self.status.status_type not in ['Pending', 'Warning']:
            yield 1
            yield self.status, None

        if self.cancel:
            yield 1
            yield self.cancel, None

        yield 2
        for ii in range(2):
            yield self.status, DATASET

    def on_c_cancel_get(self):
        '''Callback for ae.on_c_cancel_get'''
        self.cancel = True


class MoveSCP(BaseSCP):
    '''A threaded dummy storage SCP used for testing'''
    out_of_resources_match = failure.out_of_resources_match
    out_of_resources_unable = failure.out_of_resources_enable
    move_destination_unknown = failure.move_destination_unknown
    identifier_doesnt_match_sop = failure.identifier_doesnt_match_sop
    unable_to_process = failure.unable_to_process
    cancel_status = cancel.matching_terminated

    warning = warning.suboperation
    success = success.suboperation
    pending = pending.suboperation
 
    def __init__(self, port=None):

        if port is None:
            port = 11112

        ae = AE(scp_sop_class=[PatientRootQueryRetrieveInformationModelMove,
                              StudyRootQueryRetrieveInformationModelMove,
                              PatientStudyOnlyQueryRetrieveInformationModelMove,
                              RTImageStorage, CTImageStorage],
                     scu_sop_class=[RTImageStorage,
                                    CTImageStorage],
                     port=port)
        BaseSCP.__init__(self,ae=ae)
        self.status = self.pending
        self.cancel = False

    def on_c_move(self, ds, move_aet):
        '''Callback for ae.on_c_find'''
        time.sleep(self.delay)
        ds = Dataset()
        ds.PatientName = '*'
        ds.QueryRetrieveLevel = "PATIENT"

        # Check move_aet first
        if move_aet != b'TESTMOVE        ':
            yield 1
            yield None, None

        if self.status.status_type not in ['Pending', 'Warning']:
            yield 1
            yield 'localhost', 11113
            yield self.status, None

        if self.cancel:
            yield 1
            yield 'localhost', 11113
            yield self.cancel, None

        yield 2
        yield 'localhost', 11113
        for ii in range(2):
            yield self.status, DATASET

    def on_c_cancel_find(self):
        '''Callback for ae.on_c_cancel_move'''
        self.cancel = True
