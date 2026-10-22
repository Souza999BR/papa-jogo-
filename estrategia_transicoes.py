"""Estratégia de transições numéricas com janela móvel de 60 resultados.

Adaptada da análise do userscript PA333:
- Analisa transições a partir do número mais recente, usando os últimos 60 resultados.
- Não reinicia a análise por blocos de horário.
- Limita continuidades repetidas a quatro ocorrências.
- Previsão de número único: exige pelo menos 3 ocorrências.
- Em empate na maior frequência: exige pelo menos 2 ocorrências por candidato
  e mantém os dois maiores candidatos.
- Para enviar ao Telegram, escolhe apenas UM número: entre os dois empatados,
  seleciona o que apareceu menos nos últimos 10 resultados.
- Se os dois apareceram igualmente nos últimos 10, desempata pelo menor número.
"""
import csv
import os
from collections import Counter
from datetime import datetime

from modelo_numeros import numero_por_codigo, cor_por_numero, codigo_sem_acessorio

ARQUIVO_TRANSICOES = "transicoes.csv"
ARQUIVO_PREVISOES = "previsoes_codigo.csv"
MIN_OCORRENCIAS_UNICO = 3
MIN_OCORRENCIAS_EMPATE = 2
CONFIANCA_MINIMA = 0.65
MAX_CONTINUIDADE = 4
JANELA_RECENTE = 9
JANELA_ANALISE = 60


# Sem reset por blocos de horário; a previsão é limitada pela janela móvel
# dos últimos 60 resultados recebidos no histórico.
def bloco_atual(agora=None):
    return "SEM_RESET"


def registrar_transicao(historico, timestamp=None):
    """historico: lista de (timestamp, cor, codigo). Retorna o número mais recente."""
    if not historico:
        return None

    timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    codigo = historico[-1][2]
    numero = numero_por_codigo(codigo)
    if numero is None:
        return None

    bloco = bloco_atual(datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"))
    anterior = historico[-2] if len(historico) > 1 else None

    if anterior:
        n_anterior = numero_por_codigo(anterior[2])
        if n_anterior is not None:
            try:
                with open(ARQUIVO_TRANSICOES, "a", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerow([bloco, timestamp, n_anterior, numero])
            except OSError as e:
                print(f"⚠️ Não foi possível salvar transição: {e}")

    return numero


def _ler_transicoes(bloco):
    saida = []
    try:
        with open(ARQUIVO_TRANSICOES, newline="", encoding="utf-8") as f:
            for row in csv.reader(f):
                if len(row) >= 4:
                    try:
                        saida.append((int(row[2]), int(row[3])))
                    except ValueError:
                        continue
    except FileNotFoundError:
        pass
    return saida


def prever_transicao(historico):
    """Retorna dict com número único escolhido, cor, código, confiança e estatísticas.

    O histórico deve estar ordenado do mais antigo para o mais recente.
    Cada item segue o formato (timestamp, cor, codigo).
    """
    if len(historico) < 2:
        return None

    agora = datetime.now()
    bloco = bloco_atual(agora)
    numero_atual = numero_por_codigo(historico[-1][2])
    if numero_atual is None:
        return None

    # Usa exclusivamente os últimos 60 resultados recebidos no histórico.
    # Cada par consecutivo forma uma transição (resultado anterior -> seguinte).
    # Assim, transicoes.csv continua sendo registrado, mas dados antigos desse
    # arquivo não influenciam a previsão atual.
    historico_analise = historico[-JANELA_ANALISE:]
    transicoes = []
    for i in range(1, len(historico_analise)):
        try:
            origem = numero_por_codigo(historico_analise[i - 1][2])
            destino = numero_por_codigo(historico_analise[i][2])
        except (IndexError, TypeError):
            continue
        if origem is not None and destino is not None:
            transicoes.append((origem, destino))

    candidatos = [destino for origem, destino in transicoes if origem == numero_atual]
    if not candidatos:
        return None

    # Limita o peso de uma mesma continuidade a quatro ocorrências.
    contagens_brutas = Counter(candidatos)
    contagens = Counter({
        numero: min(quantidade, MAX_CONTINUIDADE)
        for numero, quantidade in contagens_brutas.items()
    })

    maior = max(contagens.values())
    # Primeiro identifica todos os números na frequência máxima. O mínimo
    # de ocorrências é aplicado depois, de forma diferente para único e empate.
    lideres = [
        numero for numero, quantidade in contagens.items()
        if quantidade == maior
    ]
    total = len(candidatos)
    confianca = (maior / total) if total else 0.0

    empate = len(lideres) > 1

    if empate:
        # EMPATE: cada candidato precisa ter pelo menos 2 ocorrências.
        # Se houver mais de dois líderes, mantém os DOIS maiores números;
        # o empate não é descartado.
        lideres_validos = [
            numero for numero in lideres
            if contagens[numero] >= MIN_OCORRENCIAS_EMPATE
        ]
        if len(lideres_validos) < 2:
            return None
        lideres = lideres_validos

        dois_candidatos = sorted(lideres, reverse=True)[:2]

        # A análise dos ÚLTIMOS 10 resultados decide qual único número
        # será enviado ao Telegram. O que apareceu menos é priorizado;
        # se um candidato acabou de sair e o outro não, isso favorece o outro.
        ultimos_numeros = []
        for item in historico[-JANELA_RECENTE:]:
            try:
                numero = numero_por_codigo(item[2])
            except (IndexError, TypeError):
                numero = None
            if numero is not None:
                ultimos_numeros.append(numero)

        frequencia_recente = Counter(ultimos_numeros)
        escolhido = min(
            dois_candidatos,
            key=lambda numero: (frequencia_recente.get(numero, 0), numero)
        )
        candidatos_selecionados = dois_candidatos
    else:
        escolhido = lideres[0]
        candidatos_selecionados = [escolhido]

        # Previsão de número único exige pelo menos 3 ocorrências.
        if contagens[escolhido] < MIN_OCORRENCIAS_UNICO:
            return None

        # A confiança mínima é aplicada somente quando há um único líder.
        # Em empate válido, a confiança não bloqueia a previsão.
        if confianca < CONFIANCA_MINIMA:
            return None

    cor = cor_por_numero(escolhido)
    codigo = codigo_sem_acessorio(escolhido)

    try:
        novo = not os.path.exists(ARQUIVO_PREVISOES)
        with open(ARQUIVO_PREVISOES, "a", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            if novo:
                escritor.writerow([
                    "timestamp", "bloco", "numero_origem", "numero_previsto",
                    "cor", "confianca", "ocorrencias", "empate",
                    "candidatos_empate", "frequencia_recente_escolhido"
                ])

            recentes = [
                numero_por_codigo(item[2])
                for item in historico[-JANELA_RECENTE:]
                if len(item) > 2 and numero_por_codigo(item[2]) is not None
            ]
            freq_escolhido = Counter(recentes).get(escolhido, 0)

            escritor.writerow([
                agora.strftime("%Y-%m-%d %H:%M:%S"),
                bloco,
                numero_atual,
                escolhido,
                cor,
                f"{confianca:.4f}",
                contagens[escolhido],
                empate,
                "/".join(map(str, candidatos_selecionados)),
                freq_escolhido
            ])
    except OSError as e:
        print(f"⚠️ Não foi possível salvar previsão por código: {e}")

    return {
        "numero": escolhido,
        "cor": cor,
        "codigo": codigo,
        "confianca": confianca,
        "ocorrencias": contagens[escolhido],
        "origem": numero_atual,
        "empate": empate,
        "candidatos_empate": candidatos_selecionados,
    }
