import sqlite3

# 1. 连接数据库 (如果不存在会自动创建一个 example.db 文件)
conn_2 = sqlite3.connect('courseinformation.db')
cursor_2 = conn_2.cursor()

# 2. 创建一张表 (如果不存在)
# 假设我们要存用户信息：姓名(name)和年龄(age)
cursor_2.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fileid TEXT UNIQUE NOT NULL,
        note TEXT NOT NULL
    )
''')



# 4. 执行插入操作
# 注意：SQL语句中的 ? 是占位符，防止恶意输入破坏数据库
cursor_2.execute(
    "INSERT INTO users (fileid, note) VALUES (?, ?)", 
    (user_fileid, user_note)
)

# 5. 提交事务 (这一步非常重要！)
conn_2.commit()

# 6. 关闭连接
conn_2.close()
print("数据插入成功！")



def new_table():
    conn_2 = sqlite3.connect('courseinformation.db')
    cursor_2 = conn_2.cursor()
    cursor_2.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fileid TEXT UNIQUE NOT NULL,
            note TEXT NOT NULL
            -- ⚠️ 注意：这里去掉了最后多余的逗号
        )
    ''')
    conn_2.commit()
    conn_2.close()