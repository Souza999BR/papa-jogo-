import csv
from collections import Counter, defaultdict
from datetime import datetime

# =========================================================
# ESTATÍSTICAS ACESSÓRIO
# =========================================================

acessorio_wins = 0
acessorio_loss = 0

ultima_previsao_acessorio = None
ultimo_codigo_processado = None
ultimo_reset_hora = None

# =========================================================
# CACHE + PESOS DINÂMICOS
# =========================================================

CACHE_PADROES = {}
PESOS_DINAMICOS = defaultdict(lambda: 1.0)

PROBABILIDADES = defaultdict(lambda: defaultdict(lambda: 1))


# =========================================================
# MAPA POR COR (IMAGENS)
# =========================================================

CODIGOS_AZUL = {
    "CHAPEU": [
        "9B1138C4B04769111A3756E7CC6E263E", "C2D2BC9253A4F95A06464C302C552FE8",
        "1701CF909C49835D0C793C7A7EF82A5D", "620726CCE3CBC8C574E5889CB404DA8C",
        "6B5DFCF1F44C9D485DDA1902AC33C0A9", "A5CB00D7C8FFFE5FB2C79C540A54817A"
    ],

    "OCULOS": [
        "FAE594628F003E7D8250252BAA6A83B2", "F2A057FC73359A2781F0FD48F63D6FDE",
        "4864DAFB55D05D74897FDCE5DEE7FD22", "88CB29DAAB6DD7AE3016B506C36E9F17",
        "C22C60349630D688CEF20A3FD708AD87", "C0069D16731C2D1EEFF8F67ED560B89B"
    ],

    "CHIFRE": [
        "2F5BB7747EFDA0546636FB385A3FA593", "1981E4A762B39858DC33F9EA28ED065A",
        "17380DDB842E984302034E1BB66C24E4", "2A0270F3B3A57F49C195A7F2B0736564",
        "3C46A0407BE60A1F00731AB8E9575DF2", "80D2B8BBB1D9FBB8AEC70C802CC67BAD"
    ],

    "SEM ACESSORIO": [
        "1F289CD1A244A837B3D946160B49E54D", "8FBDBF5573B18FAE93736180F8D0197A",
        "74BDEFAB9757A081606B181AC29F1DB2", "0299C06AED970473AE41D986B308CD09",
        "9634715CA7E046CDD0FC857CDC38DCB6", "09E25C12765906F32FEFCA6A9F366E15"
    ]
}

CODIGOS_VERMELHO = {
    "CHAPEU": [
        "B7B2D5A8D1B4D64F0E89E293D4AC08EB", "5A0B7222F0C5F9A7D569039911132B40",
        "DD7650909D02EA03DD155714A731FEF3", "3A170A9FE4F47EFA37D23AD521B9098E",
        "D742FFBECE435C9076FBA5F244396CF8", "60274C1AC606DDDFAB591309CB5ACE78"
    ],

    "OCULOS": [
        "A4385FDA98A439AEDE464B18924ABAEA", "D5AC5A27C34EBFD7A1DBD16D5B99EDFB",
        "7866CC7FB5A03C016EFD4D506A451850", "0DD954EA204F19A1B391B7828491927B",
        "4D6237DF5AB8CC9E1268B8086182979D", "13CEE27A2BD93915479F049378CFFDD3"
    ],

    "CHIFRE": [
        "98C6F2C2287F4C73CEA3D40AE7EC3FF2", "DCA19FFA163054FEEF33432FAD5F9833",
        "B772D43B49BB57B596D0343C33BCFFEC", "A12F16C644039099699332E247F11EC0",
        "6AB5DBC886D46770A86E6CC0BE54A9D1", "435C44C266BC0C05F7B6F48E7A454F1C"
    ],

    "SEM ACESSORIO": [
        "A514839C4971406FF865A3F340E4EA36", "C9E6E7B69F98F516A54CFE2C9E25FB3F",
        "421D13C7ECD67604CEDBE44F88DD1F61", "19A1DE167122A18AF369C749F4E40A48",
        "B00BDAF8D970B7DF664953F63A698374", "EA66C06C1E1C05FA9F1AA39D98DC5BC1"
    ]
}

# =========================================================
# RESET POR HORA
# =========================================================

def resetar_por_hora(caminho_resultados):
    global ultimo_reset_hora
    global acessorio_wins, acessorio_loss
    global ultima_previsao_acessorio, ultimo_codigo_processado

    agora = datetime.now().hour

    if ultimo_reset_hora == agora:
        return

    ultimo_reset_hora = agora

    print("⏰ RESET DE HORA EXECUTADO")

    with open(caminho_resultados, "w", encoding="utf-8") as f:
        f.write("resultado\n")

    acessorio_wins = 0
    acessorio_loss = 0
    ultima_previsao_acessorio = None
    ultimo_codigo_processado = None

    print("🗑️ Estatísticas resetadas")


# =========================================================
# IDENTIFICAR COR + ACESSÓRIO
# =========================================================

def identificar_cor_acessorio(codigo):
    codigo = str(codigo).strip().upper()

    for cor, mapa in [("AZUL", CODIGOS_AZUL), ("VERMELHO", CODIGOS_VERMELHO)]:
        for acessorio, lista in mapa.items():
            if codigo in lista:
                return cor, acessorio

    return "DESCONHECIDO", "DESCONHECIDO"


# =========================================================
# HISTÓRICO
# =========================================================

