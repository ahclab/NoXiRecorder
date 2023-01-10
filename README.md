# NoXiRecorder

## Operating environment
* **Macbook Air (M1, 2020)**
  - macOS Monterey 12.5.1
  - Apple M1
  - RAM 8GB
* **ALIENWARE M15**
  - Windows 11 Home
  - Intel Core i7-11800H
  - RAM 16GB

## Installation
### Install ffmpeg
* **Windows**
  1. Download ffmpeg (https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z)
  2. Unzip the downloaded file
  3. Place it in any folder and pass the path to "**ffmpeg-5.1.2-full_build/bin**".
* **Mac OS**
  1. Install via Homebrew: `brew install ffmpeg`

### Install NoXiRecorder
* Clone the github repository: `git clone https://github.com/ahclab/NoXiRecorder.git`
  - movement: `cd NoXiRecorder`
* Create conda env: `conda create -n recorder python=3.8`
  - source env: `conda activate recorder`
* Dependencies: 
  * Install requirements: `pip install -r requirements.txt`
  * Install repo: `pip install -e .`

## Setup
### Edit the settings file (NoXiRecorder/setting/...)
The main variables that need editing are listed below
  - **user**: Select the role of the computer to be used from "**expert**", "**novice**", "**observer**".
  - **device**: Enter the name of the equipment to be used for the recording
This is only valid for macOS and will not work on Windows due to system reasons.
  - **id**: Enter the device ID used for recording.
This ID will be used if the device name is not found or if Windows is used.
  - **ip**: Please enter ip address for server.

## Run
### Capture
```bash
python NoXiRecorder/capture.py
```

### Recorder
#### Recording on a single PC
```bash
python NoXiRecorder/AVrecorder.py
```
If you get "AttributeError: module 'ffmpeg' has no attribute 'input'", please execute the following command.  
`pip uninstall python-ffmpge ffmpeg-python`  
`pip install ffmpeg-python`

If you get an "Invalid buffer size error", please review the settings file.

#### Synchronized recording of two PCs
##### Server PC (expert/novice)
```bash
python NoXiRecorder/server.py
```

##### Client PC (observer)
```bash
python NoXiRecorder/client.py
```

###### Command
  - **time**: Check the current time
  - **ready**: Confirmation of communication status
  - **set option**: Setting Options  
    ex.) `--num 01`
  - **cat option**: Display of currently set options
  - **record**: Launch AVrecordeR
  - **start**: Start of recording
  - **end**: End of recording
  - **exit**: Disconnection of communication and program termination

### Monitor
#### 1. Server PC (expert)
```bash
python NoXiRecorder/monitorServerAudio.py
python NoXiRecorder/monitorServerVideo.py
```

#### 2. Server PC (novice)
```bash
python NoXiRecorder/monitorServerAudio.py
python NoXiRecorder/monitorServerVideo.py
```

#### 2. Client PC (observer)
```bash
python NoXiRecorder/monitorClientAudio.py --monitor_user expert
python NoXiRecorder/monitorClientVideo.py --monitor_user expert
python NoXiRecorder/monitorClientAudio.py --monitor_user novice
python NoXiRecorder/monitorClientVideo.py --monitor_user novice
```