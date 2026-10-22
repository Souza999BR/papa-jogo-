
"""Mapa oficial PA3333: numero, cor e os quatro códigos de imagem."""

NUMEROS = {
    1: {
        "cor": "VERMELHO",
        "SEM ACESSORIO": "EA66C06C1E1C05FA9F1AA39D98DC5BC1",
        "CHAPEU": "3A170A9FE4F47EFA37D23AD521B9098E",
        "CHIFRE": "98C6F2C2287F4C73CEA3D40AE7EC3FF2",
        "OCULOS": "13CEE27A2BD93915479F049378CFFDD3",
    },
    3: {
        "cor": "VERMELHO",
        "SEM ACESSORIO": "C9E6E7B69F98F516A54CFE2C9E25FB3F",
        "CHAPEU": "B7B2D5A8D1B4D64F0E89E293D4AC08EB",
        "CHIFRE": "B772D43B49BB57B596D0343C33BCFFEC",
        "OCULOS": "7866CC7FB5A03C016EFD4D506A451850",
    },
    5: {
        "cor": "VERMELHO",
        "SEM ACESSORIO": "19A1DE167122A18AF369C749F4E40A48",
        "CHAPEU": "60274C1AC606DDDFAB591309CB5ACE78",
        "CHIFRE": "DCA19FFA163054FEEF33432FAD5F9833",
        "OCULOS": "0DD954EA204F19A1B391B7828491927B",
    },
    7: {
        "cor": "VERMELHO",
        "SEM ACESSORIO": "A514839C4971406FF865A3F340E4EA36",
        "CHAPEU": "D742FFBECE435C9076FBA5F244396CF8",
        "CHIFRE": "6AB5DBC886D46770A86E6CC0BE54A9D1",
        "OCULOS": "D5AC5A27C34EBFD7A1DBD16D5B99EDFB",
    },
    9: {
        "cor": "VERMELHO",
        "SEM ACESSORIO": "B00BDAF8D970B7DF664953F63A698374",
        "CHAPEU": "5A0B7222F0C5F9A7D569039911132B40",
        "CHIFRE": "435C44C266BC0C05F7B6F48E7A454F1C",
        "OCULOS": "A4385FDA98A439AEDE464B18924ABAEA",
    },
    11: {
        "cor": "VERMELHO",
        "SEM ACESSORIO": "421D13C7ECD67604CEDBE44F88DD1F61",
        "CHAPEU": "DD7650909D02EA03DD155714A731FEF3",
        "CHIFRE": "A12F16C644039099699332E247F11EC0",
        "OCULOS": "4D6237DF5AB8CC9E1268B8086182979D",
    },
    2: {
        "cor": "AZUL",
        "SEM ACESSORIO": "8FBDBF5573B18FAE93736180F8D0197A",
        "CHAPEU": "620726CCE3CBC8C574E5889CB404DA8C",
        "CHIFRE": "3C46A0407BE60A1F00731AB8E9575DF2",
        "OCULOS": "C22C60349630D688CEF20A3FD708AD87",
    },
    4: {
        "cor": "AZUL",
        "SEM ACESSORIO": "74BDEFAB9757A081606B181AC29F1DB2",
        "CHAPEU": "6B5DFCF1F44C9D485DDA1902AC33C0A9",
        "CHIFRE": "2F5BB7747EFDA0546636FB385A3FA593",
        "OCULOS": "4864DAFB55D05D74897FDCE5DEE7FD22",
    },
    6: {
        "cor": "AZUL",
        "SEM ACESSORIO": "0299C06AED970473AE41D986B308CD09",
        "CHAPEU": "A5CB00D7C8FFFE5FB2C79C540A54817A",
        "CHIFRE": "17380DDB842E984302034E1BB66C24E4",
        "OCULOS": "FAE594628F003E7D8250252BAA6A83B2",
    },
    8: {
        "cor": "AZUL",
        "SEM ACESSORIO": "9634715CA7E046CDD0FC857CDC38DCB6",
        "CHAPEU": "1701CF909C49835D0C793C7A7EF82A5D",
        "CHIFRE": "1981E4A762B39858DC33F9EA28ED065A",
        "OCULOS": "F2A057FC73359A2781F0FD48F63D6FDE",
    },
    10: {
        "cor": "AZUL",
        "SEM ACESSORIO": "09E25C12765906F32FEFCA6A9F366E15",
        "CHAPEU": "C2D2BC9253A4F95A06464C302C552FE8",
        "CHIFRE": "80D2B8BBB1D9FBB8AEC70C802CC67BAD",
        "OCULOS": "88CB29DAAB6DD7AE3016B506C36E9F17",
    },
    12: {
        "cor": "AZUL",
        "SEM ACESSORIO": "1F289CD1A244A837B3D946160B49E54D",
        "CHAPEU": "9B1138C4B04769111A3756E7CC6E263E",
        "CHIFRE": "2A0270F3B3A57F49C195A7F2B0736564",
        "OCULOS": "C0069D16731C2D1EEFF8F67ED560B89B",
    },
}

# Converte qualquer um dos quatro códigos de imagem para seu número.
CODIGO_PARA_NUMERO = {
    codigo: numero
    for numero, info in NUMEROS.items()
    for chave, codigo in info.items()
    if chave != "cor"
}


def normalizar_codigo(codigo):
    return str(codigo or "").strip().upper().removesuffix(".PNG")


def numero_por_codigo(codigo):
    return CODIGO_PARA_NUMERO.get(normalizar_codigo(codigo))


def cor_por_numero(numero):
    try:
        numero = int(numero)
    except (TypeError, ValueError):
        return None

    info = NUMEROS.get(numero)
    return info["cor"] if info else None


def cor_por_codigo(codigo):
    numero = numero_por_codigo(codigo)
    return cor_por_numero(numero) if numero is not None else None


def codigo_sem_acessorio(numero):
    try:
        numero = int(numero)
    except (TypeError, ValueError):
        return None

    info = NUMEROS.get(numero)
    return info["SEM ACESSORIO"] if info else None


def url_imagem(codigo):
    codigo = normalizar_codigo(codigo)
    if not codigo:
        return None

    return f"https://www.pa3333.com/static/game/{codigo}.png"
