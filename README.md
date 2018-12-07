# Geoportale Statuto del Territorio


## Table of Contents

- Python versions
- Install
- Enviroment setup
- Project setup
- Wagtail setup


## Python versions

- Python 3


## Install

- Clone the repository:\
`git clone https://github.com/geosolutions-it/StatutoTerritorioRT.git`

- Create a virtual eniviroment and activate it

- Install requirements with pip:\
`cd StatutoTerritorioRT/requirements`\
`pip install -r requirements.txt`


## Enviroment setup

- Go to the deployment folder:\
`cd StatutoTerritorioRT/deployments`

- Set your enviroment variables values in a `your_local.env` file (`dev.env` is an example) then run this script:\
`source setenv.sh your_local.env`


## Project setup

- Go to the project management folder:\
`cd StatutoTerritorioRT/strt`

- Create the DB structure:\
`python manage.py migrate`

- Create a super user:\
`python manage.py createsuperuser`

- Run the Django development server:\
`python manage.py runserver`

- Visit http://127.0.0.1:8000/ with your web browser


## Wagtail setup

Setup an HomePage for your project:

- Log in to the Wagtail admin panel (as superuser):
http://127.0.0.1:8000/admin/

- Delete the existing pages and/or site

- Add a new page to the Root, insert your contents and promote the page

- Add a new site with this configuration:
  - `Hostname: localhost`
  - `Port: 8000`
  - `Site name: Statuto del Territorio RT`
  - `Root page:` the new page created
  - `Is default site: True`
  
- Save the new site

- Visit http://127.0.0.1:8000/ with your web browser to check the HomePage is visible

