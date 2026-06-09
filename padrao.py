import csv
from collections import Counter, OrderedDict
from datetime import datetime, timedelta
from sequencias import SEQ_HIST_FILE


SEQ_PADRAO_FILE = "seq.csv"


def carregar_historico():
    """Carrega histórico de timestamps e cores já registradas."""
    historico = []
    try:
        with open(SEQ_HIST_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # pular cabeçalho
            for row in reader:
                if len(row) >= 3:
                    timestamp, cor, codigo = row
                    historico.append((timestamp, cor))
    except FileNotFoundError:
        print("⚠️ Histórico ainda não existe.")
    return historico


def filtrar_sequencias_consecutivas(historico):
    """
    Filtra apenas os registros que estão em sequência minuto a minuto.
    Retorna uma lista contendo SOMENTE os registros consecutivos.
    """
    if len(historico) < 4:
        return []

    consecutivos = [historico[0]]
    for i in range(1, len(historico)):
        t1 = datetime.strptime(historico[i - 1][0], "%Y-%m-%d %H:%M:%S")
        t2 = datetime.strptime(historico[i][0], "%Y-%m-%d %H:%M:%S")
        if t2 - t1 == timedelta(minutes=1):
            consecutivos.append(historico[i])
        else:
            # quebra a sequência — começa nova
            consecutivos = [historico[i]]

    return consecutivos if len(consecutivos) >= 4 else []



def gerar_padroes(
    cores,
    tamanho_min=5,
    tamanho_max=6,
    top=30
):
    """
    Gera padrões mais fortes do histórico.
    Mantém apenas a ocorrência mais recente.
    Prioriza frequência.
    Remove padrões fracos.
    Remove conflitos de saída.
    """

    padroes = Counter()

    # =====================================
    # LEVANTAMENTO DE PADRÕES
    # =====================================

    for t in range(
        tamanho_min,
        tamanho_max + 1
    ):

        for i in range(
            len(cores) - t
        ):

            entrada = tuple(
                cores[i:i + t]
            )

            saida = (
                cores[i + t]
                if i + t < len(cores)
                else None
            )

            if saida:

                padroes[
                    (entrada, saida)
                ] += 1

    if not padroes:
        return []

    # =====================================
    # ORDENA POR FREQUÊNCIA
    # =====================================

    padroes_ordenados = sorted(
        padroes.items(),
        key=lambda x: (
            x[1],
            len(x[0][0])
        ),
        reverse=True
    )

    # =====================================
    # MANTÉM SOMENTE A MELHOR SAÍDA
    # PARA CADA ENTRADA
    # =====================================

    melhores = {}

    for (
        entrada,
        saida
    ), freq in padroes_ordenados:

        if entrada not in melhores:

            melhores[entrada] = (
                saida,
                freq
            )

    # =====================================
    # REMOVE PADRÕES FRACOS
    # =====================================

    padroes_filtrados = []

    for entrada, (
        saida,
        freq
    ) in melhores.items():

        if freq < 2:
            continue

        padroes_filtrados.append(
            (
                (entrada, saida),
                freq
            )
        )

    # =====================================
    # ORDENA NOVAMENTE
    # =====================================

    padroes_filtrados.sort(
        key=lambda x: (
            x[1],
            len(x[0][0])
        ),
        reverse=True
    )

    # =====================================
    # REMOVE DUPLICATAS DE SAÍDA
    # MANTÉM OS MAIS FORTES
    # =====================================

    resultado_final = []
    entradas_usadas = set()

    for item in padroes_filtrados:

        entrada = item[0][0]

        if entrada in entradas_usadas:
            continue

        entradas_usadas.add(
            entrada
        )

        resultado_final.append(
            item
        )

    return resultado_final[:top]

def salvar_padroes(padroes):
    """Salva padrões no arquivo seq.csv"""
    try:
        with open(SEQ_PADRAO_FILE, "w", encoding="utf-8") as f:
            f.write("[\n")
            for (entrada, saida), _ in padroes:
                entrada_fmt = ", ".join(f"\"{c}\"" for c in entrada)
                f.write(f"    ([{entrada_fmt}], \"{saida}\"),\n")
            f.write("]\n")
        print(f"✅ {len(padroes)} padrões salvos em {SEQ_PADRAO_FILE}")
    except Exception as e:
        print("Erro ao salvar padrões:", e)


if __name__ == "__main__":
    historico_completo = carregar_historico()
    historico_consecutivo = filtrar_sequencias_consecutivas(historico_completo)

    if len(historico_consecutivo) < 4:
        print("⚠️ Nenhuma sequência consecutiva suficiente encontrada.")
    else:
        # pega apenas as cores do histórico filtrado
        cores_filtradas = [c for _, c in historico_consecutivo]
        padroes = gerar_padroes(cores_filtradas)
        salvar_padroes(padroes)
