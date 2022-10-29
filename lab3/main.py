import numpy as np
import pickle
import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd
from sqlalchemy import create_engine

from typing import Union, List, Tuple

# connection = pg.connect(host='pgsql-196447.vipserv.org', port=5432, dbname='wbauer_adb', user='wbauer_adb', password='adb2020');

db_string = "postgresql://wbauer_adb:adb2020@pgsql-196447.vipserv.org:5432/wbauer_adb"

db = create_engine(db_string)
connection_sqlalchemy = db.connect()

def film_in_category(category_id:int)->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o tytuł filmu, język, oraz kategorię dla zadanego id kategorii.
    Przykład wynikowej tabeli:
    |   |title          |languge    |category|
    |0	|Amadeus Holy	|English	|Action|
    
    Tabela wynikowa ma być posortowana po tylule filmu i języku.
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
    
    Parameters:
    category_id (int): wartość id kategorii dla którego wykonujemy zapytanie
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(category_id, int):
        return pd.read_sql(f'''SELECT film.title, language.name as language, category.name as category\
                            FROM film\
                        INNER JOIN language  ON language.language_id = film.language_id\
                    INNER JOIN film_category ON film_category.film_id = film.film_id\
                INNER JOIN category ON category.category_id = film_category.category_id\
            WHERE category.category_id = {category_id}\
        ORDER BY title''',con=connection_sqlalchemy)
    else:
        return None

def number_films_in_category(category_id:int)->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o ilość filmów w zadanej kategori przez id kategorii.
    Przykład wynikowej tabeli:
    |   |category   |count|
    |0	|Action 	|64	  | 
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    category_id (int): wartość id kategorii dla którego wykonujemy zapytanie
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(category_id, int):
        return pd.read_sql(f'''SELECT category.name as category, count(film.title) \
                            FROM film\
                            INNER JOIN language  ON language.language_id = film.language_id\
                            INNER JOIN film_category ON film_category.film_id = film.film_id\
                            INNER JOIN category ON category.category_id = film_category.category_id\
                            WHERE category.category_id = {category_id}\
                            GROUP BY category.name''',con=connection_sqlalchemy)
    else:
        return None

def number_film_by_length(min_length: Union[int,float] = 0, max_length: Union[int,float] = 1e6 ) :
    ''' Funkcja zwracająca wynik zapytania do bazy o ilość filmów o dla poszczegulnych długości pomiędzy wartościami min_length a max_length.
    Przykład wynikowej tabeli:
    |   |length     |count|
    |0	|46 	    |64	  | 
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    min_length (int,float): wartość minimalnej długości filmu
    max_length (int,float): wartość maksymalnej długości filmu
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(min_length, int) and isinstance(max_length, int):
        return pd.read_sql(f'''SELECT length, count(title)\
            FROM film\
            WHERE length BETWEEN {min_length} and {max_length}\
            GROUP BY length''',con=connection_sqlalchemy)
    else:
        return None

def client_from_city(city:str)->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o listę klientów z zadanego miasta przez wartość city.
    Przykład wynikowej tabeli:
    |   |city	    |first_name	|last_name
    |0	|Athenai	|Linda	    |Williams
    
    Tabela wynikowa ma być posortowana po nazwisku i imieniu klienta.
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    city (str): nazwa miaste dla którego mamy sporządzić listę klientów
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(city, str):
        return pd.read_sql(f"""SELECT city.city, customer.first_name, customer.last_name\
                            FROM customer\
                        INNER JOIN address ON address.address_id = customer.customer_id\
                    INNER JOIN city ON city.city_id = address.city_id\
                    WHERE city.city = '{city}'""", con=connection_sqlalchemy)
    else:
        return None

def avg_amount_by_length(length:Union[int,float])->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o średnią wartość wypożyczenia filmów dla zadanej długości length.
    Przykład wynikowej tabeli:
    |   |length |avg
    |0	|48	    |4.295389
    
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    length (int,float): długość filmu dla którego mamy pożyczyć średnią wartość wypożyczonych filmów
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(length, int) or isinstance(length, float):
        return pd.read_sql(f"""SELECT length, avg(amount) FROM film\
        INNER JOIN Inventory on inventory.film_id = film.film_id\
        INNER JOIN rental on rental.inventory_id = inventory.inventory_id\
        INNER JOIN payment on payment.customer_id = rental.customer_id\
        WHERE length = {length} GROUP BY length""", con=connection_sqlalchemy)
    else:
        return None
    

def client_by_sum_length(sum_min:Union[int,float])->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o sumaryczny czas wypożyczonych filmów przez klientów powyżej zadanej wartości .
    Przykład wynikowej tabeli:
    |   |first_name |last_name  |sum
    |0  |Brian	    |Wyman  	|1265
    
    Tabela wynikowa powinna być posortowane według sumy, nazwiska i imienia klienta.
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    sum_min (int,float): minimalna wartość sumy długości wypożyczonych filmów którą musi spełniać klient
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(sum_min, int) or isinstance(sum_min, float):
        return pd.read_sql(f"""SELECT customer.first_name, customer.last_name, sum(film.length)  FROM film\
        INNER JOIN inventory on inventory.film_id = film.film_id\
        INNER JOIN rental on rental.inventory_id = inventory.inventory_id\
        INNER JOIN customer on customer.customer_id = rental.customer_id\
        GROUP BY customer.first_name, customer.last_name
        HAVING sum(film.length) > {sum_min}
        ORDER BY sum(film.length), customer.first_name, customer.last_name""", con=connection_sqlalchemy)
    else:
        return None  


def category_statistic_length(name:str)->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o statystykę długości filmów w kategorii o zadanej nazwie.
    Przykład wynikowej tabeli:
    |   |category   |avg    |sum    |min    |max
    |0	|Action 	|111.60 |7143   |47 	|185
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    name (str): Nazwa kategorii dla której ma zostać wypisana statystyka
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(name, str):
        return pd.read_sql(f"""SELECT category.name, avg(film.length), sum(film.length), min(film.length), max(film.length) FROM category\
            INNER JOIN film_category on film_category.category_id = category.category_id\
            INNER JOIN film on film.film_id = film_category.film_id\
            WHERE category.name = '{name}'\
            GROUP BY category.name\
            """, con=connection_sqlalchemy)
    else:
        return None
