# QueryJane

Web application created by "Roadhouse Studio"

We are using Docker to isolate the development environment to have a single
and stable operating system and libraries.

## Installation

With docker and docker-compose installed run:
    $ docker-compose build

## Running

If the requirements file has changed you must rebuild the base image, you can do
it running:

    $ docker-compose up

It will rebuild you image, since Docker has a cache mechanism it will take
less than building the image for the first time.


## Database

Since Docker does not come with database contents you migth need to populate
your database first, you can do that by restoring a database from a file:

To generate the file backup on deployment server, run:
    
    pg_dump jd_db -U roadhouse_user -h localhost -F c > qj_backup.dump

To restore the database backup locally:

    $ docker exec queryjaneapp_db_1 psql --dbname=postgres --username=postgres --command="DROP SCHEMA public CASCADE;CREATE SCHEMA public;"

    $ docker exec queryjaneapp_db_1 pg_restore /tmp/data/db.dump --dbname=postgres --username=postgres --no-owner

If a db.dump file is in the root directory of your project it will work and load
that file into the database used by Docker. You can do this anytime you need.

You can connect to the database shell using:

    $ docker exec -it queryjaneapp_db_1 psql --dbname=postgres --username=postgres
