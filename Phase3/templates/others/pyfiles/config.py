

"""
    This contains all config settings and values
"""


class Config():
    # DEBUG = False
    # TESTING = False

    def DevelopmentConfig():
        """
        Development configurations
        """
        params = {}
        params["MYSQL_HOST"] = '127.0.0.1'
        params["MYSQL_USER"] = 'root'
        params["MYSQL_PASSWORD"] = ''
        params["MYSQL_DB"] = 'quotation_formulator'  # can be any
        params["MYSQL_CURSORCLASS"] = "DictCursor"

        DEBUG = True

        return params


    def ProductionConfig():
        """
        Production configurations
        """
        MYSQL_DATABASE_USER = 'yourusername'
        MYSQL_DATABASE_PASSWORD = 'yourpassword'
        MYSQL_DATABASE_HOST = 'linktoyourdb' # eg to amazone db :- yourdbname.xxxxxxxxxx.us-east-2.rds.amazonaws.com
        MYSQL_DATABASE_DB = 'yourdbname'

        DEBUG = False