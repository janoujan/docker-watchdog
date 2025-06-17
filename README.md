2 089 / 5 000
# Docker Watchdog

An elegant and powerful Python tool for system administrators to monitor and obtain detailed statistics on running Docker containers.

## Project Goal

This script queries the local Docker daemon and provides a complete list of running containers, including their name, image, execution status, as well as detailed metrics on RAM and CPU usage.

> **Note**: This project is for educational purposes and aims to help users better understand Docker container monitoring.

## Features

- Real-time monitoring of Docker containers.
- Export data in JSON and CSV formats.
- Interactive data visualization via a Streamlit dashboard.
- Generation of detailed reports in HTML and PDF.
- Visualization of network connections between containers.
- Direct interaction with containers (start, stop, delete).

## Installation

1. **Clone the project**
or download the ZIP file and unzip it to the desired location.

```bash
git clone https://github.com/your-user/docker-watchdog.git
```
2. **Change to the project directory.**

```bash
cd docker-watchdog
```

3. **Install the necessary dependencies**

```bash
pip install -r requirements.txt
```

## Usage

#### Launch the watchdog
```bash
python3 src/monitor.py
```
#### View the report in a browser
````bash
make open-cov
````
#### Export the reports
##### to JSON
````bash
python src/monitor.py --format json
````
##### to CSV
````bash
python src/monitor.py --format csv
````

#### Launch the Interactive Dashboard
````bash
streamlit run docker_dashboard.py
````
Then access the following URL in your browser:

http://127.0.0.1:8501

## Dockerization

### Prerequisites
- docker
- docker-compose

### Build and start the container
````bash
docker-compose up --build
````

### Stop and delete the container

To stop and delete the container, along with the associated image and volumes:
````bash
docker-compose down --rmi all --volumes
````
