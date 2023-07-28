import os
import time
import random
import subprocess
import json
from flask import Flask, request, render_template, make_response, redirect, jsonify
from confluent_kafka import Producer
import pymysql
from pymemcache.client import base as memcache
import pandas as pd
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
import signal

app = Flask(__name__, template_folder='templateFiles', static_folder='staticFiles')



# Define sensible defaults for options (you can change them if needed)
options = {
    "port": 5000,
    "kafka_broker": "my-cluster-kafka-bootstrap:9092",
    "kafka_topic_tracking": "tracking-data",
    "kafka_client_id": f"tracker-{random.randint(0, 99999)}",
    "memcached_hostname": "my-memcached-service",
    "memcached_port": 11211,
    "memcached_update_interval": 5000,
    "mariadb_host": "my-app-mariadb-service",
    "mariadb_port": 3306,
    "mariadb_schema": "popular",
    "mariadb_username": "root",
    "mariadb_password": "mysecretpw",
    "number_of_missions": 30,
}

# Override options with environment variables if available
for key, value in options.items():
    env_var = os.environ.get(key.upper())
    if env_var:
        options[key] = env_var

# -------------------------------------------------------
# Database Configuration
# -------------------------------------------------------

# Connect to MariaDB
db_connection = pymysql.connect(
    host=options["mariadb_host"],
    port=int(options["mariadb_port"]),
    user=options["mariadb_username"],
    password=options["mariadb_password"],
    db=options["mariadb_schema"]
)

# Execute a query and return the results
def execute_query(query, data=None):
    with db_connection.cursor() as cursor:
        cursor.execute(query, data)
        return cursor.fetchall()

# -------------------------------------------------------
# Memcache Configuration
# === Caches are not working as of right now ===
# === commented out code has been our approach to do it ===
# -------------------------------------------------------

# Connect to the memcached instance
memcached_client = memcache.Client(
    (options["memcached_hostname"], int(options["memcached_port"]))
)
# async def initialize_memcached():
#     await get_memcached_servers_from_dns()
#     update_interval = 5  # Update interval in seconds
#     while True:
#         await asyncio.sleep(update_interval)
#         await get_memcached_servers_from_dns()

# def run_initialize_memcached():
#     asyncio_thread = threading.Thread(target=asyncio.run, args=(initialize_memcached(),))
#     asyncio_thread.start()

# def get_from_cache(key):
#     if not memcached:
#         print(f"No memcached instance available, memcachedServers = {memcachedServers}")
#         return None
#     return memcached.get(key)

# async def get_missions():
#     key = 'coffee_types'
#     cachedata = await get_from_cache(key)

#     if cachedata:
#         print(f"Cache hit for key={key}, cachedata = {cachedata}")
#         return jsonify({"result": cachedata, "cached": True})
#     else:
#         print(f"Cache miss for key={key}, querying database")

#         if data:
#             result = [row["coffee_type"] for row in data]
#             print("Got result=", result, "storing in cache")
#             if memcached:
#                 memcached.set(key, result, cacheTimeSecs)
#             return jsonify({"result": result, "cached": False})
#         else:
#             return "No coffee_types data found", 404

# async def get_single_type(coffee_type):
#     query = "SELECT coffee_type FROM coffee_types"
#     key = coffee_type
#     cachedata = await get_from_cache(key)

#     if cachedata:
#         print(f"Cache hit for key={key}, cachedata = {cachedata}")
#         return jsonify({**cachedata, "cached": True})
#     else:
#         print(f"Cache miss for key={key}, querying database")

#         data = next((row for row in data if row["coffee_type"] == coffee_type), None)
#         if data:
#             result = {"coffee_type": data["coffee_type"], "size": data["size"]}
#             print(f"Got result={result}, storing in cache")
#             if memcached:
#                 memcached.set(key, result, cacheTimeSecs)
#             return jsonify({**result, "cached": False})
#         else:
#             return "No data found for this coffee_type", 404
# async def get_memcached_servers_from_dns():
#     global memcachedServers, memcached
#     try:
#         # Query all IP addresses for the memcachedHostname
#         query_result = dns.resolver.resolve(options.memcachedHostname)

#         # Create IP:Port mappings
#         servers = [str(el.address) + ":" + str(options.memcachedPort) for el in query_result]

#         # Check if the list of servers has changed
#         # and only create a new object if the server list has changed
#         if sorted(memcachedServers) != sorted(servers):
#             print("Updated memcached server list to ", servers)
#             memcachedServers = servers

#             # Disconnect an existing client
#             if memcached:
#                 await memcached.disconnect()

#             memcached = MemcachePlus(*memcachedServers)
#     except Exception as e:
#         print("Unable to get memcache servers (yet)", e)

cache_time_secs = 60 



