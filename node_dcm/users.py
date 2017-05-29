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
from pydicom.dataset import (
    Dataset,
    FileDataset
)

from pynetdicom3 import (
    AE, 
    VerificationSOPClass,
    QueryRetrieveSOPClassList, 
    StorageSOPClassList
)

from pynetdicom3.sop_class import Status
from pynetdicom3.pdu_primitives import (
    SCP_SCU_RoleSelectionNegotiation
)

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


    def send(self,dcm_files,to_address=None,to_port=None,to_name=None):
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
            
            if not self.assoc.is_established:
                self.make_assoc()

            bot.info('Sending file: {0!s}'.format(dcm_file))
            status = self.assoc.send_c_store(dataset)

        self.assoc.release()


    def on_c_store(self, ds):
        '''Callback for ae.on_c_store'''
        time.sleep(self.delay)
        return self.status


class Find(BaseSCU):
    
    description='''The findscu application implements a Service Class User
                   (SCU) for the Query/Retrieve (QR) Service Class and the
                   Basic Worklist Management (BWM) Service Class. findscu
                   only supports query functionality using the C-FIND
                   message. It sends query keys to an SCP and waits for a
                   response. The application can be used to test SCPs of the
                   QR and BWM Service Classes.'''

    out_of_resources = failure.out_of_resources
    identifier_doesnt_match_sop = failure.identifier_doesnt_match_sop
    unable_to_process = failure.unable_to_process
    matching_terminated_cancel = cancel.matching_terminated
    success = success.matching
    pending_matches = pending.matches
    pending_warning = pending.matches_warning

    def __init__(self, name=None):

        '''create a FindSCU (Service Class USER) for query/retrieve
        :param name: the title/name for the ae. 'FINDSCU' is used if not defined.
        ''' 

        if name is None:
            name = 'FINDSCU'

        # Binding to port 0 lets the OS pick an available port
        ae = AE(scp_sop_class=[],               
                transfer_syntax=[ExplicitVRLittleEndian],
                scu_sop_class=QueryRetrieveSOPClassList,
                ae_title=name,
                port=0)

        BaseSCU.__init__(self,ae=ae)
        self.status = self.pending_matches
        self.cancel = False


    def find(self,keys,model=None,to_address=None,to_port=None,to_name=None,
             patient_name=None):
        '''send will send one or more dicom files or folders of dicom files, to
        a peer. The peer can be instantiated with the instance and used, or redefined 
        at any time with the send function.
        :params keys: a dictionary of keys/values to look up.
        '''
        if model is None:
            model = 'P'

        self.check_information_model(model)

        if patient_name is None:
            patient_name = "*"

        # Make the association -- #QUESTION - new association for each one?
        self.make_assoc(address=to_address,
                        peer_name=to_name,
                        port=to_port)

        # Create a query dataset
        dataset = Dataset()
        dataset.PatientName = patient_name
        dataset.QueryRetrieveLevel = "PATIENT"

        # Send query
        response = self.assoc.send_c_find(dataset, 
                                          query_model=model)

        time.sleep(1)
        for value in response:
            pass
            print(value)

        self.assoc.release()
        self.ae.quit()



