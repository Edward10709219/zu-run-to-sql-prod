## 此段 DDL 會先在 local 端執行完成
## local 端連線方式：./cloud-sql-proxy --credentials-file
CREATE TABLE user_conversation_log(  
    vendor_token TEXT,
    user_token TEXT,
    message_time TIMESTAMP WITHOUT TIME ZONE,
    message TEXT,
    role TEXT
);

CREATE TABLE user_info_list(  
    vendor_token TEXT,
    user_token TEXT,
    user_start_time TIMESTAMP WITHOUT TIME ZONE,
    user_end_time TIMESTAMP WITHOUT TIME ZONE
);
