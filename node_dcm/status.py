'''

status.py is a simple collection of likely status messages for a 
          SCP (service class provider)

The MIT License (MIT)

Copyright (c) 2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the 'Software'), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from .logman import bot
from pynetdicom3.sop_class import Status

##############################################################################
# Success
##############################################################################

class success:
    empty = Status('Success', 
                   '', 
                   range(0x0000, 0x0000 + 1))

    suboperation = Status('Success',
                          'Sub-operations Complete - No Failure or Warnings',
                           range(0x0000, 0x0000 + 1))


    matching = Status('Success',
                       'Matching is complete - No final Identifier is supplied',
                       range(0x0000, 0x0000 + 1))


##############################################################################
# Test
##############################################################################

class testing:

    test = Status('Test', 'A test status', range(0x0101, 0x0101 + 1))


##############################################################################
# Warning
##############################################################################


class warning:
    coercion_of_elements = Status('Warning', 
                                  'Coercion of Data Elements',
                                   range(0xB000, 0xB000 + 1))

    ds_doesnt_match_sop = Status('Warning',
                                 'Data Set does not match SOP Class',
                                  range(0xB007, 0xB007 + 1))

    element_discard = Status('Warning', 
                             'Element Discarded',
                              range(0xB006, 0xB006 + 1))

    suboperation = Status('Warning',
                          'Sub-operations Complete - One or more Failures or '
                          'Warnings',
                               range(0xB000, 0xB000 + 1))

##############################################################################
# Failure
##############################################################################

class failure:

    ds_doesnt_match_sop = Status('Failure',
                                 'Error: Data Set does not match SOP Class',
                                  range(0xA900, 0xA9FF + 1))

    cant_understand = Status('Failure', 
                             'Error: Cannot understand',
                              range(0xC000, 0xCFFF + 1))

    out_of_resources = Status('Failure','Refused: Out of resources',
                               range(0xA700, 0xA7FF + 1))


    out_of_resources_match = Status('Failure',
                                    'Refused: Out of resources - Unable '
                                    'to calculate number of matches',
                                     range(0xA701, 0xA701 + 1))

    out_of_resources_unable = Status('Failure',
                                     'Refused: Out of resources - Unable '
                                     'to perform sub-operations',
                                      range(0xA702, 0xA702 + 1))

    move_destination_unknown = Status('Failure',
                                      'Refused: Move destination unknown',
                                       range(0xA801, 0xA801 + 1))

    identifier_doesnt_match_sop = Status('Failure',
                                         'Identifier does not match SOP '
                                         'Class',
                                          range(0xA900, 0xA900 + 1))

    unable_to_process = Status('Failure',
                               'Unable to process',
                                range(0xC000, 0xCFFF + 1))



##############################################################################
# Pending
##############################################################################

class pending:

    matches = Status('Pending',
                     'Matches are continuing - Current Match is supplied '
                     'and any Optional Keys were supported in the same manner '
                     'as "Required Keys"',
                      range(0xFF00, 0xFF00 + 1))

    matches_warning = Status('Pending',
                             'Matches are continuing - Warning that one or more '
                             'Optional Keys were not supported for existence '
                             'and/or matching for this identifier',
                             range(0xFF01, 0xFF01 + 1))

    suboperation = Status('Pending',
                          'Sub-operations are continuing',
                           range(0xFF00, 0xFF00 + 1))


##############################################################################
# Cancel
##############################################################################


class cancel:
    suboperation =  Status('Cancel',
                           'Sub-operations terminated due to Cancel indication',
                            range(0xFE00, 0xFE00 + 1))


    matching_terminated = Status('Cancel',
                                 'Matching terminated due to '
                                 'Cancel request',
                                  range(0xFE00, 0xFE00 + 1))

