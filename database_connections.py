import pymysql

def connect_user_cred():
	connection = pymysql.connect(host='gif-project.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
								user='admin',
								password='mldtFSH8GKgRSOViqshD',
								db='gif_user_credentials',
								charset='utf8mb4',
								cursorclass=pymysql.cursors.DictCursor)
	return connection


def connect_meeprotect():
    connection = pymysql.connect(host='techdrive.xyz',
                                 user='techdrive_meprote',
                                 password='Webs_$#@!56',
                                 db='techdrive_meprotect',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

def connect_mobileprotection():
    connection = pymysql.connect(host='techdrive.xyz',
                                 user='techdrive_meprote',
                                 password='Webs_$#@!56',
                                 db='techdrive_mobileProtection',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

def connect_deltacore():
    connection = pymysql.connect(host='deltacore.xyz',
                                 user='techdrive_meprote',
                                 password='Webs_$#@!56',
                                 db='techdrive_meprotect',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

def connect_deltacoremobileprotection():
    connection = pymysql.connect(host='deltacore.xyz',
                                 user='techdrive_meprote',
                                 password='Webs_$#@!56',
                                 db='techdrive_mobileProtection',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection