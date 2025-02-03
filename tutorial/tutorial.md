# Introduction

This tutorial aims to give users a hands on explanation about how to use this repository in conjuction with DuckSoup in their own machine, in local mode.

# Install Docker

If you are using Windows or Mac, install docker desktop:
https://docs.docker.com/desktop/setup/install/mac-install/ 

Then create an account in docker. 
Then open the new Docker Desktop app in your computer.
Then open the terminal and check that docker installation worked:
‘docker --version’

If you are using linux install docker following the instructions [here](https://docs.docker.com/engine/install/ubuntu/).

It might be useful for users to familiarize themselves with docker at this point. Docker is a lightweight containerization platform that encapsulates applications and all their dependencies into a single, portable container. It allows for consistent environments across development, testing, and production by isolating applications from the underlying system. This approach simplifies deployment, enhances scalability, and improves resource efficiency in modern software development. We share ducksoup in docker containers. The explanation of how to use them is below. Check out [this](https://www.youtube.com/watch?v=_dfLOzuIg2o) video for an example of how we use Docker.

## Otree configuration

Start by downloading [https://code.visualstudio.com/](VScode). This will be the IDE we will be using for the development of our experiment. After installing Vscode, install the "WSL" as well as the "docker" extensions into vscode, clicking on the extension button on the left bar of vscode.


Now, open a new terminal window and go inside your ducksoup_test folder:
```
cd ducksoup_test
```

Once in the ducksoup_test folder, clone the experiment_templates repository, which has several experiment examples that we can use as a starting point:
```
git clone https://github.com/ducksouplab/experiment_templates.git
```

Move inside the repository with this command:
```
cd experiment_templates
```

The following command will create a new file called .env. This file will have the environment variables written below, which will configure the otree server (copy the whole block):
```
cat <<EOF > .env
OTREE_DUCKSOUP_URL=http://localhost:8101
OTREE_DUCKSOUP_FRONTEND_VERSION=latest
OTREE_DUCKSOUP_REQUEST_GPU=false
OTREE_DUCKSOUP_FRAMERATE=30
OTREE_DUCKSOUP_WIDTH=800
OTREE_DUCKSOUP_HEIGHT=600
OTREE_DUCKSOUP_FORMAT=H264
OTREE_REST_KEY=...
EOF
```

Make sure it worked:
```
cat .env
```

This files contains all the environement variables which control otree's behavior. In particular, it will tell otree in which port to communicate with DuckSoup (OTREE_DUCKSOUP_URL variable). Below, we will use port 8101 to initialise DuckSoup. Therefore, we are using in the .env file OTREE_DUCKSOUP_URL=http://localhost:8101 to ensure both applications can communicate.

Now, open the ```experiment_template``` folder inside vscode using the ```code .``` command. When prompted in Vs Code click "Reopen in container".

Now, to test the template experiments, in the the vscode command line— which should be inside vscode the container at this point—, type:
```make dev```

This should start a new server running otree, which should communicate with DuckSoup. You can select here a new experiment as you would do for any otree experiment. Modify the otree code in the experiment_template to create your own experiment. Refer to the otree documentation to do this.

## Ducksoup configuration
First of all you will need to download and setup Ducksoup. To do that, start by following the following tutorial (Download and setup Ducksoup): https://github.com/ducksouplab/ducksoup/blob/main/tutorials/run_in_local.md

Once you have tested that Ducksoup works correctly, you should be able to execute it:
```
docker run --name ducksoup_1 -u $(id -u):$(id -g) -p 8101:8100 -e DUCKSOUP_TEST_LOGIN=admin -e DUCKSOUP_TEST_PASSWORD=admin -e DUCKSOUP_NVCODEC=false -e DUCKSOUP_NVCUDA=false -e GST_DEBUG=3 -e DUCKSOUP_ALLOWED_WS_ORIGINS=http://localhost:8180 -e DUCKSOUP_JITTER_BUFFER=250 -e DUCKSOUP_GENERATE_PLOTS=true -e DUCKSOUP_GENERATE_TWCC=true -v $(pwd)/plugins:/app/plugins:ro -v $(pwd)/data:/app/data -v $(pwd)/log:/app/log --rm ducksoup:latest
```

## Ensuring that DuckSoup and Otree communicate well.

if you copy pasted the code below, otree and DuckSoup should be already communicating well. But this part explains how it's done. Specifically, to make DuckSoup and otree communicate, we need to ensure that Ducksoup knows which webadress otree is using, as well as ensure that otree knows which port DuckSoup is running on.


First, to ensure that Ducksoup knows where otree is going running we add the parameter to```DUCKSOUP_ALLOWED_WS_ORIGINS=http://localhost:8180```to the Ducksoup execution command.  This parameter configures ducksoup so that it accepts requests from the otree server, which will be running in adress ```http://localhost:8180```. Therefore, we put ```DUCKSOUP_ALLOWED_WS_ORIGINS=http://localhost:8180```, so that ducksoup accepts requests from this website.

Second, we need to configure otree so that it know where DuckSoup is running. To do this we added the environment variable ```OTREE_DUCKSOUP_URL=http://localhost:8101``` to the .env file in the experiment_template folder. 

## Running an experiment

Now that you have configured both Otree and DuckSoup, you can try one of our experiment examples.

### Starting Ducksoup
Start by starting Ducksoup—if it's not started already.
```
docker run --name ducksoup_1 -u $(id -u arias):$(id -g arias) -p 8101:8100 -e DUCKSOUP_TEST_LOGIN=admin -e DUCKSOUP_TEST_PASSWORD=admin -e DUCKSOUP_NVCODEC=false -e DUCKSOUP_NVCUDA=false -e GST_DEBUG=3 -e DUCKSOUP_ALLOWED_WS_ORIGINS=http://localhost:8180 -e DUCKSOUP_JITTER_BUFFER=250 -e DUCKSOUP_GENERATE_PLOTS=true -e DUCKSOUP_GENERATE_TWCC=true -v $(pwd)/plugins:/app/plugins:ro -v $(pwd)/data:/app/data -v $(pwd)/log:/app/log --rm ducksoup:latest
```

Note that you can do this previous command from a new terminal, in whichever path, as long as you don't need our custom Mozza plugin, if you do, please refer to [this tutorial](https://github.com/ducksouplab/ducksoup/blob/main/tutorials/run_in_local.md#incorporate-mozza-to-perform-real-time-smile-manipulation)) to make sure you start ducksoup in the correct folder so that it can recognise mozza.


### Starting Otree
To start otree,  start by opening the experiment_template in vs Code:

To do this, go to the experiment_template repository:
```
cd experiment_templates
```

Then open that repository inside VScode:
```
code .
```

Click in the 'reopen in container' button. After it opened in a new container, in the container terminal, run:
```
make dev
```

This shoud start the otree client. Open the webpage : http://localhost:8180/demo. That is the page where the otree service running.
To understand how this page works, you can refer to the otree documentation.

You should see a list. Each item in this list is an experiment. Click click in the "DuckSoup now!" item to start the "DuckSoup now!" experiment (this one requires the mozza plugin).  After that, open all the participant links (from p1 to p8). Each of these links is a different participant. You should see yourself in each of these windows. You can test other experiments, but ensure that, if you run an experiment which has 'smile' in its name, you have the mozza plugin configured in DuckSoup, as it will be required for the experiment.

### Create a new experiment
You can now create your own experiment using otree, use one of the template experiments as a starting point. To do this, copy one of the folders in the experiment_template folder, such as meeting_visual_smile_N8, give it a new name 

Then in the settings.py file, add an entry such as::
```
		dict(
			id='your_new_experiment', 
			name='your_new_experiment',
			display_name='your_new_experiment',
			app_sequence=['your_new_experiment'],
			num_demo_participants=8,
			participant_label_file='_rooms/n8.txt',
			num_participants_allowed=[2, 4, 6, 8, 10, 12, 14],
			doc="The number of participants must be between 2 and 14"
		)
```

Also, in the init.py file, in the folder with the code of your experiment, make sure to change NAME_IN_URL and doc to:
```
NAME_IN_URL = 'your_new_experiment'
```

As well as
doc = """
your_new_experiment
"""

Now you can restart the otree server with ```make dev```, you should see your new experiment in the list of experiments. You can now modify this experiment to your required needs.


