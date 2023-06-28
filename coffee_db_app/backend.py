from flask import Flask, render_template, request, redirect
import psycopg2
import pandas as pd
from datetime import datetime, date
import json


app = Flask(__name__, template_folder='templateFiles', static_folder='staticFiles')


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

    
    conn = psycopg2.connect(
        host="coffee_db_container",
        port = 5432,
        database="coffee_db",
        user="coffee_db_technical_user",
        password="coffeedb")
    
    cursor = conn.cursor()
    
    # checking validity of user
    try:
        sql_query = "SELECT * FROM customer_login WHERE customer_login.customer_id='"+login_info['username']+"' AND customer_login.customer_password='" + login_info['password'] + "'"
        cursor.execute(sql_query)
        result = cursor.fetchone()
        conn.commit()
        conn.close()
        if result is None:
            return "failed"


        return login_info

    except:
        return "failed"


    
# registering a new customer
@app.route("/signup_api_customer", methods=['POST'])
def handleSignup_customer():
    isvalid = False
    signup_info = request.form

    conn = psycopg2.connect(
        host="coffee_db_container",
        port = 5432,
        database="coffee_db",
        user="coffee_db_technical_user",
        password="coffeedb")
    
    cursor = conn.cursor()

    try:
        sql_query = "insert into customers (customer_id, customer_firstname, customer_lastname) values (" + signup_info['username'] + ",'" + signup_info['firstname'] + "','" + signup_info['lastname'] + "'); insert into customer_login (customer_id, customer_password) values (" + signup_info['username'] + ",'" + signup_info['password'] + "');"
        cursor.execute(sql_query)
        
        isvalid=True

    except:
        isvalid=False

    conn.commit()
    conn.close()

    if isvalid:
        return "successful"
    else:
        return "failed"


# check log in of coffee shops
@app.route("/login_api_coffee_shop", methods=['POST'])
def handleLogin_coffe_shop():
    isvalid = False
    login_info = request.form

    conn = psycopg2.connect(
        host="coffee_db_container",
        port = 5432,
        database="coffee_db",
        user="coffee_db_technical_user",
        password="coffeedb")
    
    cursor = conn.cursor()
    
    try:
        sql_query = "SELECT * FROM shop_login WHERE shop_id='"+login_info['username']+"' AND shop_password='" + login_info['password'] + "'"
        cursor.execute(sql_query)
        result = cursor.fetchone()
        conn.commit()
        conn.close()
        if result is None:
            return "failed"


        return login_info

    except:
        return "failed"


    
# registering a new coffee shop
@app.route("/signup_api_coffee_shop", methods=['POST'])
def handleSignup_coffe_shop():
    isvalid = False
    signup_info = request.form

    # checking validity
    # Verbindungszeichenfolge erstellen
    conn = psycopg2.connect(
        host="coffee_db_container",
        port = 5432,
        database="coffee_db",
        user="coffee_db_technical_user",
        password="coffeedb")
    
    cursor = conn.cursor()

    try:
        sql_query = "insert into coffee_shops (shop_id, name, country, city, street, owner_firstname, owner_lastname) values (" + signup_info['shop_id'] + ",'" + signup_info['name'] + "','" + signup_info['country'] + "','" + signup_info['city'] + "','" + signup_info['street'] + "','"+  signup_info['owner_firstname'] + "','" + signup_info['owner_lastname'] + "'); insert into shop_login (shop_id, shop_password) values (" + signup_info['shop_id'] + ",'" + signup_info['password'] + "');"
        cursor.execute(sql_query)
        
        isvalid=True

    except:
        isvalid=False

    conn.commit()
    conn.close()

    if isvalid:
        return "successful"
    else:
        return "failed"
    
# backend handling of all customer overview page functionalities
@app.route("/customer_page_api", methods=['POST'])
def customer_page_handling():
        

    data = request.form

    conn = psycopg2.connect(
        host="coffee_db_container",
        port = 5432,
        database="coffee_db",
        user="coffee_db_technical_user",
        password="coffeedb")
    
    cursor = conn.cursor()
    
    try:

        # password query is always executed before any other query to check validity of login information!
        sql_query = "SELECT * FROM customer_login WHERE customer_login.customer_id='"+data['username']+"' AND customer_login.customer_password='" + data['password'] + "'"
        cursor.execute(sql_query)
        result = cursor.fetchone()
        if result is None:
            return "unverified connection"


        # returning all the stats for the customer landing page
        result_dict=dict()


        # coffee shops overview
        coffee_shops_overview_query = f"select c.shop_id, c.name, c.city, r.score, round(average_rating_mat.average_score, 1) from (coffee_shops c left join ratings r  on c.shop_id = r.shop_id) left join average_rating_mat on average_rating_mat.shop_id = c.shop_id where r.customer_id = {data['username']} order by r.score desc;"
        cursor.execute(coffee_shops_overview_query)
        result_coffee_shops_overview = cursor.fetchall()
        result_dict["coffee_shops_overview"] = result_coffee_shops_overview

        # ratings
        ratings_overview_query = f"select c.name, r.score from coffee_shops c join ratings r on c.shop_id = r.shop_id where r.customer_id = {data['username']} order by r.score limit 5;"
        cursor.execute(ratings_overview_query)
        result_ratings_overview = cursor.fetchall()
        result_dict["ratings_overview"] = result_ratings_overview

        # recent orders
        recent_orders_overview_query = f"select o.order_id, o.order_date, cof.name  from (customers c join orders o on c.customer_id = o.customer_id) join coffee_shops cof on o.shop_id = cof.shop_id where o.customer_id = {data['username']} order by o.order_date desc limit 5;"
        cursor.execute(recent_orders_overview_query)
        result_recent_orders_overview = cursor.fetchall()
        result_dict["recent_orders_overview"] = result_recent_orders_overview

        conn.commit()
        cursor.close()
        conn.close()

        return result_dict

    except:

        return "unverified connection"
    

