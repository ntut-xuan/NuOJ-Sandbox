# NuOJ - Sandbox

## Introduction

The sandbox system based on [Isolate by IOI](https://github.com/ioi/isolate) for [Nu Online Judge](https://github.com/ntut-xuan/NuOJ).

We provide the routes for judging the code, it also handling various exceptions caused by submission code, solution and checker. 

Moreover, we wrote a utility to operate the Isolate that provide create file, run binary, compile code, execute the code, and judge the code. (See `backend/utils/isolate/util.py`)


## Supported platform

The sandbox system needs the version 1 of the control group. We provide a dockerfile to deploy the application in Docker, and make the application can work in most of the platform.

If your platfrom using the version 2 of the control group, you need to downgrade the control group to the version 1. 

The downgrade of the control group only work on Linux platform.

## Installation

### Using docker compose to deploy the application

First, you need the Docker to deploy the application. You should install the docker in [Docker official page](https://docker.com)

Check the docker is working, and use docker-compose to deploy the application.

```
docker compose up --build --no-deps --force-recreate
```

And it should be deploy the application by various steps.

When the deploy is successful, it should creating the application and running the tests to test the application working correctly.

The applicaiton will listen in 4439 port.


### Failed at environment doctor

If the steps failed in check the control group, it means the version of the control group working in this machine is version 2.

We provide a `env_setting.py` python script in `/backend` folder to downgrade the control group to version 1.

The script only work in Linux platform since the control group of WSL is version 1.

```
cd backend && python3 env_setting.py
```

