# Geoportale Statuto del Territorio


## Table of Contents

- Python versions
- Install
- Environment setup
- Project setup


## Python/Django versions

- Python 3.6+
- Django 2.0.8+

## Install
- Install system wide packages:\
  `sudo apt install python3-dev`\
  `sudo apt install postgresql-server-dev-10`\
  `sudo apt install python3-rtree`

- Create a suitable virtualenv, e.g.:\
  `mkvirtualenv --python=/usr/bin/python3 strt`

- Clone the repository: \
 `git clone https://github.com/geosolutions-it/StatutoTerritorioRT.git`

- Activate the virtual env:\
  `. strt/bin/activate`

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
  `cd StatutoTerritorioRT/strt`
  ```
  ./load_dump.sh
  ```

- Run the Django development server:\
`python manage.py runserver`

- Visit http://localhost:8000/admin/strt_users/utente/

- Set the passwords for the predefined users
 .. note:: The default password is `42`

- Visit http://localhost:8000/ with your web browser

- Login with one of the roles defined above


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