# -------------------------------------------------------
# Kafka Configuration
# -------------------------------------------------------

# Kafka Producer
kafka_producer = Producer(
    {
        "bootstrap.servers": options["kafka_broker"],
        "client.id": options["kafka_client_id"],
    }
)

# Send tracking message to Kafka
def send_tracking_message(data):
    kafka_producer.produce(options["kafka_topic_tracking"], json.dumps(data))
    kafka_producer.flush()




# -------------------------------------------------------
# Flask main application
# -------------------------------------------------------

# === coffee routes === #
### frontend page routes ###
@app.route('/')
def index():
    return redirect('/start', code=301)

@app.route('/start')
def start():
    return render_template('start.html')

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/login_customer")
def loadLoginPage_customer():
    return render_template('Login_customer.html')

@app.route("/signup_customer")
def loadSignupPage_customer():
    return render_template('Signup_customer.html')

@app.route("/login_coffee_shop")
def loadLoginPage_coffee_shop():
    return render_template('Login_coffee_shop.html')

@app.route("/signup_coffee_shop")
def loadSignupPage_coffe_shop():
    return render_template('Signup_coffee_shop.html')

@app.route("/customer_landing")
def loadCustomerLanding():
    return render_template('customer_landing.html')

@app.route("/coffee_shop_landing")
def loadCoffeeShopLanding():
    return render_template('coffee_shop_landing.html')

@app.route("/ordering_page")
def loadOrderingPage():
    return render_template('ordering_page.html')

@app.route("/ordering_details")
def loadOrderingDetailsPage():
    return render_template('ordering_details.html')



### api's (backend handling) ###

# check login of customer
@app.route("/login_api_customer", methods=['POST'])
def handleLogin_customer():
    isvalid = False
    login_info = request.form

    sql_query = "SELECT * FROM customer_login WHERE customer_login.customer_id=%s AND customer_login.customer_password=%s"
    data = (login_info['username'], login_info['password'])

    result = execute_query(sql_query, data)

    if result:
        return login_info
    else:
        return "failed"



    
# registering a new customer
@app.route("/signup_api_customer", methods=['POST'])
def handleSignup_customer():
    isvalid = False
    signup_info = request.form

    try:
        sql_query = "INSERT INTO customers (customer_id, customer_firstname, customer_lastname) VALUES (%s, %s, %s); INSERT INTO customer_login (customer_id, customer_password) VALUES (%s, %s);"
        data = (signup_info['username'], signup_info['firstname'], signup_info['lastname'], signup_info['username'], signup_info['password'])
        execute_query(sql_query, data)

        isvalid = True

    except:
        isvalid = False

    if isvalid:
        return "successful"
    else:
        return "failed"

@app.route("/signup_api_coffee_shop", methods=['POST'])
def handleSignup_coffee_shop():
    isvalid = False
    signup_info = request.form

    try:
        sql_query = "INSERT INTO coffee_shops (shop_id, name, country, city, street, owner_firstname, owner_lastname) VALUES (%s, %s, %s, %s, %s, %s, %s); INSERT INTO shop_login (shop_id, shop_password) VALUES (%s, %s);"
        data = (signup_info['shop_id'], signup_info['name'], signup_info['country'], signup_info['city'], signup_info['street'], signup_info['owner_firstname'], signup_info['owner_lastname'], signup_info['shop_id'], signup_info['password'])
        execute_query(sql_query, data)

        isvalid = True

    except:
        isvalid = False

    if isvalid:
        return "successful"
    else:
        return "failed"


# check log in of coffee shops
@app.route("/login_api_coffee_shop", methods=['POST'])
def handleLogin_coffe_shop():
    isvalid = False
    login_info = request.form

    try:
        sql_query = "SELECT * FROM shop_login WHERE shop_id=%s AND shop_password=%s"
        data = (login_info['username'], login_info['password'])
        result = execute_query(sql_query, data)

        if result is None:
            return "failed"

        return login_info

    except:
        return "failed"


    
