import pymysql.cursors

class Database:
    def __init__(self, host, user, password, db):
        self.__connection = pymysql.connect(
                            host=host,
                            user=user,
                            password=password,
                            db=db,
                            cursorclass=pymysql.cursors.DictCursor
                        )


    def insert_many(self, query, tuples):
        try:
            with self.__connection.cursor() as cursor: 
                cursor.executemany(query, tuples)
            self.__connection.commit()

        except Exception as error:
            self.__connection.rollback()
            print(f"Error al insertar registros: {error}")

    def insert_one(self, query, tuple):
        with self.__connection.cursor() as cursor: 
            cursor.execute(query, tuple)
        self.__connection.commit()

    def update(self, query, params):
        with self.__connection.cursor() as cursor: 
            cursor.execute(query, params)
        self.__connection.commit()

    def find_many(self, query):
        with self.__connection.cursor() as cursor: 
            cursor.execute(query)
            result = cursor.fetchall()
        self.__connection.commit()
        return result
    
    def find_one(self, query):
        with self.__connection.cursor() as cursor: 
            cursor.execute(query)
            result = cursor.fetchone()
        self.__connection.commit()
        return result
    

