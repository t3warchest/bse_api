from fastapi import FastAPI,status, HTTPException
from typing import List
import redis
import json
import datetime

from . import schemas
from . database import create_connection

app = FastAPI()
rd = redis.Redis("localhost",port=6379,db=0)
conn = create_connection()
cursor = conn.cursor()



# route to get top 10 stocks: localhost:8000/stocks/top10
@app.get("/stocks/top10",response_model=List[schemas.GetStock])
def get_top_10():
    cursor.execute("""SELECT * FROM equity_bhavcopy_data LIMIT 10""")
    stocks = cursor.fetchall()
    return stocks


# route to get stock by name: localhost:8000/stocks/{name}
@app.get("/stocks/{name}",response_model=schemas.GetStock)
def get_by_name(name : str):
    
    cached_data = rd.get(name)
    
    if cached_data:
        print("hit")
        
        json_format =  json.loads(cached_data)
        
        #converting date to compabitble format for pydantic 
        json_format['date'] = datetime.datetime.strptime("2020-01-01", "%Y-%m-%d")
        
        return json_format
    
    else:
        
        print("miss")
        
        # to store into redis making dictionary of fetched data from pg and jsonifying the dict
        
        # getting columns of table 
        cursor.execute("""SELECT * FROM equity_bhavcopy_data LIMIT 1""")
        column_list = cursor.fetchone()
        columns = []
        for i in column_list:
            columns.append(i) 
        
        # making the query to pg db
        cursor.execute("""SELECT * FROM equity_bhavcopy_data WHERE name=(%s)""",(name,))
        stock = cursor.fetchone()
        
        if not stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"no such stock with name {name}")
        # storing into redis
        python_data= {}
        for col in columns:
            python_data[col] = stock[col]
        redist_data = json.dumps(python_data,default=str)
        rd.set(name,redist_data)
        
        # setting expiration time of 30 minutess
        rd.expire(name, 1800)

    return stock


# function to post to favourite stock
@app.post('/favs/post',status_code =status.HTTP_201_CREATED,response_model=schemas.GetStock)
def add_to_fav(stock : schemas.AddToFav):
    
    # just for added security if there are 2 companies being mistakenly listed with same name
    # check corresponding code as well
    
    cursor.execute("""SELECT * FROM equity_bhavcopy_data WHERE name =%s""",(stock.name,))
    db_stock= cursor.fetchone()
    
    if not db_stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="no such stock")
    
    if db_stock['code'] != stock.code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="no such stock with same code")
    
    # query to return stock that is not already in favoutites
    cursor.execute("""SELECT id 
                   FROM equity_bhavcopy_data 
                   WHERE (NOT EXISTS (SELECT * FROM favourites WHERE equity_bhavcopy_data.id = favourites.stock_id)) 
                   AND name =%s AND code =%s""",(stock.name,stock.code))
    fav_stock_id = cursor.fetchone()
    
    if not fav_stock_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="this stock is already in favourites")
    
    # storing into db
    id = fav_stock_id['id']
    cursor.execute(""" INSERT INTO favourites (stock_id) VALUES (%s) RETURNING *""",[id])
    conn.commit()
    
    # now that fav tbale is changed expiring the already present fav key in redis
    rd.delete('favs')
    return db_stock


# get favourites
@app.get('/favs',response_model=List[schemas.GetStock])
def get_favs():
    # same caching proces:
    
    cached_data = rd.get('favs')
    
    if cached_data:
        print("hit")
        
        a =  json.loads(cached_data)
        for i in range(len(a)):
            a[i]['date'] = datetime.datetime.strptime("2020-01-01", "%Y-%m-%d")
        return a
    
    else:
        print("miss")
        
        cursor.execute("""SELECT * FROM equity_bhavcopy_data LIMIT 1""")
        column_list = cursor.fetchone()
        columns = []
        for i in column_list:
            columns.append(i) 
        
        cursor.execute("""
                   SELECT id,code,name,open,close,high,low,date
                   FROM equity_bhavcopy_data
                   RIGHT JOIN favourites 
                   ON stock_id = id;
                   """)
        favs = cursor.fetchall()
        
        data_list = []
        for row in favs:
            python_data= {}
            for col in columns:
                python_data[col] = row[col]
            data_list.append(python_data)
            
        redist_data = json.dumps(data_list,default=str)
        rd.set('favs',redist_data)
            
    return favs


# del favoutite
@app.delete("/favs/{name}",status_code=status.HTTP_204_NO_CONTENT)
def delete_fav(name : str):
    
    cursor.execute("""SELECT * FROM equity_bhavcopy_data WHERE name =%s""",(name,))
    stock = cursor.fetchone()
    
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"No stock with name {name}")
    
    # query to chekc if stock in favourites
    cursor.execute(""" SELECT stock_id FROM favourites
                   LEFT JOIN equity_bhavcopy_data
                   ON favourites.stock_id = equity_bhavcopy_data.id 
                   WHERE equity_bhavcopy_data.name = %s""",(name,))
    stock_id = cursor.fetchone()
    if not stock_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"No stock with name {name} in favourites")
    
    cursor.execute("""DELETE FROM favourites WHERE stock_id = %s RETURNING *""",(stock_id['stock_id'],))
    conn.commit()


# getting opening of 10 companies
@app.get("/history",response_model=List[schemas.StockHistory])
def get_history():
    cached_data = rd.get('history')
    
    if cached_data:
        print("hit")
        a =  json.loads(cached_data)
        return a
    else:
        print("miss")
        cursor.execute(""" SELECT open FROM equity_bhavcopy_data Limit 10""")
        history = cursor.fetchall()
        data_list = []
        for row in history:
            python_data= {}
            for _ in range(1):
                python_data['open'] = row['open']
            data_list.append(python_data)
        redist_data = json.dumps(data_list,default=str)
        rd.set('history',redist_data)
        rd.expire('histoty', 1800)
            
    return history

    
    
    