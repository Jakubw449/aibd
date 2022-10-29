import numpy as np
import pickle

import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd
from sqlalchemy import create_engine

from typing import Union, List, Tuple

connection = pg.connect(host='pgsql-196447.vipserv.org', port=5432, dbname='wbauer_adb', user='wbauer_adb', password='adb2020');

db_string = "postgresql://wbauer_adb:adb2020@pgsql-196447.vipserv.org:5432/wbauer_adb"

db = create_engine(db_string)
connection_sqlalchemy = db.connect()

def film_in_category(category:Union[int,str])->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o tytuł filmu, język, oraz kategorię dla zadanego:
        - id: jeżeli categry jest int
        - name: jeżeli category jest str, dokładnie taki jak podana wartość
    Przykład wynikowej tabeli:
    |   |title          |languge    |category|
    |0	|Amadeus Holy	|English	|Action|
    
    Tabela wynikowa ma być posortowana po tylule filmu i języku.
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
    
    Parameters:
    category (int,str): wartość kategorii po id (jeżeli typ int) lub nazwie (jeżeli typ str)  dla którego wykonujemy zapytanie
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(category, int):
        return pd.read_sql(f'''SELECT film.title, language.name as languge, category.name as category\
                            FROM film\
                        INNER JOIN language  ON language.language_id = film.language_id\
                    INNER JOIN film_category ON film_category.film_id = film.film_id\
                INNER JOIN category ON category.category_id = film_category.category_id\
            WHERE category.category_id = {category}\
        ORDER BY title''',con=connection_sqlalchemy)
    if isinstance(category, str):
        return pd.read_sql(f'''SELECT film.title, language.name as languge, category.name as category\
                            FROM film\
                        INNER JOIN language  ON language.language_id = film.language_id\
                    INNER JOIN film_category ON film_category.film_id = film.film_id\
                INNER JOIN category ON category.category_id = film_category.category_id\
            WHERE category.name LIKE '{category}'\
        ORDER BY title''',con=connection_sqlalchemy)
    else:
        return None
    
def film_in_category_case_insensitive(category:Union[int,str])->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o tytuł filmu, język, oraz kategorię dla zadanego:
        - id: jeżeli categry jest int
        - name: jeżeli category jest str
    Przykład wynikowej tabeli:
    |   |title          |languge    |category|
    |0	|Amadeus Holy	|English	|Action|
    
    Tabela wynikowa ma być posortowana po tylule filmu i języku.
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
    
    Parameters:
    category (int,str): wartość kategorii po id (jeżeli typ int) lub nazwie (jeżeli typ str)  dla którego wykonujemy zapytanie
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(category, int):
        return pd.read_sql(f'''SELECT film.title, language.name as languge, category.name as category\
                            FROM film\
                        INNER JOIN language  ON language.language_id = film.language_id\
                    INNER JOIN film_category ON film_category.film_id = film.film_id\
                INNER JOIN category ON category.category_id = film_category.category_id\
            WHERE category.category_id = {category}\
        ORDER BY title''',con=connection_sqlalchemy)
    if isinstance(category, str):
        return pd.read_sql(f'''SELECT film.title, language.name as languge, category.name as category\
                            FROM film\
                        INNER JOIN language  ON language.language_id = film.language_id\
                    INNER JOIN film_category ON film_category.film_id = film.film_id\
                INNER JOIN category ON category.category_id = film_category.category_id\
            WHERE category.name ILIKE '{category}'\
        ORDER BY title''',con=connection_sqlalchemy)
    else:
        return None
    
def film_cast(title:str)->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o obsadę filmu o dokładnie zadanym tytule.
    Przykład wynikowej tabeli:
    |   |first_name |last_name  |
    |0	|Greg       |Chaplin    | 
    
    Tabela wynikowa ma być posortowana po nazwisku i imieniu klienta.
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    title (int): wartość id kategorii dla którego wykonujemy zapytanie
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(title, str):
        return pd.read_sql(f"""SELECT actor.first_name, actor.last_name FROM film\
            INNER JOIN film_actor fc on fc.film_id = film.film_id\
            INNER JOIN actor on actor.actor_id = fc.actor_id\
            WHERE film.title LIKE '{title}'\
            ORDER BY actor.last_name, actor.first_name""",con=connection_sqlalchemy)
    else:
        return None

def film_title_case_insensitive(words:list) :
    ''' Funkcja zwracająca wynik zapytania do bazy o tytuły filmów zawierających conajmniej jedno z podanych słów z listy words.
    Przykład wynikowej tabeli:
    |   |title              |
    |0	|Crystal Breaking 	| 
    
    Tabela wynikowa ma być posortowana po nazwisku i imieniu klienta.
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    words(list): wartość minimalnej długości filmu
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    
    if isinstance(words, list):
        str = '|'.join(words)
        return pd.read_sql(f"""SELECT title from film\
            where lower(title) ~* '(?:^| )({str})""" + """{1,}(?:$| )' order by title""",con=connection_sqlalchemy)
    else:
        return None