class Get(BaseSCU):

    description='''The getscu application implements a Service Class User
                 (SCU) for the Query/Retrieve (QR) Service Class and the
                 Basic Worklist Management (BWM) Service Class. getscu
                 only supports query functionality using the C-GET
                 message. It sends query keys to an SCP and waits for a
                 response. The application can be used to test SCPs of the
                 QR and BWM Service Classes.'''

    cancel_status = cancel.suboperation
    warning = warning.suboperation
    success = success.suboperation
    pending = pending.suboperation

    def __init__(self, name=None):
        '''
        :param name: the title/name for the ae. 'ECHOSCP' is used if not defined.
        '''
        if name is None:
            name = 'GETSCU'

        scu_class = QueryRetrieveSOPClassList.copy()
        scu_class.extend(StorageSOPClassList)

        # Binding to port 0 lets the OS pick an available port
        ae = AE(scp_sop_class=[],
                transfer_syntax=[ExplicitVRLittleEndian],
                scu_sop_class=scu_class,
                ae_title=name
                port=0)

        BaseSCU.__init__(self,ae=ae)

        self.status = self.success
        self.cancel = False


    def get(self,model=None,to_address=None,to_port=None,to_name=None,
             patient_name=None):

        # Set the extended negotiation SCP/SCU role selection to allow us to receive
        #   C-STORE requests for the supported SOP classes
        # I don't totally understand this, leaving as is until test it out.
        ext_neg = []
        for context in self.ae.presentation_contexts_scu:
            tmp = SCP_SCU_RoleSelectionNegotiation()
            tmp.sop_class_uid = context.AbstractSyntax
            tmp.scu_role = False
            tmp.scp_role = True

            ext_neg.append(tmp)

        if model is None:
            model = 'P'

        self.check_information_model(model)

        if patient_name is None:
            patient_name = "*"

        # Make the association - updates self.assoc
        self.make_assoc(address=to_address,
                        peer_name=to_name,
                        port=to_port,
                        ext_neg=ext_neg)

        # Create a query dataset
        dataset = Dataset()
        dataset.PatientName = patient_name
        dataset.QueryRetrieveLevel = "PATIENT"

        # Send query
        if self.assoc.is_established:
            response = self.assoc.send_c_get(dataset, 
                                             query_model=model)

            time.sleep(1)
            if response is not None:
                for value in response:
                    pass

        self.assoc.release()
        self.ae.quit() # Not sure if we want to quit here


    def on_c_store(self,dataset):
        '''Function replacing ApplicationEntity.on_store(). Called when a dataset is
        received following a C-STORE. Write the received dataset to file
        :param dataset: the pydicom.Dataset sent via the C-STORE
        :returns status: a pynetdicom.sop_class.Status or int
                         A valid return status code, see PS3.4 Annex B.2.3 or the
                         StorageServiceClass implementation for the available statuses
        '''
        mode_prefix = 'UN'
        mode_prefixes = {'CT Image Storage' : 'CT',
                         'Enhanced CT Image Storage' : 'CTE',
                         'MR Image Storage' : 'MR',
                         'Enhanced MR Image Storage' : 'MRE',
                         'Positron Emission Tomography Image Storage' : 'PT',
                         'Enhanced PET Image Storage' : 'PTE',
                         'RT Image Storage' : 'RI',
                         'RT Dose Storage' : 'RD',
                         'RT Plan Storage' : 'RP',
                         'RT Structure Set Storage' : 'RS',
                         'Computed Radiography Image Storage' : 'CR',
                         'Ultrasound Image Storage' : 'US',
                         'Enhanced Ultrasound Image Storage' : 'USE',
                         'X-Ray Angiographic Image Storage' : 'XA',
                         'Enhanced XA Image Storage' : 'XAE',
                         'Nuclear Medicine Image Storage' : 'NM',
                         'Secondary Capture Image Storage' : 'SC'}
    
        try:
            mode_prefix = mode_prefixes[dataset.SOPClassUID.__str__()]
        except:
            pass

        #TODO: need to figure out where this will be stored?
        filename = '{0!s}.{1!s}'.format(mode_prefix, dataset.SOPInstanceUID)
        bot.info('Storing DICOM file: {0!s}'.format(filename))

        if os.path.exists(filename):
            bot.warning('DICOM file already exists, overwriting')

        meta = Dataset()
        meta.MediaStorageSOPClassUID = dataset.SOPClassUID
        meta.MediaStorageSOPInstanceUID = dataset.SOPInstanceUID
        meta.ImplementationClassUID = pynetdicom_uid_prefix

        ds = FileDataset(filename, {}, file_meta=meta, preamble=b"\0" * 128)
        ds.update(dataset)
        ds.is_little_endian = True
        ds.is_implicit_VR = True
        ds.save_as(filename)

        return 0x0000 # Success


