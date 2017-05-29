#!/bin/env python3

# An example of creating an Echo Service Provider

from node_dcm.providers import Echo

echoP = Echo(name="stanford-echo",start=True)

