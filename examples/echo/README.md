## Test with An Echo
The first thing I wanted to try was creating a provider to receive an echo, and then sending an echo as a user. In the shell above, in python I ran the follow, represented in [create_echoscp.py](scripts/create_echoscp.py). As a reminder, an scp is a service class provider (the one that listens for stuff).

```
from node_dcm.provider import Echo

echoP = Echo(name="stanford-echo",start=True)
```

This will leave the console hanging, because you've started the process. I then shelled into the image from another terminal to create the user. 

```
NAME=$(docker ps -aqf "name=nodedcm_node_1")
docker exec -it $NAME bash
```

Since we just want a quick command line client, we will use pynetdicom3's provided script:

```
cd /tmp && git clone https://github.com/scaramallion/pynetdicom3
cd pynetdicom3/pynetdicom3/apps
python echoscu.py localhost 11112 --debug
```

And then you will see the following output in the terminal:

```
D: echoscu.py v0.5.2 2017-02-04
D: 
I: Requesting Association
D: Request Parameters:
D: ====================== BEGIN A-ASSOCIATE-RQ =====================
D: Our Implementation Class UID:      1.2.826.0.1.3680043.9.3811.0.1.0
D: Our Implementation Version Name:   PYNETDICOM3_010
D: Application Context Name:    1.2.840.10008.3.1.1.1
D: Calling Application Name:    ECHOSCU         
D: Called Application Name:     ANY-SCP         
D: Our Max PDU Receive Size:    16384
D: Presentation Context:
D:   Context ID:        1 (Proposed)
D:     Abstract Syntax: =Verification SOP Class
D:     Proposed SCP/SCU Role: None/None
D:     Proposed Transfer Syntax:
D:       =Implicit VR Little Endian
D: Requested Extended Negotiation: None
D: Requested Common Extended Negotiation: None
D: Requested User Identity Negotiation: None
D: ======================= END A-ASSOCIATE-RQ ======================
D: Constructing Associate RQ PDU
D: PDU Type: Associate Accept, PDU Length: 189 + 6 bytes PDU header
D:     02  00  00  00  00  bd  00  01  00  00  73  74  61  6e  66  6f
D:     72  64  2d  65  63  68  6f  20  20  20  45  43  48  4f  53  43
D:     55  20  20  20  20  20  20  20  20  20  00  00  00  00  00  00
D:     00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00
D:     00  00  00  00  00  00  00  00  00  00  10  00  00  15  31  2e
D:     32  2e  38  34  30  2e  31  30  30  30  38  2e  33  2e  31  2e
D:     31  2e  31  21  00  00  19  01  00  00  00  40  00  00  11  31
D:     2e  32  2e  38  34  30  2e  31  30  30  30  38  2e  31  2e  32
D:     50  00  00  3f  51  00  00  04  00  00  40  00  52  00  00  20
D:     31  2e  32  2e  38  32  36  2e  30  2e  31  2e  33  36  38  30
D:     30  34  33  2e  39  2e  33  38  31  31  2e  30  2e  31  2e  30
D:     55  00  00  0f  50  59  4e  45  54  44  49  43  4f  4d  33  5f
D:     30  31  30
D: Parsing an A-ASSOCIATE PDU
D: Accept Parameters:
D: ====================== BEGIN A-ASSOCIATE-AC =====================
D: Their Implementation Class UID:    1.2.826.0.1.3680043.9.3811.0.1.0
D: Their Implementation Version Name: PYNETDICOM3_010
D: Application Context Name:    1.2.840.10008.3.1.1.1
D: Calling Application Name:    ECHOSCU         
D: Called Application Name:     stanford-echo   
D: Their Max PDU Receive Size:  16384
D: Presentation Contexts:
D:   Context ID:        1 (Accepted)
D:     Proposed SCP/SCU Role: Default
D:     Accepted SCP/SCU Role: Default
D:     Accepted Transfer Syntax: =Implicit VR Little Endian
D: Accepted Extended Negotiation: None
D: Accepted Common Extended Negotiation: None
D: Accepted Asynchronous Operations Window Negotiation: None
D: User Identity Negotiation Response:  None
D: ======================= END A-ASSOCIATE-AC ======================
I: Association Accepted
I: Sending Echo Request: MsgID 1
D: pydicom.read_dataset() TransferSyntax="Little Endian Implicit"
I: Received Echo Response (Status: Success)
I: Releasing Association
```

Next, we will try this using the node_dcm echo version (still under development)
