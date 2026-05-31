import csv
from collections import Counter

# =========================================================
# ESTATÍSTICAS ACESSÓRIO
# =========================================================

acessorio_wins = 0
acessorio_loss = 0

ultima_previsao_acessorio = None
ultimo_codigo_processado = None

# =========================================================
# CÓDIGOS
# =========================================================

CODIGOS_CHAPEU = {
    "B7B2D5A8D1B4D64F0E89E293D4AC08EB", "5A0B7222F0C5F9A7D569039911132B40",
    "DD7650909D02EA03DD155714A731FEF3", "3A170A9FE4F47EFA37D23AD521B9098E",
    "D742FFBECE435C9076FBA5F244396CF8", "60274C1AC606DDDFAB591309CB5ACE78",
    "9B1138C4B04769111A3756E7CC6E263E", "C2D2BC9253A4F95A06464C302C552FE8",
    "1701CF909C49835D0C793C7A7EF82A5D", "620726CCE3CBC8C574E5889CB404DA8C",
    "6B5DFCF1F44C9D485DDA1902AC33C0A9", "A5CB00D7C8FFFE5FB2C79C540A54817A"
   
}

CODIGOS_OCULOS = {
    "A4385FDA98A439AEDE464B18924ABAEA", "D5AC5A27C34EBFD7A1DBD16D5B99EDFB",
    "7866CC7FB5A03C016EFD4D506A451850", "0DD954EA204F19A1B391B7828491927B",
    "4D6237DF5AB8CC9E1268B8086182979D", "13CEE27A2BD93915479F049378CFFDD3",
    "FAE594628F003E7D8250252BAA6A83B2", "F2A057FC73359A2781F0FD48F63D6FDE",
    "4864DAFB55D05D74897FDCE5DEE7FD22", "88CB29DAAB6DD7AE3016B506C36E9F17",
    "C22C60349630D688CEF20A3FD708AD87", "C0069D16731C2D1EEFF8F67ED560B89B"

}

CODIGOS_CHIFRE = {
    "98C6F2C2287F4C73CEA3D40AE7EC3FF2", "DCA19FFA163054FEEF33432FAD5F9833",
    "B772D43B49BB57B596D0343C33BCFFEC", "A12F16C644039099699332E247F11EC0",
    "6AB5DBC886D46770A86E6CC0BE54A9D1", "435C44C266BC0C05F7B6F48E7A454F1C",
    "2F5BB7747EFDA0546636FB385A3FA593", "1981E4A762B39858DC33F9EA28ED065A",
    "17380DDB842E984302034E1BB66C24E4", "2A0270F3B3A57F49C195A7F2B0736564",
    "3C46A0407BE60A1F00731AB8E9575DF2", "80D2B8BBB1D9FBB8AEC70C802CC67BAD"
    
}

CODIGOS_SEM_ACESSORIO = {
    "A514839C4971406FF865A3F340E4EA36", "C9E6E7B69F98F516A54CFE2C9E25FB3F",
    "421D13C7ECD67604CEDBE44F88DD1F61", "19A1DE167122A18AF369C749F4E40A48",
    "B00BDAF8D970B7DF664953F63A698374", "EA66C06C1E1C05FA9F1AA39D98DC5BC1",
    "1F289CD1A244A837B3D946160B49E54D", "8FBDBF5573B18FAE93736180F8D0197A",
    "74BDEFAB9757A081606B181AC29F1DB2", "0299C06AED970473AE41D986B308CD09",
    "9634715CA7E046CDD0FC857CDC38DCB6", "09E25C12765906F32FEFCA6A9F366E15"
    
}
# =========================================================
# IDENTIFICAR ACESSÓRIO
# =========================================================