# backend handling of all coffee shop overview page functionalities
@app.route("/coffee_shop_page_api", methods=['POST'])
def coffee_shop_page_handling():
        

    data = request.form

    conn = psycopg2.connect(
        host="coffee_db_container",
        port = 5432,
        database="coffee_db",
        user="coffee_db_technical_user",
        password="coffeedb")
    
    cursor = conn.cursor()
    
    try:
        # password query is always executed before any other query to check validity of login information!
        sql_query = "SELECT * FROM shop_login WHERE shop_id="+data['username']+" AND shop_password='" + data['password'] + "'"
        cursor.execute(sql_query)
        result = cursor.fetchall()
        if result is None:
            return "unveriefied connection"
        

        # returning all the stats for the customer landing page
        result_dict=dict()


        # coffee shops overview
        coffee_types_overview_query = f"SELECT ct.coffee_type, ct.size, false AS is_not_null FROM coffee_types ct WHERE NOT EXISTS (SELECT 1 FROM coffee_shops_coffee_types rel WHERE ct.coffee_type = rel.coffee_type AND ct.size = rel.size AND rel.shop_id = {data['username']}) UNION (SELECT rel.coffee_type, rel.size, true AS is_not_null FROM coffee_shops_coffee_types rel WHERE rel.shop_id = {data['username']}) ORDER BY coffee_type asc, size desc;"
        cursor.execute(coffee_types_overview_query)
        result_coffee_types_overview = cursor.fetchall()
        result_dict["coffee_types_overview"] = result_coffee_types_overview

        # ratings
        ratings_overview_query = f"select c.customer_firstname || '' || c.customer_lastname as customer_name, r.score from customers c join ratings r on c.customer_id = r.customer_id where r.shop_id = {data['username']} order by r.score limit 5;"
        cursor.execute(ratings_overview_query)
        result_ratings_overview = cursor.fetchall()
        result_dict["ratings_overview"] = result_ratings_overview

        # recent orders
        recent_orders_overview_query = f"select o.order_id, o.order_date, c.customer_firstname || '' || c.customer_lastname as customer_name  from customers c join orders o on c.customer_id = o.customer_id where o.shop_id = {data['username']} order by o.order_date desc;"
        cursor.execute(recent_orders_overview_query)
        result_recent_orders_overview = cursor.fetchall()
        result_dict["recent_orders_overview"] = result_recent_orders_overview


        conn.commit()
        cursor.close()
        conn.close()

        return result_dict

    except:

        return "unverified connection"


# api for returning the order details
@app.route("/ordering_page_api", methods=['POST'])
def loadOrderingCoffeeTypes():
    data = request.form

    conn = psycopg2.connect(
        host="coffee_db_container",
        port = 5432,
        database="coffee_db",
        user="coffee_db_technical_user",
        password="coffeedb")
    
    cursor = conn.cursor()
    
    try:
        # password query is always executed before any other query to check validity of login information!
        sql_query = "SELECT * FROM customer_login WHERE customer_id="+data['username']+" AND customer_password='" + data['password'] + "'"
        cursor.execute(sql_query)
        result = cursor.fetchall()
        if result is None:
            return "unverified connection"
        
        coffee_types_query = f"select coffee_type, size from coffee_shops_coffee_types where shop_id = {data['shop_id']}" # coffee type query
        cursor.execute(coffee_types_query)
        result = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()

        return result

    
    except:
        return "unverified connection"


# api for returning the details of an order so that a coffee shop can see what has been ordered exactly
@app.route("/ordering_details_api", methods=['POST'])
def loadOrderingDetails():
    data = request.form

    conn = psycopg2.connect(
        host="coffee_db_container",
        port = 5432,
        database="coffee_db",
        user="coffee_db_technical_user",
        password="coffeedb")
    
    cursor = conn.cursor()
    
    try:
        # password query is always executed before any other query to check validity of login information!
        sql_query = "SELECT * FROM shop_login WHERE shop_id="+data['username']+" AND shop_password='" + data['password'] + "'"
        cursor.execute(sql_query)
        result = cursor.fetchall()
        if result is None:
            return "unverified connection"
        
        
        order_details_query = f"select coffee_type, size, number from orderitem where order_id = {data['order_id']}" # coffee type query
        
        cursor.execute(order_details_query)
        result = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()

        return result

    
    except:
        return "unverified connection"