# backend handling of all customer overview page functionalities
@app.route("/customer_page_api", methods=['POST'])
def customer_page_handling():
    data_form = request.form

    
    sql_query = "SELECT * FROM customer_login WHERE customer_login.customer_id=%s AND customer_login.customer_password=%s"
    data = (data_form['username'], data_form['password'])
    result = execute_query(sql_query, data)

    if result is None:
        return "unverified connection"

    result_dict = dict()

    # coffee shops overview
    # "SELECT c.shop_id, c.name, c.city, r.score, ROUND(average_rating_mat.average_score, 1) FROM (coffee_shops c LEFT JOIN ratings r ON c.shop_id = r.shop_id) LEFT JOIN average_rating_mat ON average_rating_mat.shop_id = c.shop_id WHERE r.customer_id = {data_form['username']} ORDER BY r.score DESC;"
    coffee_shops_overview_query = f"SELECT c.shop_id, c.name, c.city, r.score, CAST(ROUND(average_rating_mat.average_score, 1) AS FLOAT) FROM (coffee_shops c LEFT JOIN ratings r ON c.shop_id = r.shop_id) LEFT JOIN average_rating_mat ON average_rating_mat.shop_id = c.shop_id WHERE r.customer_id = {data_form['username']} ORDER BY r.score DESC;"
    result_coffee_shops_overview = execute_query(coffee_shops_overview_query)
    result_dict["coffee_shops_overview"] = result_coffee_shops_overview

    # ratings
    ratings_overview_query = f"SELECT c.name, r.score FROM coffee_shops c JOIN ratings r ON c.shop_id = r.shop_id WHERE r.customer_id = {data_form['username']} ORDER BY r.score LIMIT 5;"
    result_ratings_overview = execute_query(ratings_overview_query)
    result_dict["ratings_overview"] = result_ratings_overview

    # recent orders
    recent_orders_overview_query = f"SELECT o.order_id, o.order_date, cof.name FROM (customers c JOIN orders o ON c.customer_id = o.customer_id) JOIN coffee_shops cof ON o.shop_id = cof.shop_id WHERE o.customer_id = {data_form['username']} ORDER BY o.order_date DESC LIMIT 5;"
    result_recent_orders_overview = execute_query(recent_orders_overview_query)
    result_dict["recent_orders_overview"] = result_recent_orders_overview

    return result_dict



@app.route("/coffee_shop_page_api", methods=['POST'])
def coffee_shop_page_handling():
    data = request.form

    try:
        sql_query = "SELECT * FROM shop_login WHERE shop_id=%s AND shop_password=%s"
        data_parsed = (data['username'], data['password'])
        result = execute_query(sql_query, data_parsed)

        if result is None:
            return "unverified connection"

        result_dict = dict()

        # coffee shops overview
        coffee_types_overview_query = f"SELECT ct.coffee_type, ct.size, FALSE AS is_not_null FROM coffee_types ct WHERE NOT EXISTS (SELECT 1 FROM coffee_shops_coffee_types rel WHERE ct.coffee_type = rel.coffee_type AND ct.size = rel.size AND rel.shop_id = {data['username']}) UNION (SELECT rel.coffee_type, rel.size, TRUE AS is_not_null FROM coffee_shops_coffee_types rel WHERE rel.shop_id = {data['username']}) ORDER BY coffee_type ASC, size DESC;"
        result_coffee_types_overview = execute_query(coffee_types_overview_query)
        result_dict["coffee_types_overview"] = result_coffee_types_overview

        # ratings
        ratings_overview_query = f"SELECT CONCAT(c.customer_firstname, '', c.customer_lastname), r.score FROM customers c JOIN ratings r ON c.customer_id = r.customer_id WHERE r.shop_id = {data['username']} ORDER BY r.score LIMIT 5;"
        result_ratings_overview = execute_query(ratings_overview_query)
        result_dict["ratings_overview"] = result_ratings_overview

        # recent orders
        recent_orders_overview_query = f"SELECT o.order_id, o.order_date, CONCAT(c.customer_firstname, '', c.customer_lastname) FROM customers c JOIN orders o ON c.customer_id = o.customer_id WHERE o.shop_id = {data['username']} ORDER BY o.order_date DESC;"
        result_recent_orders_overview = execute_query(recent_orders_overview_query)
        result_dict["recent_orders_overview"] = result_recent_orders_overview

        return result_dict

    except:
        return "unverified connection"

# api for returning the order details
@app.route("/ordering_page_api", methods=['POST'])
def loadOrderingCoffeeTypes():
    data = request.form

    try:
        sql_query = "SELECT * FROM customer_login WHERE customer_id=%s AND customer_password=%s"
        data_parsed = (data['username'], data['password'])
        result = execute_query(sql_query, data_parsed)

        if result is None:
            return "unverified connection"

        coffee_types_query = f"SELECT coffee_type, size FROM coffee_shops_coffee_types WHERE shop_id = {data['shop_id']}"  # coffee type query
        result = execute_query(coffee_types_query)
        return jsonify(result)

    except:
        return "unverified connection"


# api for returning the details of an order so that a coffee shop can see what has been ordered exactly
@app.route("/ordering_details_api", methods=['POST'])
def loadOrderingDetails():
    data = request.form

    order_details_query = f"SELECT coffee_type, size, nummer FROM orderitem WHERE order_id = {data['order_id']}"  # coffee type query
    result = execute_query(order_details_query)

    return jsonify(result)




