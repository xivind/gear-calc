# Instructions for Antigravity to gear calculator web application
This file contains instructions for Antigravity to guide the building of the gear calculator web application.

# Purpose of the gear calculator web application
The purpose of the gear calculator web application is to help users to calculate the gear ratio of a bicycle. The program will let users select what chainring they have in front (can contain up to 3 chainrings) and what cog or cassette they have in back. Based on the selected chainring and cog the program will calculate what the gear ratios are and show them in a nice looking color coded table. The user will be given the option to enter a name for the combination of chainring and cog or cassette, along with comments. 

When accessing the application, the user should first be shown a landing page. This page should use tiles / cards and show all the existing chainring cog or cassette combinations created by the user. Upon clicking on any tile, the user will be directed to the relevant gear_ratio.html page (see above). From the landing page it should also be possible to create a new gear ratio configuration.

The user should also be able to register different components such as chainrings, cogs and cassettes. These components should be registered in a database and be available for selection when creating a new gear ratio configuration. For each component the user should be able to enter the name, speed / number of cogs, and number of teeth for each cog or cassette and comments. Dates are only necessary for configurations, not components.

# Tech stack
- The web application should be responsive design, so it also works on mobile phones
- FastAPI should be used for the backend
- Bootstrap should be used for the frontend
- Vanilla js should be used whenever js is needed. All js should be placed in the same js file, not placed inline in different html pages
- TomSelect should be used for advanced input boxes, and if thats not needed use standard bootstrap and html input boxes
- Date and time picker should use Tempus Domino js library
- Squlite should be used as the database
- PeeWee ORM should be used to interact with the sqlite database

# Architectural constraints
## General constraints
- main.py contains the router and should contain no business logic
- business_logic.py contains all business logic, calculations etc. Whenever CRUD operations are needed in the database, methods should always call database_manager.py and use the methods defined there. CRUD operations shall never be called directly from the business_logic module
- database_manager.py contains all methods necessary to do CRUD operations in the database
- database_model.py contains the model for the sqlite database
- logger.py contains the logging configuration. All logging, both from fastapi and python, should be done in a uniform manner and logged to the docker container. See the Dockerfile for inspiration
- seed_data.py is used to populate the database with configuration data for wheel materials on container creation
- utils.py contains helper methods, such as method to create UUIDs and other stuff that has the characteristics of being helper method
- It should be possible to run the application from the docker container and also directly from bash for development. Some Dockerfiles are provided for inspiration, along with a container creation script

## Database configuration
- The database configuration itself should be kept as simple as possible. Do not use backrefs or automatically generated IDs. Instead, always create uniue ids for records in the backend and submit that to the database. 