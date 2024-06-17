import sqlalchemy

def get_user_info_sql(vendor_token, start_date, end_date):
    try:
        sqlstring = sqlalchemy.text(
            """
            SELECT
                vendor_token,
                user_token,
                user_start_time,
                user_end_time
            FROM user_info_list
            WHERE vendor_token = {token}
              AND (
                DATE(user_start_time) BETWEEN {s_dt} AND {e_dt}
                OR
                DATE(user_end_time) BETWEEN {s_dt} AND {e_dt}
              )
            """.format(
            token=vendor_token,
            s_dt=start_date,
            e_dt=end_date
            )
        )
        return sqlstring
    except Exception as error:
        raise error

def get_conversation_log_sql(vendor_token, user_token):
    try:
        sqlstring = sqlalchemy.text(
            """
            SELECT
                vendor_token,
                user_token,
                message_time,
                message,
                role
            FROM user_conversation_log
            WHERE vendor_token = {token}
              AND user_token = {user}
            """.format(
            token=vendor_token,
            user=user_token
            )
        )
        return sqlstring
    except Exception as error:
        raise error