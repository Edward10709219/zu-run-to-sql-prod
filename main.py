import os
import ssl
from datetime import datetime
import time
import random
import hashlib


from fastapi import Depends, FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Union
import pandas as pd

import sqlalchemy
import pg8000
from google.cloud.sql.connector import Connector, IPTypes

from sql_tools import SQLTools
import sql_query_string as query_str



app = FastAPI()

# 資料庫連線 TCP/UNIX
# db_user = os.environ["DB_USER"]  # e.g. 'my-db-user'
# db_pass = os.environ["DB_PASS"]  # e.g. 'my-db-password'
# db_name = os.environ["DB_NAME"]  # e.g. 'my-database'
# unix_socket_path = os.environ["INSTANCE_UNIX_SOCKET"]
# db_url = sqlalchemy.engine.url.URL.create(
#     drivername="postgresql+pg8000",
#     username=db_user,
#     password=db_pass,
#     database=db_name,
#     query={"unix_sock": f"{unix_socket_path}/.s.PGSQL.5432"},
# )

# 資料庫連線 The Cloud SQL Python Connector


instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]
db_user = os.environ["DB_USER"]  # e.g. 'my-db-user'
db_pass = os.environ["DB_PASS"]  # e.g. 'my-db-password'
db_name = os.environ["DB_NAME"]  # e.g. 'my-database'
# iam_user = os.environ["IAM_USER"]
# secret_credentials = os.environ["SECRET_CREDENTIALS"]
ip_type = IPTypes.PUBLIC

# initialize Cloud SQL Python Connector object
connector = Connector()
def getconn() -> pg8000.dbapi.Connection:
    conn: pg8000.dbapi.Connection = connector.connect(
        instance_connection_name,
        "pg8000",
        user=db_user,
    # user=iam_user,
        password=db_pass,
        db=db_name,
    # credentials=secret_credentials,
    # enable_iam_auth=True,
        ip_type=ip_type,
    )
    return conn

# 設定 Userinfo 與 Conversationlog 兩個 API 的 request format
class Userinfo(BaseModel):
    start_date: str # yyyy-mm-dd
    end_date: str # yyyy-mm-dd

class Conversationlog(BaseModel):
    user_token: str

@app.post("/userinfo")
async def userinfo(date_range: Userinfo) -> dict:
    try:
        # pool = sqlalchemy.create_engine(db_url) # for UNIX Connector
        pool = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn) # for Cloud SQL Python Connector
        sql_tool = SQLTools(pool)
        vendor_token = os.environ.get("VENDOR_TOKEN")
        query_string = query_str.get_user_info_sql(vendor_token, date_range.start_date, date_range.end_date)
        user_info, col_list = sql_tool.read_sql(sqlstring=query_string, header_flg=True)
        user_info_dict = pd.DataFrame(user_info, columns=col_list).T.to_dict()
        return user_info_dict
    except Exception as error:
        raise error

@app.post("/conversationlog")
async def conversationlog(user: Conversationlog) -> dict: 
    try:
        conversationlog_logger.log_text('conversationlog start')
        start_time = time.time()
        # pool = sqlalchemy.create_engine(db_url) # for UNIX Connector
        pool = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn) # for Cloud SQL Python Connector
        sql_tool = SQLTools(pool)
        vendor_token = os.environ.get("VENDOR_TOKEN")
        query_string = query_str.get_conversation_log_sql(vendor_token, user.user_token)
        conversation_log, col_list = sql_tool.read_sql(sqlstring=query_string, header_flg=True)
        conversation_log_dict = pd.DataFrame(conversation_log, columns=col_list).T.to_dict()
        return conversation_log_dict
    except Exception as error:
        raise error


@app.websocket("/aicustservice/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        ## 儲存連線時間
        ws_conn_time = datetime.now()
        ## 連線資料庫, 取得 user_info 與 conversation_log 資料表欄位
        # pool = sqlalchemy.create_engine(db_url) # for UNIX Connector
        pool = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn) # for Cloud SQL Python Connector
        sql_tool = SQLTools(pool)
        user_info_col_list = sql_tool.get_table_column(schema_name='public', table_name='user_info_list')
        conversation_col_list = sql_tool.get_table_column(schema_name='public', table_name='user_conversation_log')
        vendor_token = os.environ.get("VENDOR_TOKEN")
        ## create unique user_token, and insert to user_info_list
        user_token = "choowe_1900-01-01 00:00:00_999"
        insert_data = (vendor_token, user_token, "1900-01-01 00:00:00.00000", "1900-01-01 00:00:00.00000")
        sql_tool.insert_data(
            schema_name='public', table_name='user_info_list',
            column_list=user_info_col_list, insert_data=insert_data
        )
        ## insert to user_conversation_log
        insert_data = (vendor_token, user_token, datetime.now(),
                       'AAAAA', 'BBBBB')
        sql_tool.insert_data(
            schema_name='public', table_name='user_conversation_log',
            column_list=conversation_col_list, insert_data=insert_data
        )
        while True:
            receive_text = await websocket.receive_text()
            ## update user_start_time to user_info_list
            sql_tool.update_data(
                schema_name='public', table_name='user_info_list',
                update_col='user_start_time', update_value=datetime.now(),
                token_value=vendor_token, user_value=user_token
            )
            ## 客戶輸入 1 可直接中斷連線
            if receive_text == '1':
                break

    except Exception as e:
        raise e

#edward add this#    
#edward add this#
    
def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of Postgres.
    Uses the Cloud SQL Python Connector package.
    """
    instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    ip_type = IPTypes.PUBLIC

    connector = Connector()

    def getconn() -> pg8000.dbapi.Connection:
        conn: pg8000.dbapi.Connection = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type,
        )
        return conn

    return sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)


pool = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)

class DataEntry(BaseModel):
    message: str

@app.post("/insertdata")
async def insert_data(data: DataEntry):
    try:
        with pool.connect() as conn:
            sql = sqlalchemy.text("""
            INSERT INTO test_table (message, created_at)
            VALUES (:message, NOW())
            """)
            conn.execute(sql, {"message": data.message})
        return {"status": "success", "message": "Data inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#edward add this#    
#edward add this#     


#    curl -X POST https://edward-zu-run-to-sql-prod-esjn3qpdsa-de.a.run.app/insertdata  -H "Content-Type: application/json" -d '{"message": "Hello, World!"}'

