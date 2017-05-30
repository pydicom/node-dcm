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

from node_dcm.logman import bot
import os

from pydicom.uid import (
    ExplicitVRLittleEndian, 
    ExplicitVRBigEndian,
    ImplicitVRLittleEndian,
    UID
)

from node_dcm.status import testing
import threading
from node_dcm.validate import validate_port


class BaseServiceClass(threading.Thread):
    '''Base class for the SCP and SCU classes'''

    def __init__(self,ae=None):

        self.ae = ae

        if self.ae is None:
            bot.logger.error("The base service must be instantiated with an Application Entity (AE).")
            sys.exit(1)
 
        # Validate that the port specified works
        if self.ae.port is not None:
            validate_port(self.ae.port)

        self.ae.on_c_echo = self.on_c_echo
        self.ae.on_c_store = self.on_c_store
        self.ae.on_c_find = self.on_c_find
        self.ae.on_c_get = self.on_c_get
        self.ae.on_c_move = self.on_c_move
        threading.Thread.__init__(self)
        self.daemon = True
        self.delay = 0
        self.send_abort = False


    def update_transfer_syntax(self,prefer_uncompr=True,prefer_little=False,
                               prefer_big=False,implicit=False):

        transfer_syntax = [ImplicitVRLittleEndian,
                           ExplicitVRLittleEndian,
                           ExplicitVRBigEndian]

        if prefer_uncompr and ImplicitVRLittleEndian in transfer_syntax:
            transfer_syntax.remove(ImplicitVRLittleEndian)
            transfer_syntax.append(ImplicitVRLittleEndian)

        if implicit:
            transfer_syntax = [ImplicitVRLittleEndian]

        if prefer_little and ExplicitVRLittleEndian in transfer_syntax:
            transfer_syntax.remove(ExplicitVRLittleEndian)
            transfer_syntax.insert(0, ExplicitVRLittleEndian)

        if prefer_big and ExplicitVRBigEndian in transfer_syntax:
            transfer_syntax.remove(ExplicitVRBigEndian)
            transfer_syntax.insert(0, ExplicitVRBigEndian)

        self.transfer_syntax = transfer_syntax


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
        raise RuntimeError("%s is not implemented for this application entity." %name)



class BaseSCU(BaseServiceClass):
    '''Base class for the SCU classes'''


    information_models = ['W','P','S','O']

    def __init__(self,ae=None):

        self.assoc = None
        self.pdu_max = 16384

        self.to_name = "ANY-SCP"
        self.to_address = None
        self.to_port = 11112
 
        BaseServiceClass.__init__(self,ae)
 
    # Peers
    def get_peer(self):
        '''print peer will print a human friendly, readable address and name for a
        remote peer'''
        if self.to_address is not None:
            return "[%s] %s:%s" %(self.to_name,
                                  self.to_address,
                                  self.to_port)

        return "[%s] UNDEFINED" %(self.to_name)


    def update_peer(self,address=None,port=None,name=None):
        '''update_peer will update the address, port, and name of the peer AE'''

        if name is not None:
            self.to_name = name
        
        if port is not None:
            self.to_port = port

        if address is None and self.to_address is None:
            bot.error("You must supply a peer address to make an association.")
            sys.exit(1)
        self.to_address = address
        bot.debug("Peer[%s] %s:%s" %(self.to_name,
                                     self.to_address,
                                     self.to_port))


    # Associations

    def release_assoc(self):
        '''release assoc will release any associations that are open,
        in preparation for a new one.
        '''
        if self.assoc is not None:
            if self.assoc.is_established:
                bot.debug("Found established association, releasing.")
                self.assoc.release()


    def make_assoc(self,address=None,port=None,name=None,pdu_max=None,ext_neg=None):
        '''make an association with a peer at address, and port
        :param address: the address of the peer
        :param port: the port of the peer
        :param to_name: the name of the peer
        :param max_pdu: the max pdu (bytes)
        '''
        if pdu_max is not None:
            self.pdu_max = pdu_max

        self.update_peer(address=address,
                         port=port,
                         name=name)

        self.release_assoc()
        self.assoc = self.ae.associate(self.to_address,
                                       self.to_port,
                                       self.to_name,
                                       max_pdu=self.pdu_max,
                                       ext_neg=ext_neg)

    # Information Models
    def model_help(self):
        print('''Valid information models are:
              P: patient root information model
              W: modality worklist information model
              S: study root information model             
              O: patient/study only information model
              ''')

    def check_information_model(self,model):
        '''check information model validates the user selection of an information
        model, and exits if not valid.'''
        if model not in self.information_models:
            self.model_help()
            sys.exit(1)



class BaseSCP(BaseServiceClass):
    '''Base class for the SCP classes'''

    def __init__(self,ae=None):

        BaseServiceClass.__init__(self,ae)

