from novaclient.v1_1 import client
from intern import utils

user_conn = None
admin_conn = None
def nova(admin=False):
    CONF = utils.load_config("global")
    if admin:
        global admin_conn
        if not admin_conn:
            CREDS = utils.load_config("admin")
            admin_conn = client.Client(CREDS.get('user'),
                                      CREDS.get('password'),
                                      CREDS.get('tenant'),
                                      CONF.get('auth_endpoint'))
        return admin_conn
    else:
        global user_conn
        if not user_conn:
            CREDS = utils.load_config("user")
            user_conn = client.Client(CREDS.get('user'),
                                      CREDS.get('password'),
                                      CREDS.get('tenant'),
                                      CONF.get('auth_endpoint'))
        return user_conn

