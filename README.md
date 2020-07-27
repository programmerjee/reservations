# Reservations

Reservations is a web application designed to allow apartment administration and residents to coordinate use of community amenities.  
Version one:
* Allows apartment admins to register, log in, create new time slots in 2 hour increments, check which units have reserved the use of the pool, and check which time slots are still available.
* Allows apartment residents to register, log in, commit to following recommended guidelines for social distancing, book apartment resources, and check upcoming reservations.

Future versions may include additional features, such as

* Profiles.  Currently only Admin staff can load Admin pages and only Residents can reservate time.  A more elegant solution would be to hide navigation to pages that the user should not be able to access

* Allow additional units to book amenity at the same time (up to X # of reservations)

Application is currently live on Heroku platform:
https://programmerjee-reservations.herokuapp.com/

## _Installation_

#### Mac OS:
* `brew install python3`
* `pip3 install flask`
* `pip3 install flask_session`
* `pip3 install cs50`
* `pip3 install request`

* sqlite3 is pre-installed

#### Windows:
* `pip install python3`
* `pip install flask`
* `pip install flask_session`
* `pip install cs50`
* `pip install request`

* Follow instructions to install _SQLite3_: https://www.tutorialspoint.com/sqlite/sqlite_installation.htm


## _Usage_

`git clone https://github.com/programmerjee/reservations.git`

`cd reservations`
`flask run`


## _Contributing_
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
