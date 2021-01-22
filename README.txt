This is intended to provide an easy command line interface for several VDMS APIs

Currently there is a command line interface for the following:

- LinearPlaylist

# Using these scripts

1 - Add your CMS user id and private key to the api_auth.py
2 - Build and run the container
    docker build -t vdmsapigateway .
    docker run --rm -it vdmsapigateway