class Move(BaseSCU):

    description='''The movescu application implements a Service Class User
                (SCU) for the Query/Retrieve (QR) Service Class and a SCP
                for the Storage Service Class. movescu
                supports retrieve functionality using the C-MOVE
                message. It sends query keys to an SCP and waits for a
                response. It will accept associations for the purpose of
                receiving images sent as a result of the C-MOVE request.
                The application can be used to test SCPs of the
                QR Service Classes. movescu can initiate the transfer of
                images to a third party or can retrieve images to itself
                (note: the use of the term 'move' is a misnomer, the
                C-MOVE operation performs an image copy only)'''

    cancel_status = cancel.matching_terminated
    warning = warning.suboperation
    success = success.suboperation
    pending = pending.suboperation
 
    def __init__(self,name=None):
        '''
        :param name: the title/name for the ae. 'MOVESCU' is used if not defined.
        :param model: the query information model
        '''
        if name is None:
            name = 'MOVESCU'

        ae = AE(ae_title=name,
                port=0,
                scu_sop_class=QueryRetrieveSOPClassList,
                scp_sop_class=StorageSOPClassList,
                transfer_syntax=[ExplicitVRLittleEndian])

        BaseSCP.__init__(self,ae=ae)
        self.status = self.pending
        self.cancel = False


    def move(self,model=None,to_address=None,to_port=None,to_name=None,
             patient_name=None):

        # Set the extended negotiation SCP/SCU role selection to allow us to receive
        #   C-STORE requests for the supported SOP classes
        # I don't totally understand this, leaving as is until test it out.
        ext_neg = []
        for context in self.ae.presentation_contexts_scu:
            tmp = SCP_SCU_RoleSelectionNegotiation()
            tmp.sop_class_uid = context.AbstractSyntax
            tmp.scu_role = False
            tmp.scp_role = True

            ext_neg.append(tmp)

        if model is None:
            model = 'P'

        self.check_information_model(model)

        if patient_name is None:
            patient_name = "*"

        # Make the association - updates self.assoc
        self.make_assoc(address=to_address,
                        peer_name=to_name,
                        port=to_port,
                        ext_neg=ext_neg)

        # Create a query dataset
        dataset = Dataset()
        dataset.PatientName = patient_name
        dataset.QueryRetrieveLevel = "PATIENT"

        # Send query
        if self.assoc.is_established:
            response = assoc.send_c_move(dataset, 
                                         self.to_name, 
                                         query_model=model)
    
            time.sleep(1)
            for (status, d) in response:
                pass

            self.assoc.release()


    def on_c_store(self,sop_class,dataset):
        '''Function replacing ApplicationEntity.on_store(). Called when a dataset is
        received following a C-STORE. Write the received dataset to file
        :param sop_class: pydicom.sop_class.StorageServiceClass
        :param dataset: pydicom.Dataset sent via the C-STORE
        :returns status: a valid return status, see StorageServiceClass for available    
        '''
        filename = 'CT.{0!s}'.format(dataset.SOPInstanceUID)
        bot.info('Storing DICOM file: {0!s}'.format(filename))
    
        if os.path.exists(filename):
            bot.warning('DICOM file already exists, overwriting')
    
        #logger.debug("pydicom::Dataset()")
        meta = Dataset()
        meta.MediaStorageSOPClassUID = dataset.SOPClassUID
        meta.MediaStorageSOPInstanceUID = '1.2.3'
        meta.ImplementationClassUID = '1.2.3.4'
    
        #logger.debug("pydicom::FileDataset()")
        ds = FileDataset(filename, {}, file_meta=meta, preamble=b"\0" * 128)
        ds.update(dataset)
        ds.is_little_endian = True
        ds.is_implicit_VR = True
        #logger.debug("pydicom::save_as()")
        ds.save_as(filename)
    
        return sop_class.Success