## insertion queries ##
# api for updating an existing or inserting a new rating
@app.route("/rating_update_api", methods=['POST'])
def update_rating():
    data = request.form

    query = f"INSERT INTO ratings (customer_id, shop_id, score) VALUES ({data['customer_id']}, {data['shop_id']}, {data['score']}) ON DUPLICATE KEY UPDATE score = {data['score']};"
    execute_query(query)

    return "success"

# api for updating the offered coffee types by a specific coffee shop
@app.route("/coffee_types_update_api", methods=['POST'])
def update_coffee_types():
    data = request.form

    if data['is_offered'] == "false":
        query = f"INSERT INTO coffee_shops_coffee_types (shop_id, coffee_type, size) VALUES ({data['shop_id']}, '{data['coffee_type']}', '{data['size']}');"
    else:
        query = f"delete from coffee_shops_coffee_types where shop_id = {data['shop_id']} and coffee_type = '{data['coffee_type']}' and size = '{data['size']}';"
    execute_query(query)

    return "success"


# api for inserting a new order into the database system
@app.route("/order_processing_api", methods=['POST'])
def process_order():
    data = request.form

    

    current_date = date.today().strftime("%Y%m%d")

    query_last_id = f"select order_id from orders order by order_id desc limit 1;" # query to create order with its belonging order items

    last_id=execute_query(query_last_id)


    last_id_value = last_id[0][0]

    order_items_data = []
    for sublist in json.loads(data['order_items']):
        sublist.append(last_id_value+1)
        if sublist[2]>0:
            order_items_data.append(sublist)

    insert_items_tuples = ", ".join([str(tuple(row)) for row in order_items_data]) # order_id value still missing here

    # insertion queries
    insertion_query = f"""insert into orders (order_id, shop_id, customer_id, order_date) values ({last_id_value+1}, {data['shop_id']}, {data['customer_id']}, {current_date});"""
    execute_query(insertion_query)

    for row in order_items_data:
        send_tracking_message({"coffee_type": row[0], "size": row[1], "quantity": row[2], "timestamp": int(time.time())})
        insertion_query2 = f"insert into orderitem (coffee_type, size, nummer, order_id) values {str(tuple(row))};"
        execute_query(insertion_query2)

    
    return insertion_query2



# admin page sql queries (see query documentation for more information)
@app.route("/sql_abfrage", methods=["POST"])
def sql():
        sql_querry =request.form["querry"]

        df = pd.read_sql_query(sql_querry, db_connection)

        html_df=df.to_html()
        return html_df

@app.route("/sql_abfrage_tabel", methods=["POST"])
def sql_tabel():
        sql_querry =request.form["drop"]
        if sql_querry!="none":
            sql_querry=f"Select * From {sql_querry};"
            df = pd.read_sql_query(sql_querry, db_connection)
            html_df=df.to_html()
        elif sql_querry=="popular":
            sql_querry=f"Select coffee_type, sum(total_quantity) as total_sum From {sql_querry} group by coffee_type order by total_sum desc;"
            df = pd.read_sql_query(sql_querry, db_connection)
            html_df=df.to_html()
        else:
            html_df="Please select a table"
        return html_df


@app.route("/sql_drop_req", methods=["POST"])
def sql_drop_req():
    os.kill(os.getpid(),signal.SIGINT) # development test
    # drop_req =request.form["drop_req"]
    
    # if drop_req != "none":
    #     if drop_req == "AVG-Rating-Mat-view":
    #         sql_querry="SELECT * FROM public.average_rating_mat;"
    #         df = pd.read_sql_query(sql_querry, db_connection)
    #         html_df=df.to_html()
    #     elif drop_req == "worst-rating":
    #         sql_querry = "SELECT * FROM public.worst_shop_ratings;"
    #         df = pd.read_sql_query(sql_querry, db_connection)
    #         html_df=df.to_html()   
    #     elif drop_req == "Cross-types-shops":
    #         sql_querry = "SELECT * FROM coffee_shops CROSS JOIN coffee_types;"
    #         df = pd.read_sql_query(sql_querry, db_connection)
    #         html_df=df.to_html()
    # else:
    #     html_df="Please select a table"
        
    # return html_df


## tests for dynamic flask refreshes

# @app.route("/refresh_total", methods=["POST"])
# def do_refresh():
#     data=request.form["c"]
#     sys.stdout.flush()
#     raise SystemExit("A")
#     return "d"

# @app.route('/webhook', methods=['POST'])
# def handle_webhook():
#     print("Webhook empfangen. Flask-App wird neu gestartet.")
#     subprocess.Popen(['python', 'app.py']) 
#     return jsonify({'message': 'Webhook erhalten'})





# # Main method
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=options["port"])


    ## tests for flask dynamic reloading

    # scheduler = BackgroundScheduler()
    # scheduler.add_job(poll_database, 'interval', seconds=10)  # Poll the database every 5 seconds
    # scheduler.start()
    #subprocess.Popen(['python', 'app.py'])
