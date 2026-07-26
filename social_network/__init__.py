# Условный импорт pymysql — только если установлен (нужен для MySQL)
# При использовании SQLite этот модуль не требуется
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
