# See e.g. http://stackoverflow.com/a/14076841/931303
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
