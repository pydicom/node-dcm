# node-dcm

This will provide recipes for basic Docker images using [pynetdicom3](https://github.com/scaramallion/pynetdicom3) and [pydicom](https://github.com/darcymason/pydicom) to implement different kinds of Service Class Providers and Service Class Users. I'm still learning a lot about Dicom, so this is a work in progress!

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
