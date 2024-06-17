import time

from typing import List
import sqlalchemy

class SQLTools:
    """
        A class used to provide ETL process and generate SQL statment
    """

    def __init__(self, pool: sqlalchemy.engine.base.Engine):
        self.pool = pool

    def read_sql(self, sqlstring, header_flg: bool) -> tuple:
        """read SQL statment
        - conn: A connection of DB
        - sqlstring: A composed SQL statment
        - header_flg: return header or not
        - Returns a tuple:: result of select statment and header(optional)
        """
        try:
            start_time = time.time()
            with self.pool.connect() as conn:
                conn_exe = conn.execute(sqlstring)
                result = conn_exe.fetchall()
                col_list = list(conn_exe.keys())
                read_cnt = conn_exe.rowcount
            end_time = time.time()
            execution_time = end_time - start_time
            msg = f"""
                read_sql is success,
                read {read_cnt} data,
                exe_time: {execution_time}秒
            """
            if header_flg:
                return result, col_list
            return result
        except Exception as error:
            raise error

    def get_table_column(self, schema_name: str, table_name: str) -> List:
        """get table's column
        """
        try:
            start_time = time.time()
            result_list = []
            sqlstring = sqlalchemy.text(
                """
                select column_name
                from information_schema.columns
                where table_schema='{s_name}'
                and table_name='{t_name}'
                order by ordinal_position;
                """.format(
                    s_name=schema_name,
                    t_name=table_name
                )
            )
            with self.pool.connect() as conn:
                conn_exe = conn.execute(sqlstring)
                result = conn_exe.fetchall()
            for item in result:
                result_list.append(item[0])
            end_time = time.time()
            execution_time = end_time - start_time
        except Exception as error:
            raise error
        else:
            return result_list

    def insert_data(self, schema_name: str, table_name: str,
                    column_list: List, insert_data: tuple):
        """insert data statment
        """
        try:
            start_time = time.time()
            column_string = ", ".join(column_list)
            s_string = ", ".join([':'+i for i in column_list])
            sqlstring = sqlalchemy.text(
                """
                insert into {s_name}.{t_name}({c_str})
                values ({s_str});
                """.format(
                    s_name=schema_name,
                    t_name=table_name,
                    c_str=column_string,
                    s_str=s_string
                )
            )
            with self.pool.connect() as conn:
                insert_data_dict = dict(zip(column_list, insert_data))
                conn_exe = conn.execute(sqlstring, parameters=insert_data_dict)
                conn.commit()
                insert_cnt = conn_exe.rowcount
            end_time = time.time()
            execution_time = end_time - start_time
            msg = f"""
                insert_data to {schema_name}.{table_name} success,
                insert {insert_cnt} data to db,
                exe_time: {execution_time}秒
            """
        except Exception as error:
            raise error
        else:
            return sqlstring

    def update_data(self, schema_name: str, table_name: str,
                    update_col: str, update_value: str,
                    token_value: str, user_value: str):
        """update data statment
        """
        try:
            start_time = time.time()
            sqlstring = sqlalchemy.text(
                """
                update {s_name}.{t_name} set {u_col} = {up_value}
                where vendor_token = {t_value}
                  and user_token = {u_value};
                """.format(
                    s_name=schema_name,
                    t_name=table_name,
                    u_col=update_col,
                    up_value=update_value,
                    t_value=token_value,
                    u_value=user_value
                )
            )
            with self.pool.connect() as conn:
                conn_exe = conn.execute(sqlstring)
                conn.commit()
                update_cnt = conn_exe.rowcount
            end_time = time.time()
            execution_time = end_time - start_time
            msg = f"""
                update_data {update_col} to {update_value} success,
                update {update_cnt} rows,
                exe_time: {execution_time}秒
            """
        except Exception as error:
            self.conn.rollback()
            raise error