# indeed_web_scapper
Craws through pages based on search criteria and provides the matching jobs

# How to build the virtual env for local testing
python3 -m venv venv
cd venv
source bin/activate
cd.. # Go to the root folder path
pip3 install -r requirements.txt # Recrursively install all the python lib dependencies
python3 main.py

# Build a docker image
docker build -t indeed_scapper:1.0.0 .

# Run a docker image
docker run indeed_scapper:1.0.1

# Go to inside the root access:
docker run -it indeed_scapper /bin/bash

# Run the script within the container:
python3 main.py

# Build and run your app with Compose
From your project directory, start up your application by running
docker compose up
