import psycopg2
from config import host, user, password, db_name

def connect(*args):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name)
        cursor = connection.cursor()
        len = args[0]
        if isinstance(len, str):
            cursor.execute(*args)
            connection.commit()
            if cursor.rowcount > 1:
                Client=cursor.fetchall()
                return Client
            else:
                Client=cursor.fetchone()
                return Client[0]
        else:
            sql = args[0]
            cursor.execute(sql[0], sql[1:])
            connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Failed inserting record into mobile table {}".format(error))

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

def Get_Client():
    sql_insert_query = """ SELECT * FROM public."Client" """
    return sql_insert_query

def Get_ChargePoint():
    sql_insert_query = """ SELECT * FROM public."ChargePoints" """
    return sql_insert_query

def Insert_transaction(idT):
    sql_insert_query = """ INSERT INTO public."Transaction" ("Client") VALUES (%s)"""
    id = idT
    return sql_insert_query, id

def Insert_client(client,token):
    sql_insert_query = """ INSERT INTO public."Client" ("Name","IdTag") VALUES (%s,%s)"""
    cl = client
    tag = token
    return sql_insert_query, cl, tag

def Get_Trans(tag:str):
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name)
    cursor = connection.cursor()
    id = tag
    cursor.execute('SELECT id FROM public."Transaction" WHERE "Client"=%s ORDER BY id DESC LIMIT 1', (id,))
    c = cursor.fetchone()
    return c[0]

# i="AA 12345"
# Client=Get_Trans(i)
# print(Client)
# for row in Client:
#     print(row[0])
#     print(row[1])
#     print(row[2])
# connect(Insert(1))
# Trans = connect(Get_Trans())
# print(Trans)


