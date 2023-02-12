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
            if cursor.rowcount==1:
                Client = cursor.fetchone()
                return Client


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

def Start_transaction(idT, status, cp, start_time, con_id, met_start):
    sql_insert_query = """ INSERT INTO public."Transaction" ("Client","Status","CP","Start_time","Connector_id","Meter_start") VALUES (%s,%s,%s,%s,%s,%s)"""
    id = idT
    Status=status
    CP=cp
    Start_time=start_time
    Connector_id=con_id
    Meter_start=met_start
    return sql_insert_query, id, Status, CP, Start_time, Connector_id, Meter_start
def Stop_transaction(stop_time,meter_stop,idT):
    sql_insert_query = """ UPDATE public."Transaction" SET "Stop_time"=%s, "Meter_stop"=%s WHERE "id"=%s """
    Stop_time=stop_time
    Meter_stop=meter_stop
    id=idT
    return sql_insert_query,Stop_time,Meter_stop,id


def Insert_client(client,token,groupid):
    sql_insert_query = """ INSERT INTO public."Client" ("Name","IdTag","ParentIdTag") VALUES (%s,%s,%s)"""
    cl = client
    tag = token
    parentid=groupid
    return sql_insert_query, cl, tag,parentid
def Insert_cp(vendor,model,ip,cp_tag):
    sql_insert_query = """ INSERT INTO public."ChargePoints" ("Vendor","Model","IP","CP") VALUES (%s,%s,%s,%s)"""
    Vendor = vendor
    Model = model
    Ip = ip
    Cp_tag = cp_tag
    return sql_insert_query, Vendor, Model, Ip, Cp_tag

def Insert_cp_connector(cp_tag,conn_1,conn_2,conn_3):
    sql_insert_query = """ INSERT INTO public."Connector" ("CP_tag","Connector_1","Connector_2","Connector_3") VALUES (%s,%s,%s,%s)"""
    Cp_tag = cp_tag
    Conn_1 = conn_1
    Conn_2 = conn_2
    Conn_3 = conn_3
    return sql_insert_query,Cp_tag, Conn_1, Conn_2, Conn_3,

# def Get_Trans(tag:str):
#     connection = psycopg2.connect(
#         host=host,
#         user=user,
#         password=password,
#         database=db_name)
#     cursor = connection.cursor()
#     id = tag
#     cursor.execute('SELECT id FROM public."Transaction" WHERE "Client"=%s ORDER BY id DESC LIMIT 1', (id,))
#     c = cursor.fetchone()
#     return c[0]

def Get_Trans(id_tag):
    id=id_tag
    sql_insert_query ="""SELECT id FROM public."Transaction" WHERE "Client"=%s ORDER BY id DESC LIMIT 1"""
    return sql_insert_query, id

# def Get_Connector(tag:str):
#     connection = psycopg2.connect(
#         host=host,
#         user=user,
#         password=password,
#         database=db_name)
#     cursor = connection.cursor()
#     CP_tag = tag
#     cursor.execute('SELECT "Connector_1","Connector_2","Connector_3" FROM public."Connector" WHERE "CP_tag"=%s', (CP_tag,))
#     c = cursor.fetchone()
#     return c

def Get_Connector(cp_tag):
    CP_tag = cp_tag
    sql_insert_query = """SELECT "Connector_1","Connector_2","Connector_3" FROM public."Connector" WHERE "CP_tag"=%s"""
    return sql_insert_query, CP_tag

# i="Test"
# Transz=connect(Stop_transaction('111',1,23))
# Client=connect(Get_Client())
# print(Client)
# for row in Client:
#     print(row[0])
#     print(row[1])
#     print(row[2])
# connect(Insert(1))
# Trans = connect(Get_Trans('AA 12345'))
# print(Trans[0])
# Conn=connect(Get_Connector('Test'))
# print(Conn)

