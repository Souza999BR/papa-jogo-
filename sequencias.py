import csv
import requests
import os
import ast
import re

from bs4 import BeautifulSoup

from datetime import datetime, timedelta

# ========================
# ARQUIVOS
# ========================
SEQ_HIST_FILE = "sequencias.csv"
CODIGO_FILE = "codigo.csv"

# ========================
# API
# ========================
API_URL = "https://game.pa3333.com/api/game/get_game?lang=pt"

# ========================
# SITE
# ========================
SITE_URL = "https://www.pa3333.com/?cur=game"

# ========================
# HISTÓRICO APOSTAS
# ========================
historico_apostas = []

# ========================
# IMAGENS
# ========================

IMAGENS_VERMELHO = [
    "https://www.pa3333.com/static/game/A4385FDA98A439AEDE464B18924ABAEA.png",
    "https://www.pa3333.com/static/game/A514839C4971406FF865A3F340E4EA36.png",
    "https://www.pa3333.com/static/game/B7B2D5A8D1B4D64F0E89E293D4AC08EB.png",
    "https://www.pa3333.com/static/game/5A0B7222F0C5F9A7D569039911132B40.png",
    "https://www.pa3333.com/static/game/C9E6E7B69F98F516A54CFE2C9E25FB3F.png",
    "https://www.pa3333.com/static/game/98C6F2C2287F4C73CEA3D40AE7EC3FF2.png",
    "https://www.pa3333.com/static/game/DCA19FFA163054FEEF33432FAD5F9833.png",
    "https://www.pa3333.com/static/game/DD7650909D02EA03DD155714A731FEF3.png",
    "https://www.pa3333.com/static/game/D5AC5A27C34EBFD7A1DBD16D5B99EDFB.png",
    "https://www.pa3333.com/static/game/7866CC7FB5A03C016EFD4D506A451850.png",
    "https://www.pa3333.com/static/game/B772D43B49BB57B596D0343C33BCFFEC.png",
    "https://www.pa3333.com/static/game/A12F16C644039099699332E247F11EC0.png",
    "https://www.pa3333.com/static/game/421D13C7ECD67604CEDBE44F88DD1F61.png",
    "https://www.pa3333.com/static/game/0DD954EA204F19A1B391B7828491927B.png",
    "https://www.pa3333.com/static/game/4D6237DF5AB8CC9E1268B8086182979D.png",
    "https://www.pa3333.com/static/game/19A1DE167122A18AF369C749F4E40A48.png",
    "https://www.pa3333.com/static/game/3A170A9FE4F47EFA37D23AD521B9098E.png",
    "https://www.pa3333.com/static/game/B00BDAF8D970B7DF664953F63A698374.png",
    "https://www.pa3333.com/static/game/EA66C06C1E1C05FA9F1AA39D98DC5BC1.png",
    "https://www.pa3333.com/static/game/13CEE27A2BD93915479F049378CFFDD3.png",
    "https://www.pa3333.com/static/game/D742FFBECE435C9076FBA5F244396CF8.png",
    "https://www.pa3333.com/static/game/6AB5DBC886D46770A86E6CC0BE54A9D1.png",
    "https://www.pa3333.com/static/game/435C44C266BC0C05F7B6F48E7A454F1C.png",
    "https://www.pa3333.com/static/game/60274C1AC606DDDFAB591309CB5ACE78.png"
]

