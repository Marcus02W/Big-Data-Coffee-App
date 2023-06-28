BEGIN;


CREATE TABLE IF NOT EXISTS public.coffee_shops
(
    shop_id integer NOT NULL,
    name character varying COLLATE pg_catalog."default" NOT NULL,
    country character varying COLLATE pg_catalog."default" NOT NULL,
    city character varying COLLATE pg_catalog."default" NOT NULL,
    street character varying COLLATE pg_catalog."default" NOT NULL,
    owner_firstname character varying COLLATE pg_catalog."default" NOT NULL,
    owner_lastname character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT coffee_shops_pkey PRIMARY KEY (shop_id)
);

CREATE TABLE IF NOT EXISTS public.coffee_shops_coffee_types
(
    shop_id integer NOT NULL,
    coffee_type character varying COLLATE pg_catalog."default" NOT NULL,
    size character varying COLLATE pg_catalog."default" NOT NULL
);

CREATE TABLE IF NOT EXISTS public.coffee_types
(
    coffee_type character varying COLLATE pg_catalog."default" NOT NULL,
    size character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT coffee_types_pkey PRIMARY KEY (coffee_type, size)
);

CREATE TABLE IF NOT EXISTS public.customer_login
(
    customer_id integer NOT NULL,
    customer_password character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT customer_login_pkey PRIMARY KEY (customer_id, customer_password)
);

CREATE TABLE IF NOT EXISTS public.customers
(
    customer_id integer NOT NULL,
    customer_firstname character varying COLLATE pg_catalog."default",
    customer_lastname character varying COLLATE pg_catalog."default",
    CONSTRAINT customers_pkey PRIMARY KEY (customer_id)
);

CREATE TABLE IF NOT EXISTS public.orderitem
(
    coffee_type character varying COLLATE pg_catalog."default" NOT NULL,
    size character varying COLLATE pg_catalog."default" NOT NULL,
    "number" integer,
    order_id integer NOT NULL,
    CONSTRAINT orderitem_pkey PRIMARY KEY (coffee_type, size, order_id)
);

CREATE TABLE IF NOT EXISTS public.orders
(
    order_id integer NOT NULL,
    shop_id integer,
    customer_id integer,
    order_date integer,
    CONSTRAINT order_pkey PRIMARY KEY (order_id)
);

CREATE TABLE IF NOT EXISTS public.ratings
(
    customer_id integer NOT NULL,
    shop_id integer NOT NULL,
    score integer,
    CONSTRAINT ratings_pkey PRIMARY KEY (customer_id, shop_id)
);

CREATE TABLE IF NOT EXISTS public.shop_login
(
    shop_password character varying COLLATE pg_catalog."default" NOT NULL,
    shop_id integer NOT NULL,
    CONSTRAINT shop_login_pkey PRIMARY KEY (shop_password, shop_id)
);

ALTER TABLE IF EXISTS public.coffee_shops_coffee_types
    ADD CONSTRAINT shop_connector_mn FOREIGN KEY (shop_id)
    REFERENCES public.coffee_shops (shop_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.coffee_shops_coffee_types
    ADD CONSTRAINT type_connector_mn FOREIGN KEY (coffee_type, size)
    REFERENCES public.coffee_types (coffee_type, size) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.customer_login
    ADD CONSTRAINT customer_connector_p FOREIGN KEY (customer_id)
    REFERENCES public.customers (customer_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.orderitem
    ADD CONSTRAINT order_connector FOREIGN KEY (order_id)
    REFERENCES public.orders (order_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.orderitem
    ADD CONSTRAINT type_connector FOREIGN KEY (coffee_type, size)
    REFERENCES public.coffee_types (coffee_type, size) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.orders
    ADD CONSTRAINT customer_connector2 FOREIGN KEY (customer_id)
    REFERENCES public.customers (customer_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.orders
    ADD CONSTRAINT shop_connector2 FOREIGN KEY (shop_id)
    REFERENCES public.coffee_shops (shop_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.ratings
    ADD CONSTRAINT customer_connector FOREIGN KEY (customer_id)
    REFERENCES public.customers (customer_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.ratings
    ADD CONSTRAINT shop_connector FOREIGN KEY (shop_id)
    REFERENCES public.coffee_shops (shop_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.shop_login
    ADD CONSTRAINT shop_connector_p FOREIGN KEY (shop_id)
    REFERENCES public.coffee_shops (shop_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

END;