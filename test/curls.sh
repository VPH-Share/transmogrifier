#!/bin/sh

curl -X OPTIONS http://127.0.0.1:8080/v1


curl -X OPTIONS http://127.0.0.1:8080/v1/identify
curl -X GET http://127.0.0.1:8080/v1/identify?src=http://upload.wikimedia.org/wikipedia/en/2/24/Lenna.png
curl -X POST -F file=@Lenna.png http://127.0.0.1:8080/v1/identify?dest=lob://Lenna.png
curl -X GET http://127.0.0.1:8080/v1/identify?src=lob://Lenna.png
curl -X GET http://127.0.0.1:8080/v1/identify.xml?src=lob://Lenna.png


curl -X OPTIONS http://127.0.0.1:8080/v1/convert
curl -X GET http://127.0.0.1:8080/v1/convert?src=http://upload.wikimedia.org/wikipedia/en/2/24/Lenna.png&flip=V&format=jpg&resize=100x100&rotate=45
curl -X POST -F file=@Lenna.png -F flip=V -F format=jpg -F resize=100x100 -F rotate=45 http://127.0.0.1:8080/v1/convert
curl -X GET http://127.0.0.1:8080/v1/convert?src=lob://Lenna.png&flip=V&format=jpg&resize=100x100&rotate=45
