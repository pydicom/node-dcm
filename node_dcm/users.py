'''

users.py: dicom services user classes

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
import os
import time

from pydicom import read_file
from pydicom.dataset import Dataset

from pynetdicom3 import (
    AE, 
    VerificationSOPClass,
    QueryRetrieveSOPClassList, 
    StorageSOPClassList
)

from pynetdicom3.sop_class import Status

from .status import (
    success,
    failure,
    pending,
    testing,
    cancel,
    warning
)


from node_dcm.base import BaseSCU
from node_dcm.utils import get_dcm_files

class Echo(BaseSCU):

    description='''The echoscu application implements a Service Class User
                   (SCU) for the Verification SOP Class. It sends a DICOM
                   C-ECHO message to a Service Class Provider (SCP) and
                   waits for a response. The application can be used to
                   verify basic DICOM connectivity.'''


    def __init__(self, port=11112, peer=None, peer_port=None, 
                       peer_name="ANY-SCP", name='ECHOSCU', prefer_uncompr=True,
                       prefer_little=False, repeat=1, prefer_big=False, 
                       implicit=False, timeout=None, dimse_timeout=None,
                       acse_timeout=60, pdu_max=16382, start=False, abort=False):

        '''
        :param port: the port to use, default is 11112.
        :param peer: the hostname of DICOM peer (not required)
        :param repeat: repeat N times (default is 1)
        :param name: the title/name for the ae. 'ECHOSCU' is used if not defined.
        :param prefer_uncompr: prefer explicit VR local byte order (default)
        :param prefer_little: prefer explicit VR little endian TS
        :param perfer_big: prefer explicit VR big endian TS
        :param implicit: accept implicit VR little endian TS only
        :param timeout: timeout for connection requests (default None)
        :param acse_timeout: timeout for ACSE messages (default 60)
        :param dimse_timeout: timeout for the DIMSE messages (default None) 
        :param pdu_max: set max receive pdu to n bytes (4096..131072) default 16382
        :param start: if True, start the ae. (default False)
        :param abort: if True, abort the association after releasing it (default False)
        ''' 
        self.port = port
        self.repeat = repeat
        self.abort = abort
     
        # Update preferences
        self.update_transfer_syntax(prefer_uncompr=prefer_uncomp,
                                    prefer_little=prefer_little,
                                    prefer_big=prefer_big,
                                    implicit=implicit)

        ae = AE(scp_sop_class=[VerificationSOPClass], 
                scu_sop_class=[],
                port=self.port,
                transfer_syntax=self.transfer_syntax)

        # Set timeouts, name, transfer
        ae.ae_title=name
        ae.maximum_pdu_size = pdu_max
        ae.network_timeout = timeout
        ae.acse_timeout = acse_timeout
        ae.dimse_timeout = dimse_timeout
        BaseSCU.__init__(self,ae=ae)

        if start is True:

            # Make the association
            assoc = self.make_assoc(address=peer,
                                    peer_name=peer_name,
                                    pdu_max=pdu_max,
                                    port=peer_port)

            self.send_echo()


    def send_echo(self):
        '''send an echo repeat times, and close the association when finished'''

        # If we successfully Associated then send N DIMSE C-ECHOs
        if self.assoc.is_established:

            for ii in range(self.repeat):
                status = assoc.send_c_echo()

            if status is not None:

                # Abort or release association
                if self.abort:
                    self.assoc.abort()
                else:
                    self.assoc.release()


    def on_c_echo(self,delay=None):
        '''Callback for ae.on_c_echo
        :param delay: Wait (delay) in seconds before sending response (int/float)
        '''
        if delay is None:
            delay = self.delay
        time.sleep(delay)
        
        if self.send_abort:
            self.ae.active_associations[0].abort()



class Store(BaseSCU):

    description='''Store implementis a Service Class User (SCU)
                   for the Storage Service Class. It sends a 
                   C-STORE message to a Storage Service Class 
                   Provider (SCP) and waits for a response. The 
                   application can be used to transmit DICOM
                   images and other composite objectes, and should
                   be instantiated first and then used to send'''

    out_of_resources = failure.out_of_resources
    ds_doesnt_match_sop_fail = failure.ds_doesnt_match_sop
    cant_understand = failure.cant_understand
    coercion_of_elements = warning.coercion_of_elements
    ds_doesnt_match_sop_warn = warning.ds_doesnt_match_sop
    elem_discard = warning.element_discard
    success = success.empty

    def __init__(self, port=11112, peer=None, to_port=None, 
                       to_name="ANY-SCP", name='STORESCU', prefer_uncompr=True,
                       prefer_little=False, repeat=1, prefer_big=False, 
                       implicit=False, timeout=None, dimse_timeout=None,
                       acse_timeout=60, pdu_max=16382, start=False):

        '''
        :param port: the port to use, default is 11112.
        :param peer: the hostname of DICOM peer (not required)
        :param toport: the port of the peer to send to
        :parm toname: the name of the peer to send to
        :param repeat: repeat N times (default is 1)
        :param name: the title/name for the ae. 'ECHOSCU' is used if not defined.
        :param prefer_uncompr: prefer explicit VR local byte order (default)
        :param prefer_little: prefer explicit VR little endian TS
        :param perfer_big: prefer explicit VR big endian TS
        :param implicit: accept implicit VR little endian TS only
        :param timeout: timeout for connection requests (default None)
        :param acse_timeout: timeout for ACSE messages (default 60)
        :param dimse_timeout: timeout for the DIMSE messages (default None) 
        :param pdu_max: set max receive pdu to n bytes (4096..131072) default 16382
        :param start: if True, start the ae. (default False)
        :param abort: if True, abort the association after releasing it (default False)
        ''' 
        self.port = port
        self.repeat = repeat
        self.abort = abort
        self.update_peer(peer=peer,
                         port=to_port,
                         name=to_name)
     
        # Update preferences
        self.update_transfer_syntax(prefer_uncompr=prefer_uncomp,
                                    prefer_little=prefer_little,
                                    prefer_big=prefer_big,
                                    implicit=implicit)

        ae = AE(ae_title=name,
                port=self.port,
                scu_sop_class=StorageSOPClassList,
                scp_sop_class=[],
                transfer_syntax=self.transfer_syntax)


        # Set timeouts, name, transfer
        ae.ae_title=name
        ae.maximum_pdu_size = pdu_max
        ae.network_timeout = timeout
        ae.acse_timeout = acse_timeout
        ae.dimse_timeout = dimse_timeout
        BaseSCU.__init__(self,ae=ae)
        self.status = self.success


    def send(self,dcm_files,to_address=None,to_port=None,to_name=None)
        '''send will send one or more dicom files or folders of dicom files, to
        a peer. The peer can be instantiated with the instance and used, or redefined 
        at any time with the send function.
        '''
        self.release_assoc()
        self.update_peer(address=to_address,
                         port=to_port,
                         name=to_name)

        # Make the association -- #QUESTION - new association for each one?
        assoc = self.make_assoc(address=peer,
                                peer_name=peer_name,
                                pdu_max=pdu_max,
                                port=peer_port)

        # Obtain valid dicom files
        dcm_files = get_dcm_files(dcm_files,
                                  check=True)

        # Send each dataset
        for dcm_file in dcm_files:
            with open(dcm_file, 'rb') as filey:
                dataset = read_file(filey, force=True)
            
            if self.assoc.is_established:
                bot.info('Sending file: {0!s}'.format(dcm_file))
                status = self.assoc.send_c_store(dataset)

        self.assoc.release()


    def on_c_store(self, ds):
        '''Callback for ae.on_c_store'''
        time.sleep(self.delay)
        return self.status


class Find(BaseSCP):
    
    description='''The findscp application implements a Service Class
                   Provider (SCP) for the Query/Retrieve (QR) Service Class
                   and the Basic Worklist Management (BWM) Service Class.
                   findscp only supports query functionality using the C-FIND
                   message. It receives query keys from an SCU and sends a
                   response. The application can be used to test SCUs of the
                   QR and BWM Service Classes.'''

    out_of_resources = failure.out_of_resources
    identifier_doesnt_match_sop = failure.identifier_doesnt_match_sop
    unable_to_process = failure.unable_to_process
    matching_terminated_cancel = cancel.matching_terminated
    success = success.matching
    pending_matches = pending.matches
    pending_warning = pending.matches_warning

    def __init__(self, dicom_home,port=None,name=None,prefer_uncompr=True,prefer_little=False,
                       prefer_big=False, implicit=False, timeout=None, dimse_timeout=None,
                       acse_timeout=None, pdu_max=None):

        '''create a FindSCP (Service Class Provider) for query/retrieve and basic workflow management
        :param dicom_home: must be the base folder of dicom files **TODO: make this more robust
        :param port: TCP/IP port number to listen on
        :param name: the title/name for the ae. 'ECHOSCP' is used if not defined.
        :param prefer_uncompr: prefer explicit VR local byte order (default)
        :param prefer_little: prefer explicit VR little endian TS
        :param perfer_big: prefer explicit VR big endian TS
        :param implicit: accept implicit VR little endian TS only
        :param timeout: timeout for connection requests (default None)
        :param acse_timeout: timeout for ACSE messages (default 60)
        :param dimse_timeout: timeout for the DIMSE messages (default None) 
        :param pdu_max: set max receive pdu to n bytes (4096..131072) default 16382
        '''

        # First validate port
        if port is None:
            port = 11112
        self.port = port

        # Base for dicom files (we can do better here)
        self.base = dicom_home

        if pdu_max is None:
            pdu_max = 16384

        if acse_timeout is None:
            acse_timeout = 60
 
        if name is None:
            name = 'FINDSCP'

        ae = AE(scp_sop_class=QueryRetrieveSOPClassList,               
                transfer_syntax=self.transfer_syntax,
                scu_sop_class=[],
                ae_title=name,
                port=self.port)

        # Set timeouts, name, transfer
        ae.maximum_pdu_size = pdu_max
        ae.network_timeout = timeout
        ae.acse_timeout = acse_timeout
        ae.dimse_timeout = dimse_timeout

        BaseSCP.__init__(self,ae=ae)
        self.status = self.pending_matches
        self.cancel = False


    def on_c_find(self, query_level, patient_name):

        time.sleep(self.delay)
        dicom_files = glob("%s/*.dcm" %(self.base))

        for dcm in dcm_files:
            dataset = read_file(dcm, force=True)

            ds = Dataset()
            ds.QueryRetrieveLevel = dataset.QueryRetrieveLevel
            ds.RetrieveAETitle = self.ae.ae_title
            ds.PatientName = dataset.PatientName
            if ds.PatientName == patient_name and ds.QueryRetrieveLevel == query_level: 
                yield 0xff00, ds

            else:
                yield self.status, None
                
            if self.cancel:
                yield self.matching_terminated_cancel, None
                return

            yield self.status, None


    def on_c_cancel_find(self):
        '''Callback for ae.on_c_cancel_find'''
        self.cancel = True



class Get(BaseSCP):

    description='''The getscp application implements a Service Class
                   Provider (SCP) for the Query/Retrieve (QR) Service Class
                   and the Basic Worklist Management (BWM) Service Class.
                   getscp only supports query functionality using the C-GET
                   message. It receives query keys from an SCU and sends a
                   response. The application can be used to test SCUs of the
                   QR and BWM Service Classes.'''
 

    out_of_resources_match = failure.out_of_resources_match
    out_of_resources_unable = failure.out_of_resources_unable
    identifier_doesnt_match_sop = failure.identifier_doesnt_match_sop
    unable = failure.unable_to_process
    cancel_status = cancel.suboperation

    warning = warning.suboperation
    success = success.suboperation
    pending = pending.suboperation

    def __init__(self, dicom_home,port=None,name=None,prefer_uncompr=True,prefer_little=False,
                       prefer_big=False, implicit=False, timeout=None, dimse_timeout=None,
                       acse_timeout=None, pdu_max=None, start=False):
        '''
        :param dicom_home: must be the base folder of dicom files **TODO: make this more robust
        :param port: TCP/IP port number to listen on
        :param name: the title/name for the ae. 'ECHOSCP' is used if not defined.
        :param prefer_uncompr: prefer explicit VR local byte order (default)
        :param prefer_little: prefer explicit VR little endian TS
        :param perfer_big: prefer explicit VR big endian TS
        :param implicit: accept implicit VR little endian TS only
        :param timeout: timeout for connection requests (default None)
        :param acse_timeout: timeout for ACSE messages (default 60)
        :param dimse_timeout: timeout for the DIMSE messages (default None) 
        :param pdu_max: set max receive pdu to n bytes (4096..131072) default 16382
        '''

        # First validate port
        if port is None:
            port = 11112
        self.port = port

        if pdu_max is None:
            pdu_max = 16384

        if acse_timeout is None:
            acse_timeout = 60
 
        if name is None:
            name = 'GETSCP'

        self.base = dicom_home

        scp_sop_class = StorageSOPClassList.copy()
        scp_sop_class.extend(QueryRetrieveSOPClassList)

        ae = AE(scp_sop_class=scp_classes,
                transfer_syntax=self.transfer_syntax,
                scu_sop_class=[],
                ae_title=name
                port=port)

        BaseSCP.__init__(self,ae=ae)

        self.ae.maximum_pdu_size = max_pdu
        self.ae.network_timeout = timeout
        self.ae.acse_timeout = acse_timeout
        self.ae.dimse_timeout = dimse_timeout

        self.status = self.success
        self.cancel = False

        if start is True:
            self.start()


    def on_c_get(self, patient_name, query_level):
        '''Callback for ae.on_c_get'''

        time.sleep(self.delay)

        # I think here I need to do the search/match
        #TODO: this needs to search some metddata for files
        dcm_files = glob("%s/*.dcm" %(self.base))

        yield len(dcm_files)

        for dcm in dcm_files:

            if self.cancel:
                yield self.cancel, None
                return

            ds = read_file(dcm, force=True)
            yield 0xFF00, ds


    def on_c_cancel_get(self):
        '''Callback for ae.on_c_cancel_get'''
        self.cancel = True





class Move(BaseSCP):

    description='''The movescp application implements a Service Class
                   Provider (SCP) for the Query/Retrieve (QR) Service Class 
                   and the Basic Worklist Management (BWM) Service Class.
                   movescp only supports query functionality using the C-MOVE
                   message. It receives query keys from an SCU and sends a
                   response. The application can be used to test SCUs of the
                   QR and BWM Service Classes.'''

    out_of_resources_match = failure.out_of_resources_match
    out_of_resources_unable = failure.out_of_resources_unable
    move_destination_unknown = failure.move_destination_unknown
    identifier_doesnt_match_sop = failure.identifier_doesnt_match_sop
    unable_to_process = failure.unable_to_process
    cancel_status = cancel.matching_terminated

    warning = warning.suboperation
    success = success.suboperation
    pending = pending.suboperation
 
    def __init__(self, dicom_home,port=None,name=None,prefer_uncompr=True,prefer_little=False,
                       prefer_big=False, implicit=False, timeout=None, dimse_timeout=None,
                       acse_timeout=None, pdu_max=None, start=False):
        '''
        :param dicom_home: must be the base folder of dicom files **TODO: make this more robust
        :param port: TCP/IP port number to listen on
        :param name: the title/name for the ae. 'ECHOSCP' is used if not defined.
        :param prefer_uncompr: prefer explicit VR local byte order (default)
        :param prefer_little: prefer explicit VR little endian TS
        :param perfer_big: prefer explicit VR big endian TS
        :param implicit: accept implicit VR little endian TS only
        :param timeout: timeout for connection requests (default None)
        :param acse_timeout: timeout for ACSE messages (default 60)
        :param dimse_timeout: timeout for the DIMSE messages (default None) 
        :param pdu_max: set max receive pdu to n bytes (4096..131072) default 16382
        '''

        if port is None:
            port = 11112
        self.port = port

        if pdu_max is None:
            pdu_max = 16384

        if acse_timeout is None:
            acse_timeout = 60
 
        if name is None:
            name = 'MOVESCP'

        self.base = dicom_home

        ae = AE(ae_title=name,
                port=self.port,
                scu_sop_class=StorageSOPClassList,
                scp_sop_class=QueryRetrieveSOPClassList,
                transfer_syntax=self.transfer_syntax)

        BaseSCP.__init__(self,ae=ae)
        self.status = self.pending
        self.cancel = False

        self.ae.maximum_pdu_size = args.max_pdu
        self.ae.network_timeout = args.timeout
        self.ae.acse_timeout = args.acse_timeout
        self.ae.dimse_timeout = args.dimse_timeout

        if start is True:
            self.start()


    def on_c_move(self, ds, move_aet):
        '''Callback for ae.on_c_move'''

        time.sleep(self.delay)

        # I think here I need to do the search/match
        #TODO: this needs to search some metddata for files
        dcm_files = glob("%s/*.dcm" %(self.base))

        # Number of matches
        yield len(dcm_files)

        # Matching datasets to send
        for dcm in dcm_files:

            if self.cancel:
                yield self.cancel, None
                return

            ds = read_file(dcm, force=True)
            yield 0xff00, ds


    def on_c_cancel_find(self):
        '''Callback for ae.on_c_cancel_move'''
        self.cancel = True
