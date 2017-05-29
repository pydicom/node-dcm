# node-dcm

This will provide recipes for basic Docker images using [pynetdicom3](https://github.com/scaramallion/pynetdicom3) and [pydicom](https://github.com/darcymason/pydicom) to implement different kinds of Service Class Providers and Service Class Users. I'm still learning a lot about Dicom, so this is a work in progress!

## Getting Started
First, you should build your image base. We will create an image, and download test dicom datasets into it.

```
git clone https://www.github.com/pydicom/node-dcm
cd node-dcm
docker build -t vanessa/nodedcm .
```

Next, let's start our set of images (a nginx web server and node dcm) with docker-compose.

```
docker-compose up -d
```

Then get the name programatically, and shell into it

```
NAME=$(docker ps -aqf "name=nodedcm_node_1")
docker exec -it $NAME bash
```

You will be sitting at the base, in `/code`, which is also mounted to the host. This means that you can make changes locally (on the host) and they will be represented in the container. For any changes to your applications, you will usually need to restart. Let's first download some sample dicoms to `/data`

```
./scripts/get_datasets.sh
ls /data
ls /data
cookie-1   cookie-19  cookie-28  cookie-37  cookie-46  cookie-55  cookie-64
cookie-10  cookie-2   cookie-29  cookie-38  cookie-47  cookie-56  cookie-65
cookie-11  cookie-20  cookie-3	 cookie-39  cookie-48  cookie-57  cookie-66
cookie-12  cookie-21  cookie-30  cookie-4   cookie-49  cookie-58  cookie-67
cookie-13  cookie-22  cookie-31  cookie-40  cookie-5   cookie-59  cookie-68
cookie-14  cookie-23  cookie-32  cookie-41  cookie-50  cookie-6   cookie-69
cookie-15  cookie-24  cookie-33  cookie-42  cookie-51  cookie-60  cookie-7
cookie-16  cookie-25  cookie-34  cookie-43  cookie-52  cookie-61  cookie-8
cookie-17  cookie-26  cookie-35  cookie-44  cookie-53  cookie-62  cookie-9
cookie-18  cookie-27  cookie-36  cookie-45  cookie-54  cookie-63
```

For examples of how to use and test, please see the [examples](examples) folder. So far, I've started the following examples:

 - [echo](examples/echo)


**under development**


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
