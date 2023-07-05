from flask import Flask


import gspread
import pandas as pd
import datetime

credentials = {
  "type": "service_account",
  "project_id": "tidy-gravity-349514",
  "private_key_id": "2d2d47fb47ddfb4ec6c2fa7beacdd8fe785f998e",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC0Bg21E6axY3fb\nww1iZnNG7zEc0D6Wy3lqsCSgQBnyb6PQcuMfAwK+4ZPDWh0dyGJ3nE6lHnn/IBrg\nsIFxBbUh5oZOwfaN1A9GU2/QDNiUNeJ3i7ba4mN1URqUpixQZFXYJ3jGN1bNJevl\npfkXXMx+9o0qXN5ZHKLso7K36WFZZdzRcWVDtyQskmE6kyVGUAQak/dWY0ZVMYFG\nsa/qnxvfRz57LrowzDFaenv0yp6/6vL5jyACoO/7BuJu36l43QLpDj9dC8dnlgO0\nZt05TjikSEzi/FnGQrK6BBYIZUdwxGqvFMyehbp/KV0YN1d9tvYnc80uSSkUzsYD\n283z6GD1AgMBAAECggEAA44gDKyp7NRkTFJ+i+wuiB7WpzVEmylDCVSXsJN7f7Jt\nN4NhUV43mmnth1za+NjZeve7BN9EdQGfDkNmFwOQF26MRfdmJVhkAdVJfsAWMd0b\njxVTA+EXKjyzC+75LpBAsr9azv1OSUhfr34W3HuAbVx0nrrNSFC8tfQopiGlgsSr\n4MqrHdR+qXaWHof1H4ypYVY8uWSd5bXXJ/H4joNcpyIQ2KyJSpAmhuXEDAu6eaKA\nNwM6w43ModnaP+pWtAoiVSTlnsy5Eaw2c0zCrfqXq83Zft0uZMPRU5IWpYBArV4C\neF7znLal8fyNyAeMbjFQbOq6Xwxm2C+WFUedDUAl+QKBgQD7rcjdFxpCcm7Llsso\nqOIDaKmoXF3dzANciUULJleu1Z+uwXd5caRpStRrgIONZeEqqCHDSLVaU4QHg4nN\nOUA38NBcN4Q/G87n/9Fw+D9AbbYDKTrPFDFgN/KcyyXLnlfY6oNBXeaqhTiIxokD\nHV1m7Xt2monPr5ixt2k9w9maqQKBgQC3HVHQ0NysVHifD7bYw0BsmBRUF/gyhZKm\nvE+3HZnTTNzSlUt1vKUePflyc26S4xFHczZR1zs1/UJztvNusUeRNQTrKv/3xpqg\n+COxb6Kx6pzo6SSjFbdOYFxMEv0WU/HeMODdQahggL1/TIW9T1cc89IB3WwyQ3Nx\nPZ+L0EivbQKBgBB2ksAbpcUY9TRuHcYAHiC49PglaqJ6mPGxrQmIrY2rPbHRx/3y\nuB2HHpQVqQVT18HRk7vRgsNw2R8gtJ/vEctW/lo563WxXPyCGHI6WvDc/F4CkW1A\nVeaEYmNtSoCiT/7JgGKDQPaAlm0kB4xjnFuCR2Q/waoLQ4LEi6bVq+NZAoGAOEOZ\nBQl4FLdrzKv+acIsxHFCJcirqZJjSjooYEKHJmbCny3iXs3VCmLOh70yJ43/nC2p\nbiIs/lzQE1AOol90dwiMd1niBpcOohE8nmOH4RUOm34vlLCyfzGaioF3JGossjHg\nlft7qhNEpp2zpkR/ptTAHXSUrykMiqn9oO8htk0CgYBA3yB9DeatlSe9c3yUhzhe\nBeDEaOtXF7Mu/mR/AEzF4+UMI4g9syIQ40M3uEedBdgw2tmO2+HRl8n8giacLzok\nQJN3AE7zIxaRg4XwZ5XdoYtEgaEHHOA0iQv4uFtOwzyrRnJUHCw8lKcl238Cj1ek\nM7UmX5im0Vs7sDU5KDcv+g==\n-----END PRIVATE KEY-----\n",
  "client_email": "eys-445@tidy-gravity-349514.iam.gserviceaccount.com",
  "client_id": "106310523143023000697",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/eys-445%40tidy-gravity-349514.iam.gserviceaccount.com"
}

gc = gspread.service_account_from_dict(credentials)
gs = gc.open("ABLExR-DATA")
wk = gs.get_worksheet(0)



def get_data():
    return pd.DataFrame(wk.get_all_records())

def add_record(sesionId, reactionTime):
    ethnicity = int(sesionId / 1000)
    id = sesionId % 1000
    now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    record = [id,ethnicity,reactionTime, now]
    df.loc[len(df)] = record
    wk.update([df.columns.values.tolist()] + df.values.tolist())

df = get_data()


app = Flask(__name__)

@app.route("/")
def index():
    return "Hello ABLExR!"


@app.route("/case3/<sesionId>/<reactionTime>")
def reaction(sesionId, reactionTime):
    add_record(int(sesionId), int(reactionTime))
    # TODO the method will return the msg to display on the screen
    return "Avg. Intervention Time: 12.6s"



@app.route("/case3/add_sesion/<sesionId>/<ethnicity>/<descripion>")
def add_session(sesionId, ethnicity, descripion=""):  
    wk2 = gs.get_worksheet(1)
    df2 = pd.DataFrame(wk2.get_all_records())
    record = [sesionId,ethnicity,descripion]
    df2.loc[len(df2)] = record
    wk2.update([df2.columns.values.tolist()] + df2.values.tolist())
    return "OK"


@app.route("/case3/last_session")
def last_session():  
    wk2 = gs.get_worksheet(1)
    df = wk2.get_all_records()
    sessionId = int(df[-1]["ethnicity"]) * 1000 +  int(df[-1]["sesionId"])
    return str(sessionId)






