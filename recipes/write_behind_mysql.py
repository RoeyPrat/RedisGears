mydb = None
# addQuery = "insert into test_table values (%s, %s) ON DUPLICATE KEY UPDATE value=%s"
# deleteQuery = 'delete from test_table where test_table.key="%s"'

ADD_QUERY_KEY = '_add_query'
DEL_QUERY_KEY = '_delete_query'
TABLE_KEY = '_table'
KEY = '_key'

# MYSQL_CONFIG = {
#     'host': '172.31.52.0',
#     'user': 'demouser',
#     'password' : '*******',
#     'database' : 'test',
# }

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'demouser',
    'password' : '*******',
    'database' : 'test',
}

config = {
    'person:id':{
        'first_name':'first',
        'last_name':'last',
        'age':'age',
    },
    'car:license_id':{
        'color':'color',
        'model':'model',
    },
}

def Log(msg, prefix='RedisGears - '):
    msg = prefix + msg
    try:
        execute('debug', 'log', msg)
    except Exception:
        print(msg)

def Connect():
    import mysql.connector
    Log('connecting to database, host=%s, user=%s, password=********, database=%s' % (MYSQL_CONFIG['host'], MYSQL_CONFIG['user'], MYSQL_CONFIG['database']))
    mydb = mysql.connector.connect(host=MYSQL_CONFIG['host'], user=MYSQL_CONFIG['user'], passwd=MYSQL_CONFIG['password'], database=MYSQL_CONFIG['database'])
    return mydb

def PrepereQueries():
    for k,v in config.items():
        table, key = k.split(':')
        v[TABLE_KEY] = table
        v[KEY] = key
        if table is None or key is None:
            raise Exception('failed to create query for %s', str(k))

        # create insert query
        query = 'REPLACE INTO %s' % table
        values = [val for kk, val in v.items() if not kk.startswith('_')]
        values = [key] + values
        values.sort()
        query = '%s(%s) values(%s)' % (query, ','.join(values), ','.join(['%s' for a in values]))
        v[ADD_QUERY_KEY] = query

        # create delete query
        query = 'delete from %s where %s="%s"' % (table, key, '%s')
        v[DEL_QUERY_KEY] = query

def PrintAllQueries():
    for v in config.values():
        Log('add_query="%s", del_query="%s"' % (v[ADD_QUERY_KEY], v[DEL_QUERY_KEY]))

def GetStreamName(config):
    return '_%s-stream-{%s}' % (config[TABLE_KEY], hashtag())

def CreateStreamInserter(config):
    def AddToStream(r):
        keys = r['value'].keys()
        data = []
        for kInHash, kInDB in config.items():
            if kInHash.startswith('_'):
                continue
            if kInHash not in keys:
                msg = 'Could not find %s in hash %s' % (kInHash, r['key'])
                Log(msg)
                raise Exception(msg)
            data.append([kInDB, r['value'][kInHash]])
        data.append([config[KEY], r['key'].split(':')[1]])
        execute('xadd', GetStreamName(config), '*', *sum(data, []))
    return AddToStream

def CreateMySqlDataWriter(config):
    def WriteToMySql(r):
        global mydb
        if not mydb:
            mydb = Connect()
        try:
            mycursor = mydb.cursor()

            for x in r:
                vals = [(k, v) for k,v in x.items() if k != 'streamId']
                vals.sort()
                vals = tuple([a[1] for a in vals])
                mycursor.execute(config[ADD_QUERY_KEY], vals)
        except Exception as e:
            Log('got exception when writing to mysql, query="%s", error="%s"' % ((config[ADD_QUERY_KEY] % vals), str(e)))
            raise e
        finally:
            mydb.commit()
            mycursor.close()
    return WriteToMySql

def RegisterExecutions():
    for v in config.values():

        ## create the execution to write each changed key to stream
        GB('KeysReader', desc='add each changed key with prefix %s* to Stream' % v[TABLE_KEY]).\
        filter(lambda x: x['key'] != GetStreamName(v)).\
        foreach(CreateStreamInserter(v)).\
        register(mode='sync', regex='%s:*' % v[TABLE_KEY])

        ## create the execution to write each key from stream to mysql
        GB('StreamReader', desc='read from stream and write to mysql table %s' % v[TABLE_KEY]).\
        aggregate([], lambda a, r: a + [r], lambda a, r: a + r).\
        foreach(CreateMySqlDataWriter(v)).\
        count().\
        register(regex='_%s-stream-*' % v[TABLE_KEY], mode="async_local", batch=100, duration=4000)


PrepereQueries()

PrintAllQueries()

RegisterExecutions()