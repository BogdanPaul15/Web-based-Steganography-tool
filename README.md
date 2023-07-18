# Web-based steganography tool

## Frontend

For the frontend I have used BOOTSTRAP. There are 3 principal pages:

- <b>homepage</b> - where there is a short description of the application and some links to the main operations;
- <b>encode</b> - where the encoding of the message in the image is carried out, it contains a text and a select
- <b>decode</b> - where the image is decoded and the message is showed

Also, on both decode and encode pages there are last image encoded and last message decoded.
All forms also have a little data parsing to avoid errors. I also made a small 404 redirect in case someone tries to access "image/last/encoded" or "image/last/decoded" before there is anything there.

## Steganography

For the encoding process, I have converted the input message to binary, the input image to binary (it must be .PNG, otherwise it won't work) and encoded them according to the formula. I have added a stop string  ("&#36;&#35;&#38;") at the end, to know where to stop in the decoding process. Basically, the message + &#36;&#35;&#38; is encoded in the pixels of the image, and when the message is fully traversed, then the pixel traversal is exited. The image is saved at path:"public/images/encoded_image.png" so that it can also be displayed at the path "image/last/encoded", but also for the last encoded image.

For the decoding process, I have converted the image back to binary and went pixel by pixel and did the reverse of the encoding. I also checked the stop string ("&#36;&#35;&#38;"), so I know when to stop and not loop through the whole image for nothing. The received binary message is then converted to ASCII by evaluating chunks of 8 bits each. The final message is written to path:"public/message/message.txt" to be displayed in the last message decoded section and in the "image/last/decoded" path.

## Dockerfile

The docker image has the FLASK and PILLOW requirements. So, to create the docker image, you have to use this command:

```
    docker build -t iap-tema2 .
```

and to start it, use this command:

```
    docker run -p 8080:80 -it iap-tema2
```

It should be available [Here](http://localhost:8080/)