## insertion queries ##
# api for updating an existing or inserting a new rating
@app.route("/rating_update_api", methods=['POST'])
def update_rating():
    data = request.form
    conn = psycopg2.connect(
        host="coffee_db_container",
        port = 5432,
        database="coffee_db",
        user="coffee_db_technical_user",
        password="coffeedb")
    cursor = conn.cursor()

    query = f"INSERT INTO ratings (customer_id, shop_id, score) VALUES ({data['customer_id']}, {data['shop_id']}, {data['score']}) ON CONFLICT (customer_id, shop_id) DO UPDATE SET score = {data['score']};"
    cursor.execute(query)

    conn.commit()
    cursor.close()
    conn.close()

    return "success"

# api for updating the offered coffee types by a specific coffee shop
@app.route("/coffee_types_update_api", methods=['POST'])
def update_coffee_types():
    data = request.form
    conn = psycopg2.connect(
        host="coffee_db_container",
        port = 5432,
        database="coffee_db",
        user="coffee_db_technical_user",
        password="coffeedb")
    cursor = conn.cursor()
    if data['is_offered'] == "false":
        query = f"INSERT INTO coffee_shops_coffee_types (shop_id, coffee_type, size) VALUES ({data['shop_id']}, '{data['coffee_type']}', '{data['size']}');"
    else:
        query = f"delete from coffee_shops_coffee_types where shop_id = {data['shop_id']} and coffee_type = '{data['coffee_type']}' and size = '{data['size']}';"
    cursor.execute(query)

    conn.commit()
    cursor.close()
    conn.close()

    return "success"


# api for inserting a new order into the database system
@app.route("/order_processing_api", methods=['POST'])
def process_order():
    data = request.form

    

    current_date = date.today().strftime("%Y%m%d")

    conn = psycopg2.connect(
        host="coffee_db_container",
        port = 5432,
        database="coffee_db",
        user="coffee_db_technical_user",
        password="coffeedb")
    cursor = conn.cursor()

    query_last_id = f"select order_id from orders order by order_id desc limit 1;" # query to create order with its belonging order items

    cursor.execute(query_last_id)

    last_id = cursor.fetchall()

    last_id_value = last_id[0][0]

    order_items_data = []
    for sublist in json.loads(data['order_items']):
        sublist.append(last_id_value+1)
        order_items_data.append(sublist)

    insert_items_tuples = ", ".join([str(tuple(row)) for row in order_items_data]) # order_id value still missing here

    # insertion queries
    insertion_query = f"""insert into orders (order_id, shop_id, customer_id, order_date) values ({last_id_value+1}, {data['shop_id']}, {data['customer_id']}, {current_date});
                          insert into orderitem (coffee_type, size, number, order_id) values {insert_items_tuples};"""

    cursor.execute(insertion_query)
    conn.commit()
    cursor.close()
    conn.close()

    return "success"



# admin page sql queries (see query documentation for more information)
@app.route("/sql_abfrage", methods=["POST"])
def sql():
        sql_querry =request.form["querry"]

        conn = psycopg2.connect(
            host="coffee_db_container",
            port = 5432,
            database="coffee_db",
            user="coffee_db_technical_user",
            password="coffeedb")
        df = pd.read_sql_query(sql_querry, conn)
        conn.close()
        html_df=df.to_html()
        return html_df

@app.route("/sql_abfrage_tabel", methods=["POST"])
def sql_tabel():
        sql_querry =request.form["drop"]
        if sql_querry!="none":

            conn = psycopg2.connect(
                host="coffee_db_container",
                port = 5432,
                database="coffee_db",
                user="coffee_db_technical_user",
                password="coffeedb")
            sql_querry=f"Select * From {sql_querry};"
            df = pd.read_sql_query(sql_querry, conn)
            conn.close()
            html_df=df.to_html()
        else:
            html_df="Please select a table"
        return html_df

@app.route("/sql_drop_req", methods=["POST"])
def sql_drop_req():
    drop_req =request.form["drop_req"]
    conn = psycopg2.connect(
        host="coffee_db_container",
        port = 5432,
        database="coffee_db",
        user="coffee_db_technical_user",
        password="coffeedb")
    
    if drop_req != "none":
        if drop_req == "AVG-Rating-Mat-view":
            sql_querry="SELECT * FROM public.average_rating_mat;"
            df = pd.read_sql_query(sql_querry, conn)
            conn.close()
            html_df=df.to_html()
        elif drop_req == "worst-rating":
            sql_querry = "SELECT * FROM public.worst_shop_ratings;"
            df = pd.read_sql_query(sql_querry, conn)
            conn.close()
            html_df=df.to_html()   
        elif drop_req == "Cross-types-shops":
            sql_querry = "SELECT * FROM coffee_shops CROSS JOIN coffee_types;"
            df = pd.read_sql_query(sql_querry, conn)
            conn.close()
            html_df=df.to_html()
    else:
        html_df="Please select a table"
        
    return html_df





    