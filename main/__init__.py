# see http://stackoverflow.com/a/21416007/931303
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