IMAGENS_AZUL = [
    "https://www.pa3333.com/static/game/1F289CD1A244A837B3D946160B49E54D.png",
    "https://www.pa3333.com/static/game/2F5BB7747EFDA0546636FB385A3FA593.png",
    "https://www.pa3333.com/static/game/9B1138C4B04769111A3756E7CC6E263E.png",
    "https://www.pa3333.com/static/game/8FBDBF5573B18FAE93736180F8D0197A.png",
    "https://www.pa3333.com/static/game/FAE594628F003E7D8250252BAA6A83B2.png",
    "https://www.pa3333.com/static/game/C2D2BC9253A4F95A06464C302C552FE8.png",
    "https://www.pa3333.com/static/game/F2A057FC73359A2781F0FD48F63D6FDE.png",
    "https://www.pa3333.com/static/game/4864DAFB55D05D74897FDCE5DEE7FD22.png",
    "https://www.pa3333.com/static/game/1981E4A762B39858DC33F9EA28ED065A.png",
    "https://www.pa3333.com/static/game/88CB29DAAB6DD7AE3016B506C36E9F17.png",
    "https://www.pa3333.com/static/game/C22C60349630D688CEF20A3FD708AD87.png",
    "https://www.pa3333.com/static/game/1701CF909C49835D0C793C7A7EF82A5D.png",
    "https://www.pa3333.com/static/game/74BDEFAB9757A081606B181AC29F1DB2.png",
    "https://www.pa3333.com/static/game/620726CCE3CBC8C574E5889CB404DA8C.png",
    "https://www.pa3333.com/static/game/0299C06AED970473AE41D986B308CD09.png",
    "https://www.pa3333.com/static/game/17380DDB842E984302034E1BB66C24E4.png",
    "https://www.pa3333.com/static/game/2A0270F3B3A57F49C195A7F2B0736564.png",
    "https://www.pa3333.com/static/game/9634715CA7E046CDD0FC857CDC38DCB6.png",
    "https://www.pa3333.com/static/game/6B5DFCF1F44C9D485DDA1902AC33C0A9.png",
    "https://www.pa3333.com/static/game/A5CB00D7C8FFFE5FB2C79C540A54817A.png",
    "https://www.pa3333.com/static/game/3C46A0407BE60A1F00731AB8E9575DF2.png",
    "https://www.pa3333.com/static/game/80D2B8BBB1D9FBB8AEC70C802CC67BAD.png",
    "https://www.pa3333.com/static/game/09E25C12765906F32FEFCA6A9F366E15.png",
    "https://www.pa3333.com/static/game/C0069D16731C2D1EEFF8F67ED560B89B.png"
]

# ========================
# FUNÇÕES AUXILIARES
# ========================