def identificar_acessorio(codigo):

    if not codigo:
        return "DESCONHECIDO"

    codigo = str(codigo).strip().upper()

    if codigo in CODIGOS_CHAPEU:
        return "CHAPEU"
    if codigo in CODIGOS_OCULOS:
        return "OCULOS"
    if codigo in CODIGOS_CHIFRE:
        return "CHIFRE"
    if codigo in CODIGOS_SEM_ACESSORIO:
        return "SEM ACESSORIO"

    return "DESCONHECIDO"

# =========================================================
# HISTÓRICO
# =========================================================

def carregar_historico(csv_file="sequencias.csv"):

    historico = []

    try:
        with open(csv_file, "r", encoding="utf-8") as file:
            reader = list(csv.DictReader(file))

            if reader and not reader[-1].get("Codigo"):
                reader = reader[:-1]

            for row in reader:

                codigo = row.get("Codigo", "").strip().upper()

                if not codigo:
                    continue

                historico.append(codigo)

    except Exception as e:
        print(f"⚠️ Erro CSV: {e}")

    return historico

# =========================================================
# PADRÕES
# =========================================================

def gerar_padroes(historico, janela=4):

    padroes = {}

    if len(historico) < janela + 1:
        return padroes

    for i in range(len(historico) - janela):

        seq = tuple(historico[i:i + janela])
        prox = historico[i + janela]

        padroes.setdefault(seq, []).append(prox)

    return padroes

# =========================================================
# PREVISÃO
# =========================================================

def prever_proximo_acessorio():

    global ultima_previsao_acessorio

    historico = carregar_historico()

    if len(historico) < 10:
        return None

    votos = []
    pesos = {7:5, 6:4, 5:3, 4:2}

    for janela in [7,6,5,4]:

        if len(historico) < janela + 1:
            continue

        padroes = gerar_padroes(historico, janela)

        seq = tuple(historico[-janela:])

        if seq not in padroes:
            continue

        proximos = padroes[seq]

        contador = Counter(proximos)

        pred = contador.most_common(1)[0][0]

        taxa = contador[pred] / len(proximos)

        if taxa < 0.65:
            continue

        votos.extend(
            [pred] * int(
                taxa * pesos[janela] * 20
            )
        )

    if not votos:
        return None

    final = Counter(votos)

    acessorio_previsto = (
        final.most_common(1)[0][0]
    )

    confianca = (
        final[acessorio_previsto]
        / len(votos)
    ) * 100

    if confianca < 75:
        return None

    ultima_previsao_acessorio = (
        acessorio_previsto
    )

    return {
        "acessorio": acessorio_previsto,
        "confianca": round(
            confianca,
            2
        )
    }
# =========================================================
# VALIDAÇÃO (CORRETA POR CÓDIGO REAL)
# =========================================================

def processar_validacao_acessorio():

    global acessorio_wins, acessorio_loss
    global ultima_previsao_acessorio, ultimo_codigo_processado

    historico = carregar_historico()

    if len(historico) < 2:
        return

    codigo_real = historico[-1]

    if ultimo_codigo_processado == codigo_real:
        return

    ultimo_codigo_processado = codigo_real

    def tipo(codigo):

        if codigo in CODIGOS_CHAPEU:
            return "CHAPEU"
        if codigo in CODIGOS_OCULOS:
            return "OCULOS"
        if codigo in CODIGOS_CHIFRE:
            return "CHIFRE"
        if codigo in CODIGOS_SEM_ACESSORIO:
            return "SEM ACESSORIO"

        return None

    real = tipo(codigo_real)

    if not ultima_previsao_acessorio or not real:
        return

    if real == ultima_previsao_acessorio:
        acessorio_wins += 1
        print("🎩 WIN ACESSÓRIO")
    else:
        acessorio_loss += 1
        print("🎩 LOSS ACESSÓRIO")

# =========================================================
# RELATÓRIO
# =========================================================

def obter_resultado_acessorio():

    total = acessorio_wins + acessorio_loss

    taxa = (acessorio_wins / total * 100) if total else 0

    return {
        "wins": acessorio_wins,
        "loss": acessorio_loss,
        "taxa": round(taxa, 2)
    }