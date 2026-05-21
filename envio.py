import time
import requests

# Configurações do bot
BOT_TOKEN = "5965310119:AAFbNw-r1UgaqMkDn0Ivx4-j-HBPgCKQgFU"
CHAT_ID = "-4666794010"

# Lista de links
links = [
    "https://www.pa3333.com/static/game/13CEE27A2BD93915479F049378CFFDD3.png",
    "https://www.pa3333.com/static/game/421D13C7ECD67604CEDBE44F88DD1F61.png",
    "https://www.pa3333.com/static/game/0299C06AED970473AE41D986B308CD09.png",
    "https://www.pa3333.com/static/game/DCA19FFA163054FEEF33432FAD5F9833.png",
    "https://www.pa3333.com/static/game/B7B2D5A8D1B4D64F0E89E293D4AC08EB.png",
    "https://www.pa3333.com/static/game/98C6F2C2287F4C73CEA3D40AE7EC3FF2.png",
    "https://www.pa3333.com/static/game/C2D2BC9253A4F95A06464C302C552FE8.png",
    "https://www.pa3333.com/static/game/17380DDB842E984302034E1BB66C24E4.png",
    "https://www.pa3333.com/static/game/1981E4A762B39858DC33F9EA28ED065A.png",
    "https://www.pa3333.com/static/game/1701CF909C49835D0C793C7A7EF82A5D.png",
    "https://www.pa3333.com/static/game/2A0270F3B3A57F49C195A7F2B0736564.png",
    "https://www.pa3333.com/static/game/3A170A9FE4F47EFA37D23AD521B9098E.png",
    "https://www.pa3333.com/static/game/6B5DFCF1F44C9D485DDA1902AC33C0A9.png",
    "https://www.pa3333.com/static/game/C0069D16731C2D1EEFF8F67ED560B89B.png",
    "https://www.pa3333.com/static/game/7866CC7FB5A03C016EFD4D506A451850.png",
    "https://www.pa3333.com/static/game/80D2B8BBB1D9FBB8AEC70C802CC67BAD.png",
    "https://www.pa3333.com/static/game/435C44C266BC0C05F7B6F48E7A454F1C.png",
    "https://www.pa3333.com/static/game/D5AC5A27C34EBFD7A1DBD16D5B99EDFB.png",
    "https://www.pa3333.com/static/game/F2A057FC73359A2781F0FD48F63D6FDE.png",
    "https://www.pa3333.com/static/game/19A1DE167122A18AF369C749F4E40A48.png",
    "https://www.pa3333.com/static/game/3C46A0407BE60A1F00731AB8E9575DF2.png",
    "https://www.pa3333.com/static/game/620726CCE3CBC8C574E5889CB404DA8C.png",
    "https://www.pa3333.com/static/game/C9E6E7B69F98F516A54CFE2C9E25FB3F.png",
    "https://www.pa3333.com/static/game/1F289CD1A244A837B3D946160B49E54D.png",
    "https://www.pa3333.com/static/game/B772D43B49BB57B596D0343C33BCFFEC.png",
    "https://www.pa3333.com/static/game/9634715CA7E046CDD0FC857CDC38DCB6.png",
    "https://www.pa3333.com/static/game/74BDEFAB9757A081606B181AC29F1DB2.png",
    "https://www.pa3333.com/static/game/88CB29DAAB6DD7AE3016B506C36E9F17.png",
    "https://www.pa3333.com/static/game/DD7650909D02EA03DD155714A731FEF3.png",
    "https://www.pa3333.com/static/game/8FBDBF5573B18FAE93736180F8D0197A.png",
    "https://www.pa3333.com/static/game/D742FFBECE435C9076FBA5F244396CF8.png",
    "https://www.pa3333.com/static/game/4864DAFB55D05D74897FDCE5DEE7FD22.png",
    "https://www.pa3333.com/static/game/EA66C06C1E1C05FA9F1AA39D98DC5BC1.png",
    "https://www.pa3333.com/static/game/B00BDAF8D970B7DF664953F63A698374.png",
    "https://www.pa3333.com/static/game/6AB5DBC886D46770A86E6CC0BE54A9D1.png",
    "https://www.pa3333.com/static/game/A514839C4971406FF865A3F340E4EA36.png",
    "https://www.pa3333.com/static/game/5A0B7222F0C5F9A7D569039911132B40.png",
    "https://www.pa3333.com/static/game/09E25C12765906F32FEFCA6A9F366E15.png",
    "https://www.pa3333.com/static/game/A5CB00D7C8FFFE5FB2C79C540A54817A.png",
    "https://www.pa3333.com/static/game/60274C1AC606DDDFAB591309CB5ACE78.png",
    "https://www.pa3333.com/static/game/A12F16C644039099699332E247F11EC0.png",
    "https://www.pa3333.com/static/game/C22C60349630D688CEF20A3FD708AD87.png",
    "https://www.pa3333.com/static/game/4D6237DF5AB8CC9E1268B8086182979D.png",
]

# Função para enviar mensagem
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            print(f"✅ Enviado: {text}")
        else:
            print(f"❌ Erro ao enviar: {r.text}")
    except Exception as e:
        print(f"⚠️ Erro: {e}")

# Enviar todos os links (um de cada vez com intervalo)
for link in links:
    send_message(link)
    time.sleep(3)  # tempo de espera entre envios (10 segundos)