def salvar_codigo_desconhecido(codigo_img):

    url = f"https://www.pa3333.com/static/game/{codigo_img}.png"

    if url in IMAGENS_AZUL or url in IMAGENS_VERMELHO:
        return

    try:

        with open(
            CODIGO_FILE,
            "a",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            writer.writerow([
                timestamp,
                url
            ])

        print(
            f"⚠️ Código desconhecido salvo: {url}"
        )

    except Exception as e:

        print(
            f"❌ Erro ao salvar código desconhecido: {e}"
        )


def cor_por_codigo(codigo_img):

    url = f"https://www.pa3333.com/static/game/{codigo_img}.png"

    if url in IMAGENS_AZUL:
        return "AZUL"

    if url in IMAGENS_VERMELHO:
        return "VERMELHO"

    salvar_codigo_desconhecido(codigo_img)

    return None


# ========================
# API
# ========================

def pegar_ultima_cor():

    try:

        resp = requests.get(
            API_URL,
            timeout=15
        )

        if resp.status_code != 200:

            print(
                f"⚠️ Status inválido API: {resp.status_code}"
            )

            return None, None

        data = resp.json()

        if "data" not in data:

            print(
                "⚠️ Campo data não encontrado."
            )

            return None, None

        ultima_img = data["data"].get(
            "last_image_name"
        )

        if not ultima_img:

            print(
                "⚠️ last_image_name vazio."
            )

            return None, None

        codigo = ultima_img.replace(
            ".png",
            ""
        )

        cor = cor_por_codigo(codigo)

        return cor, codigo

    except requests.RequestException as e:

        print(
            f"❌ Erro de conexão API: {e}"
        )

    except Exception as e:

        print(
            f"❌ Erro geral API: {e}"
        )

    return None, None


# ========================
# LEITURA DAS APOSTAS
# ========================

def pegar_valores_apostas():

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        resp = requests.get(
            SITE_URL,
            headers=headers,
            timeout=15
        )

        if resp.status_code != 200:

            print(
                "⚠️ Falha carregar página."
            )

            return None

        soup = BeautifulSoup(
            resp.text,
            "html.parser"
        )

        # =========================
        # VERMELHO
        # =========================

        vermelho_elem = soup.find(
            attrs={"data-type": "red"}
        )

        vermelho = 0.0

        if vermelho_elem:

            texto_vermelho = vermelho_elem.get_text(
                " ",
                strip=True
            )

            match_vermelho = re.search(
                r"TOTAL:R\$([\d\.]+)",
                texto_vermelho
            )

            if match_vermelho:

                vermelho = float(
                    match_vermelho.group(1)
                )

        # =========================
        # AZUL
        # =========================

        azul = 0.0

        todos_totais = soup.find_all(
            string=re.compile(r"TOTAL:R\$")
        )

        valores_encontrados = []

        for item in todos_totais:

            match = re.search(
                r"TOTAL:R\$([\d\.]+)",
                item
            )

            if match:

                valores_encontrados.append(
                    float(match.group(1))
                )

        for valor in valores_encontrados:

            if valor != vermelho:

                azul = valor
                break

        if azul == 0 and vermelho == 0:

            print(
                "⚠️ Não encontrou apostas."
            )

            return None

        diferenca = abs(
            azul - vermelho
        )

        resultado = {
            "azul": azul,
            "vermelho": vermelho,
            "diferenca": diferenca,
            "timestamp": datetime.now()
        }

        historico_apostas.append(
            resultado
        )

        if len(historico_apostas) > 50:
            historico_apostas.pop(0)

        print(
            f"💰 AZUL={azul} | "
            f"VERMELHO={vermelho}"
        )

        return resultado

    except Exception as e:

        print(
            f"❌ Erro apostas: {e}"
        )

        return None


# ========================
# HISTÓRICO
# ========================

def salvar_historico(cor, codigo):

    if not cor or not codigo:
        return

    try:

        agora = datetime.now()

        timestamp = agora.replace(
            second=10,
            microsecond=0
        ).strftime("%Y-%m-%d %H:%M:%S")

        ultimo_timestamp = None

        if os.path.exists(SEQ_HIST_FILE):

            with open(
                SEQ_HIST_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                linhas = list(csv.reader(f))

                if len(linhas) > 1:
                    ultimo_timestamp = linhas[-1][0]

        if ultimo_timestamp == timestamp:

            print(
                "⚠️ Registro duplicado ignorado."
            )

            return

        with open(
            SEQ_HIST_FILE,
            "a",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            writer.writerow([
                timestamp,
                cor,
                codigo
            ])

        print(
            f"🟢 Nova cor registrada: "
            f"{cor} | "
            f"Código: {codigo} | "
            f"Hora: {timestamp}"
        )

    except Exception as e:

        print(
            f"❌ Erro ao salvar histórico: {e}"
        )


def carregar_historico_cores():

    historico = []

    try:

        with open(
            SEQ_HIST_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            reader = csv.reader(f)

            next(reader, None)

            for row in reader:

                if len(row) >= 3:

                    timestamp = row[0]
                    cor = row[1]
                    codigo = row[2]

                    if cor in [
                        "AZUL",
                        "VERMELHO"
                    ]:

                        historico.append(
                            (
                                timestamp,
                                cor,
                                codigo
                            )
                        )

    except FileNotFoundError:
        pass

    except Exception as e:

        print(
            f"❌ Erro carregar histórico: {e}"
        )

    return historico


def traduzir_cor(cor):

    if not cor:
        return None

    cor = cor.upper()

    if cor.startswith("A"):
        return "A"

    if cor.startswith("V"):
        return "V"

    return None


# ========================
# HORÁRIOS
# ========================

def horarios_sao_consecutivos(historico):

    if len(historico) < 4:
        return False

    ultimos = historico[-4:]

    horarios = []

    try:

        for x in ultimos:

            ts = x[0]

            # =========================
            # AJUSTE:
            # ACEITA DATETIME OU STRING
            # =========================

            if isinstance(ts, datetime):

                horario = ts

            else:

                try:

                    horario = datetime.strptime(
                        str(ts),
                        "%Y-%m-%d %H:%M:%S"
                    )

                except:

                    horario = datetime.strptime(
                        str(ts),
                        "%H:%M"
                    )

            horarios.append(horario)

        for i in range(1, len(horarios)):

            esperado = (
                horarios[i - 1]
                + timedelta(minutes=1)
            )

            if (
                horarios[i].replace(second=0)
                != esperado.replace(second=0)
            ):

                print(
                    f"⚠️ Horário quebrado: "
                    f"{horarios[i - 1]} -> "
                    f"{horarios[i]}"
                )

                return False

        return True

    except Exception as e:

        print(
            f"❌ Erro validar horários: {e}"
        )

        return False

# ========================
# PREVISÃO POR COR
# ========================

def calcular_previsao_exata_por_cor(
    historico_cores,
    caminho_seq='seq.csv',
    caminho_resultados='resultados.csv',
    caminho_sequencias='sequencias.csv'
):

    import os
    import csv
    import ast
    from datetime import datetime

    if len(historico_cores) < 7:
        return None

    if not horarios_sao_consecutivos(historico_cores):
        return None

    if not os.path.exists(caminho_seq):
        print(f"⚠️ Arquivo {caminho_seq} não encontrado.")
        return None

    try:
        with open(caminho_seq, 'r', encoding='utf-8') as f:
            conteudo = f.read().strip()

        sequencias_fixas = ast.literal_eval(conteudo)

    except Exception as e:
        print(f"❌ Erro ao ler seq.csv: {e}")
        return None

    if not isinstance(sequencias_fixas, list):
        print("⚠️ seq.csv inválido.")
        return None

    # ==========================================
    # WIN / LOSS
    # ==========================================

    total_win = 0
    total_loss = 0

    try:
        if os.path.exists(caminho_resultados):

            with open(caminho_resultados, 'r', encoding='utf-8') as f:
                leitor = csv.reader(f)
                next(leitor, None)

                for linha in leitor:
                    linha_texto = ",".join(linha).upper()

                    if "WIN" in linha_texto:
                        total_win += 1
                    elif "LOSS" in linha_texto:
                        total_loss += 1

        print(f"📊 WIN: {total_win} | LOSS: {total_loss}")

    except Exception as e:
        print(f"❌ Erro resultados: {e}")


   
    # ==========================================
    # CONTROLE DE MODO POR HORA
    # ==========================================

    arquivo_modo = "modo_analise.txt"
    arquivo_hora_modo = "ultima_hora_modo.txt"

    modo_anterior = "FAVOR"

    try:

        if os.path.exists(arquivo_modo):

            with open(
                arquivo_modo,
                "r",
                encoding="utf-8"
            ) as f:

                valor_salvo = (
                    f.read()
                    .strip()
                    .upper()
                )

                if valor_salvo in [
                    "CONTRA",
                    "FAVOR"
                ]:

                    modo_anterior = valor_salvo

    except Exception as erro:

        print(
            f"⚠️ Erro ao carregar modo: {erro}"
        )

    modo_analise = modo_anterior

    print(
        f"📊 WIN: {total_win} | LOSS: {total_loss}"
    )

    # ==========================================
    # TROCA APENAS UMA VEZ POR HORA
    # ==========================================

    hora_atual_modo = datetime.now().strftime("%Y-%m-%d %H")

    ultima_hora_processada = ""

    try:

        if os.path.exists(
            arquivo_hora_modo
        ):

            with open(
                arquivo_hora_modo,
                "r",
                encoding="utf-8"
            ) as f:

                ultima_hora_processada = (
                    f.read()
                    .strip()
                )

    except Exception as erro:

        print(
            f"⚠️ Erro lendo hora modo: {erro}"
        )

    if (
        hora_atual_modo !=
        ultima_hora_processada
    ):

        if total_loss > total_win:

            if modo_anterior == "FAVOR":

                modo_analise = "CONTRA"

                print(
                    "🔄 LOSS > WIN → FAVOR para CONTRA"
                )

            else:

                modo_analise = "FAVOR"

                print(
                    "🔄 LOSS > WIN → CONTRA para FAVOR"
                )

        else:

            print(
                "✅ WIN >= LOSS → Mantendo modo atual"
            )

        try:

            with open(
                arquivo_hora_modo,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    hora_atual_modo
                )

        except:
            pass

    # ==========================================
    # SALVA MODO
    # ==========================================

    try:

        with open(
            arquivo_modo,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                modo_analise
            )

    except:
        pass

    print(
        f"🧠 Modo análise atual: {modo_analise}"
    )

    # ==========================================
    # RESET POR HORA (RESULTADOS)
    # ==========================================

    try:

        if os.path.exists(caminho_sequencias):

            with open(caminho_sequencias, 'r', encoding='utf-8') as f:
                leitor = csv.DictReader(f)
                linhas = list(leitor)

            if linhas:

                ultimo = linhas[-1]

                data_obj = datetime.strptime(
                    ultimo["Timestamp"],
                    "%Y-%m-%d %H:%M:%S"
                )

                hora_atual = data_obj.strftime("%Y-%m-%d %H")
                arquivo_hora = "ultima_hora_reset.txt"

                ultima_hora = ""

                if os.path.exists(arquivo_hora):
                    with open(arquivo_hora, "r", encoding="utf-8") as f:
                        ultima_hora = f.read().strip()

                if hora_atual != ultima_hora:

                    print("⏰ Virada de hora detectada")

                    # reset resultados
                    with open(caminho_resultados, "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(["Resultado"])

                    print("🗑️ resultados.csv resetado")

                    with open(arquivo_hora, "w", encoding="utf-8") as f:
                        f.write(hora_atual)

    except Exception as e:
        print(f"❌ Erro reset hora: {e}")

    # ==========================================
    # BUSCA SEQUÊNCIA (JANELAS 6,5,4)
    # ==========================================

    janelas_prioridade = [6, 5]

    for janela_desejada in janelas_prioridade:

        for entrada, saida in sequencias_fixas:

            janela = len(entrada)

            if janela != janela_desejada:
                continue

            if len(historico_cores) < janela:
                continue

            ultimos = [x[1].upper() for x in historico_cores[-janela:]]
            entrada_upper = [x.upper() for x in entrada]

            if ultimos == entrada_upper:

                previsao_original = saida.upper()

                print(f"✅ Sequência encontrada: {entrada_upper}")
                print(f"🔍 Padrão original: {previsao_original}")
                print(f"📈 Modo análise: {modo_analise}")
                print(f"🎯 PREVISÃO COR: {previsao_original}")

                return {
                    "cor": previsao_original,
                    "entrada": entrada_upper,
                    "original": previsao_original,
                    "modo": modo_analise
                }

    print("⚠️ Nenhuma sequência encontrada.")
    return None


# ========================
# PREVISÃO POR CÓDIGO
# ========================

def calcular_previsao_exata(
    historico_codigos
):

    if len(historico_codigos) < 10:

        print(
            "⚠️ Histórico insuficiente por código."
        )

        return None

    historico_normalizado = []

    try:

        for horario, cor, codigo in historico_codigos:

            if isinstance(
                horario,
                str
            ):

                horario = datetime.strptime(
                    horario,
                    "%Y-%m-%d %H:%M:%S"
                )

            historico_normalizado.append(
                (
                    horario,
                    cor.upper(),
                    codigo
                )
            )

    except Exception as e:

        print(
            f"❌ Erro converter horários: {e}"
        )

        return None

    historico_codigos = historico_normalizado

    sequencia_valida = []

    for item in historico_codigos:

        sequencia_valida.append(item)

        if len(sequencia_valida) < 4:
            continue

        if not horarios_sao_consecutivos(
            sequencia_valida[-4:]
        ):

            sequencia_valida.pop(0)

    if len(sequencia_valida) < 8:

        print(
            "⚠️ Nenhuma sequência consecutiva suficiente encontrada."
        )

        return None

    historico_codigos = sequencia_valida

    try:

        # =========================================
        # AGRUPA POR HORA
        # =========================================

        blocos_hora = {}

        for horario, cor, codigo in historico_codigos:

            chave_hora = horario.strftime(
                "%Y-%m-%d %H"
            )

            blocos_hora.setdefault(
                chave_hora,
                []
            ).append(
                (
                    horario,
                    cor,
                    codigo
                )
            )

        apenas_cores_atuais = [

            cor

            for _, cor, _
            in historico_codigos

        ]

        cor_prevista = None
        confianca = 0
        janela_usada = None
        cor_dominante = None
        proximas_cores = []

        # =========================================
        # PROCURA PADRÃO MAIS FORTE
        # 6 -> 5 -> 4
        # =========================================

        for TAM_JANELA in [6, 5]:

            padroes_cores = {}

            for hora, dados in blocos_hora.items():

                if len(dados) <= TAM_JANELA:
                    continue

                apenas_cores = [

                    cor

                    for _, cor, _
                    in dados

                ]

                for i in range(
                    len(apenas_cores)
                    - TAM_JANELA
                ):

                    janela = tuple(
                        apenas_cores[
                            i:i + TAM_JANELA
                        ]
                    )

                    proxima_cor = (
                        apenas_cores[
                            i + TAM_JANELA
                        ]
                    )

                    padroes_cores.setdefault(
                        janela,
                        []
                    ).append(
                        proxima_cor
                    )

            janela_atual_cores = tuple(
                apenas_cores_atuais[
                    -TAM_JANELA:
                ]
            )

            if (
                janela_atual_cores
                not in padroes_cores
            ):
                continue

            proximas_cores_local = (
                padroes_cores[
                    janela_atual_cores
                ]
            )

            if len(proximas_cores_local) < 3:
                continue

            contagem_cores = {

                cor: proximas_cores_local.count(
                    cor
                )

                for cor in set(
                    proximas_cores_local
                )
            }

            total = len(
                proximas_cores_local
            )

            dominante_local = max(
                contagem_cores,
                key=contagem_cores.get
            )

            maior_contagem = (
                contagem_cores[
                    dominante_local
                ]
            )

            confianca_local = (
                maior_contagem / total
            )

            if confianca_local < 0.80:
                continue

            candidatos = [

                cor

                for cor, qtd
                in contagem_cores.items()

                if qtd == maior_contagem

            ]

            if len(candidatos) > 1:
                continue

            cor_prevista = dominante_local
            confianca = confianca_local
            cor_dominante = dominante_local
            janela_usada = TAM_JANELA
            proximas_cores = proximas_cores_local

            break

        if not cor_prevista:

            print(
                "⚠️ Nenhum padrão forte encontrado."
            )

            return None

        # =====================================
        # INVERTE APENAS EM TENDÊNCIA FORTE
        # =====================================

        ultimas_cores = apenas_cores_atuais[-4:]

        if len(set(ultimas_cores)) == 1:

            print(
                "🔄 Tendência forte detectada."
            )

            if cor_prevista == "AZUL":

                cor_prevista = "VERMELHO"

            else:

                cor_prevista = "AZUL"

        # =========================================
        # PREVISÃO POR CÓDIGO
        # =========================================

        apenas_codigos = [

            c

            for _, _, c
            in historico_codigos

        ]

        proximo_codigo = None

        for TAM_JANELA in [6, 5]:

            if len(apenas_codigos) <= TAM_JANELA:
                continue

            padroes = {}

            for i in range(
                len(apenas_codigos)
                - TAM_JANELA
            ):

                janela = tuple(
                    apenas_codigos[
                        i:i + TAM_JANELA
                    ]
                )

                proximo = (
                    apenas_codigos[
                        i + TAM_JANELA
                    ]
                )

                padroes.setdefault(
                    janela,
                    []
                ).append(
                    proximo
                )

            janela_atual = tuple(
                apenas_codigos[
                    -TAM_JANELA:
                ]
            )

            if janela_atual not in padroes:
                continue

            proximos = padroes[
                janela_atual
            ]

            codigos_filtrados = []

            for codigo in proximos:

                cor_codigo = (
                    cor_por_codigo(
                        codigo
                    )
                )

                if (
                    cor_codigo
                    == cor_prevista
                ):

                    codigos_filtrados.append(
                        codigo
                    )

            if codigos_filtrados:

                contagens = {

                    codigo:
                    codigos_filtrados.count(
                        codigo
                    )

                    for codigo
                    in set(
                        codigos_filtrados
                    )

                }

                proximo_codigo = max(
                    contagens,
                    key=contagens.get
                )

                break

        # =========================================
        # FALLBACK
        # =========================================

        if not proximo_codigo:

            for _, cor, codigo in reversed(
                historico_codigos
            ):

                if cor == cor_prevista:

                    proximo_codigo = codigo
                    break

        print(
            f"🔎 Janela usada: "
            f"{janela_usada}"
        )

        print(
            f"📊 Próximas cores: "
            f"{proximas_cores}"
        )

        print(
            f"🎯 Cor dominante: "
            f"{cor_dominante}"
        )

        print(
            f"🎯 Cor prevista: "
            f"{cor_prevista}"
        )

        print(
            f"✅ Confiança: "
            f"{confianca:.2%}"
        )

        return (
            proximo_codigo,
            cor_prevista,
            confianca
        )

    except Exception as e:

        print(
            f"❌ Erro previsão código: {e}"
        )

        return None
    
# ========================
# LEITURA DAS APOSTAS
# ========================

SITE_URL = "https://www.pa3333.com/?cur=game"

historico_apostas = []


def extrair_valor_total(texto):

    try:

        match = re.search(
            r"TOTAL:R\$([\d\.]+)",
            texto
        )

        if match:

            return float(
                match.group(1)
            )

    except Exception:
        pass

    return 0.0


def pegar_valores_apostas():

    try:

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/122.0 Safari/537.36"
            )
        }

        resp = requests.get(
            SITE_URL,
            headers=headers,
            timeout=20
        )

        if resp.status_code != 200:

            print(
                f"⚠️ Falha carregar página: "
                f"{resp.status_code}"
            )

            return None

        soup = BeautifulSoup(
            resp.text,
            "html.parser"
        )

        # =========================================
        # BLOCO AZUL
        # =========================================
        bloco_azul = soup.find(
            attrs={
                "data-type": "blue"
            }
        )

        # =========================================
        # BLOCO VERMELHO
        # =========================================
        bloco_vermelho = soup.find(
            attrs={
                "data-type": "red"
            }
        )

        if not bloco_azul or not bloco_vermelho:

            print(
                "⚠️ Não encontrou apostas."
            )

            return None

        texto_azul = bloco_azul.get_text(
            " ",
            strip=True
        )

        texto_vermelho = bloco_vermelho.get_text(
            " ",
            strip=True
        )

        azul = extrair_valor_total(
            texto_azul
        )

        vermelho = extrair_valor_total(
            texto_vermelho
        )

        if azul <= 0 and vermelho <= 0:

            print(
                "⚠️ Valores inválidos."
            )

            return None

        diferenca = abs(
            azul - vermelho
        )

        resultado = {

            "azul": azul,

            "vermelho": vermelho,

            "diferenca": diferenca,

            "timestamp": datetime.now()
        }

        historico_apostas.append(
            resultado
        )

        # mantém últimos 100 ciclos
        historico_apostas[:] = (
            historico_apostas[-100:]
        )

        print(
            f"💰 APOSTAS -> "
            f"AZUL:R${azul} | "
            f"VERMELHO:R${vermelho} | "
            f"DIF:R${diferenca}"
        )

        return resultado

    except Exception as e:

        print(
            f"❌ Erro apostas: {e}"
        )

        return None


# ========================
# LEITURA DAS APOSTAS
# ========================

SITE_URL = "https://www.pa3333.com/?cur=game"

historico_apostas = []


def extrair_valor(texto):

    try:

        match = re.search(
            r"TOTAL:R\$([\d\.]+)",
            texto
        )

        if match:

            return float(
                match.group(1)
            )

    except Exception:
        pass

    return 0.0


def pegar_valores_apostas():

    try:

        headers = {
            "User-Agent": (
                "Mozilla/5.0"
            )
        }

        resp = requests.get(
            SITE_URL,
            headers=headers,
            timeout=15
        )

        if resp.status_code != 200:

            print(
                "⚠️ Falha carregar página."
            )

            return None

        soup = BeautifulSoup(
            resp.text,
            "html.parser"
        )

        # =====================================
        # IDENTIFICA EXATAMENTE PELO data-type
        # =====================================

        bloco_azul = soup.find(
            attrs={
                "data-type": "blue"
            }
        )

        bloco_vermelho = soup.find(
            attrs={
                "data-type": "red"
            }
        )

        if not bloco_azul:

            print(
                "⚠️ Não encontrou apostas AZUL."
            )

            return None

        if not bloco_vermelho:

            print(
                "⚠️ Não encontrou apostas VERMELHO."
            )

            return None

        # =====================================
        # EXTRAI TEXO DOS BLOCOS
        # =====================================

        texto_azul = bloco_azul.get_text(
            " ",
            strip=True
        )

        texto_vermelho = bloco_vermelho.get_text(
            " ",
            strip=True
        )

        # =====================================
        # EXTRAI TOTAL:R$
        # =====================================

        azul = extrair_valor(
            texto_azul
        )

        vermelho = extrair_valor(
            texto_vermelho
        )

        if azul <= 0 and vermelho <= 0:

            print(
                "⚠️ Valores inválidos."
            )

            return None

        diferenca = abs(
            azul - vermelho
        )

        resultado = {
            "azul": azul,
            "vermelho": vermelho,
            "diferenca": diferenca,
            "timestamp": datetime.now()
        }

        historico_apostas.append(
            resultado
        )

        # mantém histórico leve
        if len(historico_apostas) > 300:

            historico_apostas.pop(0)

        print(
            f"💰 AZUL={azul} | "
            f"VERMELHO={vermelho} | "
            f"DIF={diferenca}"
        )

        return resultado

    except Exception as e:

        print(
            f"❌ Erro apostas: {e}"
        )

        return None


# ========================
# PREVISÃO POR APOSTAS (IA ADAPTATIVA)
# ========================

def calcular_pressao_apostas():

    if len(historico_apostas) < 15:

        print(
            "⚠️ Histórico apostas insuficiente."
        )

        return None

    try:

        # =========================================
        # ANALISA SOMENTE OS ÚLTIMOS 15 CICLOS
        # =========================================
        ultimos = historico_apostas[-15:]

        score_azul = 0
        score_vermelho = 0

        ciclos_inversao_azul = 0
        ciclos_inversao_vermelho = 0

        repeticao_azul = 0
        repeticao_vermelho = 0

        tendencia_azul = 0
        tendencia_vermelho = 0

        diferencas = []

        # =========================================
        # IA ANALISA PADRÃO DA PLATAFORMA
        # =========================================
        for i, item in enumerate(ultimos):

            azul = item["azul"]
            vermelho = item["vermelho"]

            diferenca = abs(
                azul - vermelho
            )

            diferencas.append(
                diferenca
            )

            # =====================================
            # DETECTA LADO COM MAIOR PRESSÃO
            # =====================================
            if azul > vermelho:

                repeticao_azul += 1

                # plataforma tende quebrar maioria
                score_vermelho += 1.4

                if diferenca >= 300:
                    score_vermelho += 1

                if diferenca >= 700:
                    score_vermelho += 2

                tendencia_azul += diferenca

            else:

                repeticao_vermelho += 1

                score_azul += 1.4

                if diferenca >= 300:
                    score_azul += 1

                if diferenca >= 700:
                    score_azul += 2

                tendencia_vermelho += diferenca

            # =====================================
            # IA DETECTA INVERSÕES
            # =====================================
            if i >= 1:

                anterior = ultimos[i - 1]

                azul_ant = anterior["azul"]
                vermelho_ant = anterior["vermelho"]

                # explosão azul
                if (
                    azul >
                    azul_ant * 1.8
                ):

                    ciclos_inversao_azul += 1

                    score_vermelho += 1.5

                # explosão vermelho
                if (
                    vermelho >
                    vermelho_ant * 1.8
                ):

                    ciclos_inversao_vermelho += 1

                    score_azul += 1.5

        # =========================================
        # MÉDIA DAS DIFERENÇAS
        # =========================================
        media_diferenca = (
            sum(diferencas)
            / len(diferencas)
        )

        # =========================================
        # DETECTA DOMÍNIO
        # =========================================
        if repeticao_azul >= 10:

            score_vermelho += 3

        if repeticao_vermelho >= 10:

            score_azul += 3

        # =========================================
        # DETECTA TENDÊNCIA
        # =========================================
        if tendencia_azul > tendencia_vermelho:

            score_vermelho += 2

        elif tendencia_vermelho > tendencia_azul:

            score_azul += 2

        # =========================================
        # DETECTA ARMADILHA
        # =========================================
        ultimo = ultimos[-1]

        azul_final = ultimo["azul"]
        vermelho_final = ultimo["vermelho"]

        diferenca_final = abs(
            azul_final - vermelho_final
        )

        if diferenca_final >= (
            media_diferenca * 2
        ):

            if azul_final > vermelho_final:

                score_vermelho += 4

                print(
                    "🧠 IA detectou armadilha AZUL"
                )

            else:

                score_azul += 4

                print(
                    "🧠 IA detectou armadilha VERMELHO"
                )

        # =========================================
        # NORMALIZA
        # =========================================
        total = (
            score_azul +
            score_vermelho
        )

        if total <= 0:

            print(
                "⚠️ Sem força suficiente."
            )

            return None

        confianca_azul = (
            score_azul / total
        )

        confianca_vermelho = (
            score_vermelho / total
        )

        # =========================================
        # LOG DETALHADO
        # =========================================
        print(
            f"📊 SCORE -> "
            f"AZUL:{score_azul:.2f} | "
            f"VERMELHO:{score_vermelho:.2f}"
        )

        print(
            f"📈 REPETIÇÕES -> "
            f"AZUL:{repeticao_azul} | "
            f"VERMELHO:{repeticao_vermelho}"
        )

        print(
            f"🔄 INVERSÕES -> "
            f"AZUL:{ciclos_inversao_azul} | "
            f"VERMELHO:{ciclos_inversao_vermelho}"
        )

        print(
            f"📉 MÉDIA DIFERENÇA -> "
            f"{media_diferenca:.2f}"
        )

        # =========================================
        # DECISÃO FINAL
        # =========================================
        if confianca_azul >= 0.60:

            print(
                f"🤖 IA escolheu AZUL "
                f"({confianca_azul:.1%})"
            )

            return {
                "cor": "AZUL",
                "forca": score_azul,
                "confianca": confianca_azul,
                "modelo": "IA_ADAPTATIVA"
            }

        if confianca_vermelho >= 0.60:

            print(
                f"🤖 IA escolheu VERMELHO "
                f"({confianca_vermelho:.1%})"
            )

            return {
                "cor": "VERMELHO",
                "forca": score_vermelho,
                "confianca": confianca_vermelho,
                "modelo": "IA_ADAPTATIVA"
            }

        print(
            "⚠️ IA sem confiança suficiente."
        )

        return None

    except Exception as e:

        print(
            f"❌ Erro pressão apostas: {e}"
        )

        return None