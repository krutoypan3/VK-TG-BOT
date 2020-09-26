import pyodbc

try:
    def create_connection():
        server = 'localhost\SQLEXPRESS'
        database = 'BotDB'
        username = 'sa'
        password = 'sa'
        driver = '{SQL Server}'
        conn = pyodbc.connect(
            'DRIVER=' + driver + ';SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        return conn

    con = create_connection()

    # Вставка СТРОКИ в ТАБЛИЦУ Table_1 в БД
    def sql_insert(conc2, entities):
        cursorObj3 = conc2.cursor()
        cursorObj3.execute('INSERT INTO Table_2(UserName, Password, vk_id, teleg_id) VALUES(?, ?, ?, ?)', entities)
        conc2.commit()


    # Обновление параметра в таблице Table_1
    def sql_update(con5, what_fetch, what_fetch_new):
        cursorObj1 = con5.cursor()
        cursorObj1.execute('UPDATE Table_2 SET ' + str(what_fetch) + ' = CAST(' + "'" + str(what_fetch_new) + "'"
                           + ' AS varchar)')
        con5.commit()


    # Получение параметров из таблицы Table_1
    def sql_fetch(conc, what_return, vk_id):
        cursorObj1 = conc.cursor()
        cursorObj1.execute('SELECT ' + str(what_return) + ' FROM Table_2 WHERE vk_id = CAST(' + "'" + str(vk_id) + "'" + ' AS varchar)')
        rows = cursorObj1.fetchall()
        if len(rows) == 0:
            return None
        return rows[0][0]


    # Получение параметров из таблицы Table_1
    def sql_fetch_user(conc, what_return, UserName):
        cursorObj1 = conc.cursor()
        cursorObj1.execute('SELECT ' + str(what_return) + ' FROM Table_2 WHERE UserName = CAST(' + "'" + str(UserName) + "'" + ' AS varchar)')
        rows = cursorObj1.fetchall()
        if len(rows) == 0:
            return None
        return rows[0][0]




except Exception as e:
    print("Возникла ошибка: " + str(e))
