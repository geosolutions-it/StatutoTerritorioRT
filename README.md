# Geoportale Statuto del Territorio


## Table of Contents

- Python versions
- Install
- Environment setup
- Project setup
- Wagtail setup


## Python/Django versions

- Python 3.6+
- Django 2.0.8+

## Install

- Clone the repository:\
`git clone https://github.com/geosolutions-it/StatutoTerritorioRT.git`

- Create a virtual environment and activate it

- Install requirements with pip:\
`cd StatutoTerritorioRT/requirements`\
`pip install -r requirements.txt`


## Environment setup

- Go to the deployment folder:\
`cd StatutoTerritorioRT/deployment`

- Create the DB if not exists
  ```
  sudo -u postgres createuser -P <username>

  sudo -u postgres createdb -O <username> <dbname>
  sudo -u postgres psql -d <dbname> -c 'CREATE EXTENSION postgis;'
  sudo -u postgres psql -d <dbname> -c 'GRANT ALL ON geometry_columns TO PUBLIC;';
  sudo -u postgres psql -d <dbname> -c 'GRANT ALL ON spatial_ref_sys TO PUBLIC;';
  sudo -u postgres psql -d <dbname> -c 'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO <username>;'
  ```

- Set your environment variables values in a `your_local.env` file (`dev.env` is an example) then run this script:\
`source setenv.sh your_local.env`

Update the `DJANGO_DATABASE_URL` accordingly or leave null for default sqlite DB

## Project setup

- Go to the project management folder:\
`cd StatutoTerritorioRT/strt`

- Create the DB structure:\
`python manage.py migrate`

- Create a super user:\
`python manage.py createsuperuser`

- Load default data:
  ```
  python manage.py loaddata fixtrues/strt_core.json
  python manage.py loaddata fixtrues/strt_users.json
  python manage.py loaddata fixtrues/strt_homepage.json
  ```

- Run the Django development server:\
`python manage.py runserver`

- Visit http://127.0.0.1:8000/ with your web browser


## Wagtail setup

### Prepare the client and theme:

- Go to the Theme folder:\
`cd StatutoTerritorioRT/strt/theme`

- Build the CSS:\
`npm install`

- Go to the Client folder:\
`cd StatutoTerritorioRT/strt/serapide_client`

- Build the Frontend:
  ```
  npm install
  npm run build-with-theme
  ```

### Setup an HomePage for your project:

- Log in to the Wagtail admin panel (as superuser):
http://127.0.0.1:8000/admin/

- Delete the existing Pages and Sites

- Add a new Page to the Root, insert your contents and publish the Page

- Add a new Site with this configuration:
  - `Hostname: localhost`
  - `Port: 8000`
  - `Site name: Statuto del Territorio RT`
  - `Root page:` the new Page created
  - `Is default site: True`

- Save the new Site

- Visit http://127.0.0.1:8000/ with your web browser to check the HomePage is visible
