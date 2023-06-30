Experimental Flask App

Important:
Connection settings are different for connecting to your local postgre database and to your containerized database!

Local:
        host="localhost",
        database="coffee_db",
        user="coffee_db_technical_user",
        password="coffeedb"

Container:
        host="coffee_db_container",
        port = 5432,
        database="coffee_db",
        user="coffee_db_technical_user",
        password="coffeedb"