# FACS Docker : How to use

In this document, we will explain how to download, setup, and run [FACS](https://github.com/djgroen/facs) within a Docker image

## Dependencies
#### What you need:
- [Docker](https://www.docker.com), which you can download and install from [here](https://docs.docker.com/install/).
- [GitHub](https://github.com/)

## Installation


#### Build Docker image locally:
1. Clone FACS image in your local PC
	`git clone https://github.com/djgroen/facs.git`
2. Go to `facs` folder and run
	 `docker build -t facs .`
3. Check if the docker image is available in your system
    ```sh
    $ docker images
    REPOSITORY   TAG        IMAGE ID       CREATED          SIZE
    facs         latest     c823f89d2355   15 minutes ago   793MB
    python       3.9-slim   0d9b718e2063   2 days ago       124MB    
    ```
#### Pull from  [Docker Hub](https://hub.docker.com/):
Currently, FACS is not synced with Docker Hub. This option will be added

## FACS Docker Usage
To run a FACS simulation for a scenario location, you can use the available locations from https://github.com/djgroen/FabCovid19/tree/master/config_files

First, select one of them, for example, `brent`, then go to the folder, and run
```sh
docker run -it -v $PWD:/FACS_app/config_files facs --generic_outfile --location=brent  --transition_scenario=extend-lockdown  --transition_mode=1  --ci_multiplier=0.475  --output_dir=.  --data_dir=covid_data  --starting_infections=500  --start_date=1/3/2020  --simulation_period=-1
```
