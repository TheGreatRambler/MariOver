from anynet import tls
from nintendo import switch
from nintendo.switch import dauth, dragons
from anynet import tls

info = switch.ProdInfo(
    switch.load_keys("ConsoleData/prod.keys"), "ConsoleData/PRODINFO.dec"
)

with open("cert.pem", "wb") as cert_file:
    cert_file.write(info.get_tls_cert().encode(tls.TYPE_PEM))

with open("pkey.pem", "wb") as cert_file:
    cert_file.write(info.get_tls_key().encode(tls.TYPE_PEM))
