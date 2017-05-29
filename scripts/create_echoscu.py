#!/bin/env python3

# An example of creating an Echo Service Provider

from node_dcm.users import Echo

echoU = Echo(name="stanford-echo",port=99)

# If the other echoP is running on port 11112, send an echo to it
echoU.send_echo(to_port=11112,to_address='localhost')

