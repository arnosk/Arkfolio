Arkfolio Development
=======

Datatypes
-----
- data types for the database stuff
- db schema types for different types of sites (exchange/txns sites/price info) and transaction types (sell/buy/in/out/etc)
- Money, not using floating point amounts of an asset, but integer with decimal places
- Timestamp or TimestampMS are just an integers


Databse
-----
- using raw sqlite3
- version of db is checked
- first start, the database is created
- after that the db schema types are written to the sitetype and transacttype table


Errors
------
- Definitions of exceptions
- These erros must be shown on ui with messageboard


Function (Helper functions)
-------
- saving files
- converting dates and times


Models (Sitemodel)
-----
This are the programs for the site types to get all transactions and prices
Now an automatic class declarations is used in sitemodelfinder.py together with __init__.py in the underlying folders. 
Don't know if this is the best way to do it. Can also import by hand all classes.

- The sitemodel is automatically added to the database
- When necessary user has to provide secret / api key
- Can be disabled by user
- Getting txns first time reads all txns untill now, this might take several request depending on limit of site
- Getting txns next time, will take in consideration the existing txns in database by using last_time


Request
------
Using the request library to get the data in json
- Sleeping/backoff time must be on ui


Server
-----
The backbone for starting threads with sitemodels to get the txns and prices
- Initialize all available sitemodels classes in na dictionairy with key is sitemodel_id and value is the SiteModel class
- Read database for wallets which are connected to a sitemodel. This is constructing a dictionairy with key is sitemodel_id and value is al ist of wallets
- Start the threads every hour / day


UI Client
-----
Will probably consist of model-controller-view principle or using fast-api or ???
- For now controller makes a profile and a bitcoin wallet