# node-dcm

This will build a basic Docker image using [pynetdicom3](https://github.com/scaramallion/pynetdicom3) and [pydicom](https://github.com/darcymason/pydicom)

**under development**


## Testing

The below is testing and thinking that I am doing, it is not ready for use.


```
docker build -t vanessa/netdicom .
```

and then to shell into

```
docker run -it vanessa/netdicom /bin/bash
```

To test, I deployed two images, as above, and then started running the server in one:

```
docker run -it vanessa/netdicom /bin/bash
python

>>> from pynetdicom3 import AE, VerificationSOPClass

ae = AE(port=3031, scp_sop_class=[VerificationSOPClass])

# Start the SCP
ae.start()
```

Then (on my host) I used docker inspect to get the ip address of the other running image.

```
docker inspect vanessa/netdicom2
# look for IpAddress
```

and then I could send a signal to my first instance

```
from pynetdicom3 import AE

# The Verification SOP Class has a UID of 1.2.840.10008.1.1
ae = AE(scu_sop_class=['1.2.840.10008.1.1'])
addr = '172.17.0.2'
port = 3031

# Try and associate with the peer AE
# Returns the Association thread
print('Requesting Association with the peer')
assoc = ae.associate(addr, port)

if assoc.is_established: # returns True
    print('Association accepted by the peer')
    # Send a DIMSE C-ECHO request to the peer
    echo = assoc.send_c_echo()
    print(echo.status_type) # Success
    # Release the association
    assoc.release()
elif assoc.is_rejected:
    print('Association was rejected by the peer')
elif assoc.is_aborted:
    print('Received an A-ABORT from the peer during Association')
```

The above is basic testing, next I will try to implement various functions with storage, verification, and find using a more robust class of servers (still under development).



## Google Cloud
It will probably be the case that we want to eventually test on Google Cloud, and it is important to open the [dicom ports](https://en.wikipedia.org/wiki/DICOM#Port_numbers_over_IP) to allow this. Better instructions will be written, but for now here are the simple steps to open ports. 

To deploy on Google Cloud, the (manual) way is to create an ubuntu:16.04 instance, and then build the image as follows. In the case of needing to open/close ports, you will need to do this in the cloud console. For example, I needed to expose port 104 for an instance running CTP:

1. Go to cloud.google.com
2. Go to my Console
3. Choose you Project.
4. Choose "Networking"
5. Choose "Firewalls rules"
6. Choose the interface for you Instances.
7. In firewalls section, Go to Create New.
8. Create your rule, in this case "Protocols & Ports" would be "tcp:104"
9. Save


## Links

- [FHIR](https://www.hl7.org/fhir/documentation.html)
- [Dicom (Wikipedia)](https://en.wikipedia.org/wiki/DICOM)
