-- Creating a materialized view named "average_rating_mat" in the "public" schema.
-- This view calculates the average rating (average_score) for each coffee shop (shop_name).
CREATE MATERIALIZED VIEW public.average_rating_mat AS
SELECT 
    cs.shop_id AS shop_id,
    cs.name AS shop_name, 
    AVG(r.score) AS average_score
FROM 
    public.coffee_shops cs
JOIN 
    public.ratings r ON cs.shop_id = r.shop_id
GROUP BY 
    cs.shop_id;

-- Creating a unique index on the "shop_name" column of the "average_rating_mat" materialized view.
-- This can improve the performance of queries that filter or sort results based on the shop's name.
CREATE UNIQUE INDEX idx_average_rating_mat ON public.average_rating_mat (shop_id);

-- Creating or replacing a function named "refresh_average_rating_mat".
-- This function refreshes the materialized view "average_rating_mat".
-- It is defined as a trigger, which is a procedure that is automatically executed in response to certain events.
CREATE OR REPLACE FUNCTION refresh_average_rating_mat()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW public.average_rating_mat;
    RETURN NULL;
END $$ LANGUAGE plpgsql;

-- Creating a trigger named "refresh_average_rating_mat".
-- This trigger executes the "refresh_average_rating_mat" function after any INSERT, UPDATE, or DELETE operation on the "ratings" table.
-- This ensures that the "average_rating_mat" materialized view is always up to date with the latest ratings data.
CREATE TRIGGER refresh_average_rating_mat
AFTER INSERT OR UPDATE OR DELETE ON public.ratings
FOR EACH STATEMENT
EXECUTE PROCEDURE refresh_average_rating_mat();

-- Creating or replacing a view named "worst_shop_ratings" in the "public" schema.
-- This view shows the minimum rating (rating) given by each customer (customer_firstname, customer_lastname) to each coffee shop (shop_name).
-- It uses a common table expression (CTE) named "min_ratings" to first calculate the minimum rating for each shop.
CREATE OR REPLACE VIEW public.worst_shop_ratings AS
WITH min_ratings AS (
    SELECT 
        shop_id,
        MIN(score) AS min_score
    FROM 
        public.ratings
    GROUP BY 
        shop_id
)
SELECT 
    cs.name AS shop_name,
    c.customer_firstname,
    c.customer_lastname,
    mr.min_score AS rating
FROM 
    public.ratings r
JOIN 
    min_ratings mr ON r.shop_id = mr.shop_id AND r.score = mr.min_score
JOIN 
    public.customers c ON r.customer_id = c.customer_id
JOIN 
    public.coffee_shops cs ON r.shop_id = cs.shop_id;

-- creating a function to automatically give NaN ratings from a newly registered customer to each coffee shop
-- this is necessary for the some queries involving the ratings table to function (more can be read in documentation)
CREATE OR REPLACE FUNCTION add_rating_on_new_customer() RETURNS TRIGGER AS $$
DECLARE
  shop_cursor CURSOR FOR
    SELECT shop_id
    FROM coffee_shops;
  
  -- Variable to store the current shop_id
  shopId INTEGER;
BEGIN
  OPEN shop_cursor;
  
  -- Fetch the first shop_id
  FETCH NEXT FROM shop_cursor INTO shopId;
  
  -- Loop through each shop_id in the cursor
  LOOP
    -- Exit the loop if no more rows to fetch
    EXIT WHEN NOT FOUND;
    
    INSERT INTO ratings (customer_id, shop_id, score) 
    VALUES (NEW.customer_id, shopId, NULL);
    
    -- Fetch the next shop_id
    FETCH NEXT FROM shop_cursor INTO shopId;
  END LOOP;
  
  -- Close the cursor
  CLOSE shop_cursor;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER new_customer_trigger
AFTER INSERT ON customers
FOR EACH ROW
EXECUTE PROCEDURE add_rating_on_new_customer();


-- creating a function to automatically insert NaN ratings from all existing customers to a new coffee shop
-- serves the same reason as above (just now for the case a new coffee shop is registered)
CREATE OR REPLACE FUNCTION add_rating_on_new_shop() RETURNS TRIGGER AS $$
DECLARE
  customer_cursor CURSOR FOR
    SELECT customer_id
    FROM customers;
  
  -- Variable to store the current customer_id
  customerId INTEGER;
BEGIN
  -- Open the cursor
  OPEN customer_cursor;
  
  -- Fetch the first customer_id
  FETCH NEXT FROM customer_cursor INTO customerId;
  
  -- Loop through each customer_id in the cursor
  LOOP
    EXIT WHEN NOT FOUND;
    INSERT INTO ratings (customer_id, shop_id, score) 
    VALUES (customerId, NEW.shop_id, NULL);
    
    -- Fetch the next customer_id
    FETCH NEXT FROM customer_cursor INTO customerId;
  END LOOP;
  
  -- Close the cursor
  CLOSE customer_cursor;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER new_shop_trigger
AFTER INSERT ON coffee_shops
FOR EACH ROW
EXECUTE PROCEDURE add_rating_on_new_shop();
