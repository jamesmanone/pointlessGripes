# Pointless Gripes
__
### Introduction
Pointless Gripes is a multiuser blog website based on the google app engine platform. It uses a backend built in python to handle requests from users. Pointless Gripes supports upvotes and comments, and uses jQuery AJAX requests to handle the display and posting of comments, as well as updating and incrementing upvote counts.
___
### Requirements
To run this application you must have python 2.7 or later installed. If you do not, please download and install it from [here](https://www.python.org/downloads/). This app was designed for the Google app engine platform. The only way to run it is to use google app engine SDK. If you do not have Google app engine SDK installed you can get it [here](https://cloud.google.com/appengine/downloads)
___
### Running Pointless Gripes
The best way to experience this app is to go to the website. It is located at [pointlessGripes.com](http://www.pointlessgripes.com). If you want to run this locally, you can. Follow these steps.
1. Clone this repo to your local disk
2. From the command line navigate to the directory you cloned it
3. Enter `dev_server.py app.yaml`
4. Open a browser and to to `localhost:8080`
This will run a fully featured version on your local machine, but entries will only be logged to the local database, and only local entries will be shown.