def carregar_historico(csv_file="sequencias.csv"):
    historico_azul = []
    historico_vermelho = []

    try:
        with open(csv_file, "r", encoding="utf-8") as file:
            reader = list(csv.DictReader(file))

            for row in reader:
                codigo = row.get("Codigo", "").strip().upper()
                if not codigo:
                    continue

                cor, acessorio = identificar_cor_acessorio(codigo)

                if acessorio == "DESCONHECIDO":
                    continue

                if cor == "AZUL":
                    historico_azul.append(acessorio)
                else:
                    historico_vermelho.append(acessorio)

    except Exception as e:
        print(f"⚠️ Erro CSV: {e}")

    return historico_azul, historico_vermelho


# =========================================================
# CACHE DE PADRÕES (⚡ MAIS RÁPIDO)
# =========================================================

def gerar_padroes_cache(historico, janela):
    key = (tuple(historico), janela)

    if key in CACHE_PADROES:
        return CACHE_PADROES[key]

    padroes = {}

    for i in range(len(historico) - janela):
        seq = tuple(historico[i:i + janela])
        prox = historico[i + janela]

        padroes.setdefault(seq, []).append(prox)

    CACHE_PADROES[key] = padroes
    return padroes


# =========================================================
# BAYES SIMPLES (🧠 INTELIGÊNCIA)
# =========================================================

def bayes_probabilidade(seq, proximos):
    cont = Counter(proximos)

    total = sum(cont.values())

    probs = {}
    for k, v in cont.items():
        probs[k] = v / total

    return probs


# =========================================================
# DASHBOARD
# =========================================================

def dashboard(cor, acessorio, confianca):
    total = acessorio_wins + acessorio_loss
    taxa = (acessorio_wins / total * 100) if total else 0

    print("\n================ DASHBOARD ================")
    print(f"COR: {cor}")
    print(f"PREVISÃO: {acessorio}")
    print(f"CONFIANÇA: {confianca:.2f}%")
    print(f"WINS: {acessorio_wins} | LOSS: {acessorio_loss}")
    print(f"ACURÁCIA: {taxa:.2f}%")
    print("===========================================\n")


# =========================================================
# PREVISÃO PRINCIPAL
# =========================================================

def prever_proximo_acessorio():
    global ultima_previsao_acessorio

    historico_azul, historico_vermelho = carregar_historico()

    resultados = {}

    for cor_nome, historico in [("AZUL", historico_azul), ("VERMELHO", historico_vermelho)]:

        if len(historico) < 10:
            continue

        votos = []
        predicoes_janelas = []

        pesos_base = {6: 1.5, 5: 1.2, 4: 1.0}

        for janela in [6, 5, 4]:

            if len(historico) < janela + 1:
                continue

            padroes = gerar_padroes_cache(historico, janela)
            seq = tuple(historico[-janela:])

            if seq not in padroes:
                continue

            proximos = padroes[seq]

            probs = bayes_probabilidade(seq, proximos)

            pred = max(probs, key=probs.get)
            taxa = probs[pred]

            # pesos dinâmicos (aprendem com histórico)
            peso_dinamico = PESOS_DINAMICOS[(cor_nome, pred)]

            if taxa >= 0.60:

                predicoes_janelas.append(pred)

                votos.extend([pred] * int(taxa * pesos_base[janela] * peso_dinamico * 10))

        if len(predicoes_janelas) < 2:
            continue

        if len(set(predicoes_janelas)) != 1:
            continue

        if not votos:
            continue

        final = Counter(votos)
        acessorio = final.most_common(1)[0][0]

        confianca = (final[acessorio] / sum(final.values())) * 100

        if confianca >= 70:
            resultados[cor_nome] = (acessorio, confianca)

    if not resultados:
        print("❌ Sem previsão")
        return None

    cor, (acessorio, confianca) = max(resultados.items(), key=lambda x: x[1][1])

    ultima_previsao_acessorio = acessorio

    dashboard(cor, acessorio, confianca)

    return {
        "cor": cor,
        "acessorio": acessorio,
        "confianca": round(confianca, 2)
    }


# =========================================================
# VALIDAÇÃO + APRENDIZADO
# =========================================================

def processar_validacao_acessorio():
    global acessorio_wins, acessorio_loss
    global ultima_previsao_acessorio, ultimo_codigo_processado
    global PESOS_DINAMICOS

    try:
        with open("sequencias.csv", "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))

            if not reader:
                return

            codigo_real = reader[-1].get("Codigo", "").strip().upper()

    except:
        return

    if not codigo_real or codigo_real == ultimo_codigo_processado:
        return

    ultimo_codigo_processado = codigo_real

    _, acessorio_real = identificar_cor_acessorio(codigo_real)

    if acessorio_real == "DESCONHECIDO" or not ultima_previsao_acessorio:
        return

    print(f"🎩 Previsto: {ultima_previsao_acessorio}")
    print(f"🎩 Real: {acessorio_real}")

    if acessorio_real == ultima_previsao_acessorio:
        acessorio_wins += 1
        PESOS_DINAMICOS[("AZUL", acessorio_real)] += 0.05
        print(f"✅ WIN ({acessorio_wins})")
    else:
        acessorio_loss += 1
        PESOS_DINAMICOS[("AZUL", acessorio_real)] -= 0.02
        print(f"❌ LOSS ({acessorio_loss})")


# =========================================================
# RESULTADO
# =========================================================

def obter_resultado_acessorio():
    total = acessorio_wins + acessorio_loss

    taxa = (acessorio_wins / total * 100) if total else 0

    return {
        "wins": acessorio_wins,
        "loss": acessorio_loss,
        "taxa": round(taxa, 2)
    }