## Find Service Class
A find service class is a way to serve a provider to allow querying a dicom base, or a user to do the query. As a reminder, we start here after using the [get_datasets.sh](../../scripts/get_datasets.sh) to first download the dicom-cookies dataset to `/data` in the container, and then shelling into the container and running python interactively.

### Provider
First, let's again create the provider, and the example below is provided in [create_findscp.py](create_findscp.py).


```
from node_dcm.providers import Find

findP = Find(name="stanford-find", 
             dicom_home="/data",
             start=True)

DEBUG Found 260 dicom files in data
DEBUG Checking 260 dicom files for validation.
Found 260 valid dicom files
```

And given that we set start=True, the console will be hanging and the find provider serving on default port `11112`. Also by default, the Find Service Class Provider will (pre-find) dicom files, defined by files with extension `*.dcm` in all subdirectories, all levels, of `/data`. This list will not be updated unless you initialize (or change) the update_on_find variable of the class. Let's say that we didn't start (we didn't set start=True), then we could change the findP object directly to **not** update the file list when a client asked to find:

```
findP.update_on_find
False

findP.update_on_find = True

```

or we could define this variable when we instantiate the Find instance:

```
findP = Find(name="stanford-find", dicom_home="/data", update_on_find=True)
```

You probably want to implement a more efficient way to have an updated list of files, or better yet, have a more robust database for the end storage, but this will work for this learning example.  Now, since we set start=True, our AE will be waiting (listening!) for a user to ask it to find something. Let's make that user now.


### User
The Find Service Class User (SCU) is the one to generate a query dataest, and send it to the Find Service Class Provider (SCP) to search through his datasets (the ones we made in `/data`) to see if there is a match! To help guide our queries, I've generated a "cookie manifest" that has all of the cookies provided in the cookie dataset, so we can cheat and know what to look for. You can find [the manifest here](https://github.com/pydicom/dicom-cookies/blob/master/scripts/cookie_manifest.json).

If you aren't working in two terminals already, you want to first shell into your running image in a second terminal:

```
NAME=$(docker ps -aqf "name=nodedcm_node_1")
docker exec -it $NAME bash
```

And start Python to create a Find Service Class User. This example is provided in [create_findscu.py](create_findscu.py). Remember, we already have our provider running in another terminal to receive this:

```
from node_dcm.users import Find

findU = Find(name="stanford-find")
patient_name = "summer fog"
findU.find(to_port=11112,
           to_address='localhost',
           patient_name=patient_name)
```

** still figuring this out  **
I am able to receive a status and type "None" to indicate no results (this is from the Find User):

```
DEBUG Peer[ANY-SCP] localhost:11112
DEBUG Found established association, releasing.
(<pynetdicom3.sop_class.Status object at 0x7f88dd451438>, None)
```

And I need to see if this is a bug, or the message/error returned given not finding a result. I think likely there is a problem with sending over the Dataset, and then querying - I need to read more about exactly how this is actually done :).

```
E: pydicom.write_dataset() failed:
E: 'NoneType' object is not iterable
E: Failed to decode the received Identifier dataset
```
