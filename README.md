# AI Engine - Video Surveillance - Face Clustering Service

# AI Engine - Video Surveillance - Face Encode Service

## Video AI Sample model service

#### For more info: http://flask.pocoo.org/docs/1.0/installation/

###### Description
    This service receives sqs message from Face Recognition Service .When a message is received the service encodes the face and updates the encodings to a pickle file in S3 bucket. 
###### Prerequisites

- Python 3
- Pip 19.1.1
- Git
- MongoDB
- Postman (to test APIs)

###### General commands:

- `pip install virtualenv` - Installs virtualenv so that our dependencies are kept locally
- `mkdir sample-service`
- `cd sample-service`
- `python3 -m venv venv` - Create virtualenv in the folder
- `py -3 -m venv venv` - Create virtualenv in the folder (Windows)
- `. venv/bin/activate` - Activate virtualenv in Mac/Linux
- `\env\Scripts\activate.bat` - Activate virtualenv (Windows)
- `deactivate` - To deactivate virtualenv
- `pip install Flask` - Install Flask
- To format the code, run `black flaskr`
- To test the API endpoints, open `Postman` and `Import` the files in the `docs` folder

###### Pip Cheat-sheet

- `pip freeze` - Displays a list of currently installed dependencies, we can copy this to the `requirements.txt`
- `pip install -r requirements.txt` - Installs all the dependencies in the `requirements.txt`
- `pip install Watchdog && pip freeze > requirements.txt` - To install a new dependency
- `pip install -e .` - Install project in the virtual environment
- `pip list` - View all dependencies

###### Mac/Linux: (development server)

- `export SETTINGS=../config.cfg`
- `export S3_SETTINGS=../s3_config.cfg`
- `export SQS_SETTINGS=../sqs_config.cfg`
- `export FLASK_ENV=development`
- `export FLASK_APP=flaskr/__init__.py`
- `flask run`
- OR `sh run-dev.sh` - Custom boot script for Mac

###### Windows: (development server)

###### Command Prompt:

- `set SETTINGS=../config.cfg`
- `set S3_SETTINGS=../s3_config.cfg`
- `set SQS_SETTINGS=../sqs_config.cfg`
- `set FLASK_ENV=development`
- `set FLASK_APP=flaskr/__init__.py`
- `flask run`

###### PowerShell

- `$env:SETTINGS = "../config.cfg"`
- `$env:FLASK_ENV = "development"`
- `$env:FLASK_APP = "flaskr/__init__.py"`
- `flask run`

###### How to start the application

- Install Python3 & Pip
- Install virtualenv
- Git clone this repo & cd into the project folder
- Create a virtualenv and activate it
- Install all the dependencies
- Run the application

###### How to setup on Ubuntu on EC2

- sudo apt-get update
- sudo apt install python3
- sudo apt-get -y install python3-pip
- sudo apt-get install python3-venv
- sudo apt-get install libxext6 libsm6 libxrender1 libfontconfig1
- pip3 install --upgrade setuptools
- pip3 install --upgrade pip (try once)
- git clone https://samjones310@bitbucket.org/mtxadmins/ai-engine-video-surveillance-face-clustering-service.git
- cd ~/ai-engine-video-surveillance-face_clustering_service
- python3 -m venv venv
- . venv/bin/activate
- python -m pip install https://files.pythonhosted.org/packages/0e/ce/f8a3cff33ac03a8219768f0694c5d703c8e037e6aba2e865f9bae22ed63c/dlib-19.8.1-cp36-cp36m-win_amd64.whl#sha256=794994fa2c54e7776659fddb148363a5556468a6d5d46be8dad311722d54bfcf
- pip install -r requirements.txt
- pip install --upgrade pip (skip once)
- pip install opencv-python (skip once)
- pip install waitress (skip once)
- sudo nano /etc/systemd/system/videoai.service (update to copy)
- sudo systemctl start videoai - Starts the Video AI app as a service


###### Prod Service cheat sheet
- sudo systemctl status videoai.service
- sudo systemctl stop videoai.service
- journalctl -f -u videoai.service


###### Directory Structure

```
/<project-directory>

├── flaskr/
│   ├── __init__.py
│   ├── db.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   │   ├── login.html
│   └── static/
│       └── style.css_
├── tests/
│   ├── conftest.py
│   ├── data.sql
│   ├── test_db.py
│   ├── test_auth.py
├── venv/
├── setup.py
├── MANIFEST.in
├── run.*.sh
└── README.md
```
