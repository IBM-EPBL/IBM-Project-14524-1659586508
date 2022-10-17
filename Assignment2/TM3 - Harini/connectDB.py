import ibm_db

try:
    conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=125f9f61-9715-46f9-9399-c8177b21803b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30426;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;PROTOCOL=TCPIP;UID=str00116;PWD=fpvVNC88XonuES12;", "", "")
    print("Connected to database")
    
except:
    print("Failed to connect: ", ibm_db.conn_errormsg())