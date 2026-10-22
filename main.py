import asyncio
import random
import csv
import subprocess
import sys
import os

from datetime import datetime, timedelta
from telegram import (
    Bot,
    Update
)

from telegram.error import TelegramError

from telegram.request import HTTPXRequest

from acessorio import ativar_previsao_acessorio

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from PIL import (
    Image,
    ImageDraw,
    ImageFont
)


from acessorio import (
    prever_proximo_acessorio,
    obter_resultado_acessorio,
    processar_validacao_acessorio,
    cancelar_previsao_acessorio,
    CODIGOS_AZUL,
    CODIGOS_VERMELHO
)



from sequencias import (
    pegar_ultima_cor,
    pegar_valores_apostas,
    calcular_pressao_apostas,
    IMAGENS_AZUL,
    IMAGENS_VERMELHO,
    SEQ_HIST_FILE,
    salvar_historico,
    calcular_previsao_exata,
    calcular_previsao_exata_por_cor
)

# ================= CONFIGURAÇÕES =================
from dotenv import load_dotenv
from modelo_numeros import numero_por_codigo, cor_por_codigo as cor_oficial_por_codigo, url_imagem
from estrategia_transicoes import prever_transicao, registrar_transicao, bloco_atual

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise RuntimeError(
        "TELEGRAM_TOKEN e CHAT_ID precisam estar definidos nas variaveis de ambiente "
        "(arquivo .env local ou nas variaveis de ambiente do Discloud)."
    )

request = HTTPXRequest(
    connect_timeout=30,
    read_timeout=30,
    write_timeout=30,
    pool_timeout=30
)

bot = Bot(
    token=BOT_TOKEN,
    request=request
)

# ================= STICKERS =================
STICKER_WIN = 'CAACAgEAAxkBAAITqGgtuzP0U5-3voB9ikh3Rw5OGqhSAALRAAPsRYBHoFAhCDLaaBY2BA'

STICKER_LOSS = 'CAACAgEAAxkBAAITqmgtvwzbwwMwZP57WU4uu45iR_2BAALCAAMHBnhH7HTVhGeXUrU2BA'

# ================= VARIÁVEIS =================
ultima_previsao = None

ultima_hora_relatorio_enviado = None

obter_resultado_acessorio()

ultima_validacao_acessorio = None

resultados = []

ultima_hora_reset = bloco_atual()

# ================= CONTROLE TENDÊNCIA =================
hora_reset_tendencia = bloco_atual()

historico_tendencia = []

# =========================================================
# HISTÓRICO
# =========================================================
def carregar_historico_completo():

    global historico_tendencia

    historico = []

    for item in historico_tendencia:

        if len(item) >= 3:

            timestamp = item[0]
            cor = item[1]
            codigo = item[2]

            if cor in ["AZUL", "VERMELHO"]:

                historico.append(
                    (
                        timestamp,
                        cor,
                        codigo
                    )
                )

    return historico


# =========================================================
# RESETAR TENDÊNCIA (A CADA HORA)
# =========================================================
def resetar_tendencia_se_necessario():
    global hora_reset_tendencia, historico_tendencia
    chave = bloco_atual()
    if hora_reset_tendencia != chave:
        hora_reset_tendencia = chave
        historico_tendencia = []
        print(f"🔄 Janela de análise reiniciada no bloco iniciado em {chave}")


# =========================================================
# LIMPAR AS 3 PRIMEIRAS HORAS DE CADA BLOCO DE 4 HORAS
# Mantém a coleta da última hora de cada bloco:
# 02:00–06:00 -> limpa às 05:00; mantém 05:00–06:00
# 06:00–10:00 -> limpa às 09:00; mantém 09:00–10:00
# Depois: 13:00, 17:00, 21:00 e 01:00
# =========================================================
def resetar_transicoes_se_necessario(agora=None):
    """Limpa transicoes.csv no início da última hora de cada bloco de 4h, preservando o cabeçalho."""
    agora = agora or datetime.now()

    # O reset ocorre somente às 01:00, 05:00, 09:00, 13:00, 17:00 e 21:00.
    # Assim, as três primeiras horas do bloco são apagadas e a última hora fica registrada.
    horas_reset = {1, 5, 9, 13, 17, 21}
    if agora.hour not in horas_reset:
        return

    chave_reset = agora.strftime("%Y-%m-%d %H:00")
    arquivo_transicoes = os.path.join(os.getcwd(), "transicoes.csv")
    marcador_reset = os.path.join(os.getcwd(), "transicoes_reset.marker")

    try:
        try:
            with open(marcador_reset, "r", encoding="utf-8") as f:
                ultimo_reset = f.read().strip()
        except FileNotFoundError:
            ultimo_reset = ""

        # Evita limpar o arquivo repetidamente durante a mesma hora.
        if ultimo_reset == chave_reset:
            return

        if os.path.exists(arquivo_transicoes):
            # Preserva a primeira linha (cabeçalho) do CSV.
            with open(arquivo_transicoes, "r", newline="", encoding="utf-8-sig") as f:
                cabecalho = f.readline()

            with open(arquivo_transicoes, "w", newline="", encoding="utf-8") as f:
                if cabecalho:
                    f.write(cabecalho)

            print(f"🧹 transicoes.csv limpo às {chave_reset}; a partir de agora serão mantidos os dados da última hora do bloco.")
        else:
            print(f"ℹ️ transicoes.csv ainda não existe; reset registrado para {chave_reset}")

        with open(marcador_reset, "w", encoding="utf-8") as f:
            f.write(chave_reset)

    except Exception as e:
        print(f"⚠️ Erro ao resetar transicoes.csv: {e}")


# =========================================================
# ESCOLHER IMAGEM
# =========================================================
def escolher_imagem_exata(cor):
    """Escolhe aleatoriamente uma imagem da cor prevista, sem alterar as análises específicas."""
    try:
        cor = str(cor or "").strip().upper()

        if cor == "AZUL":
            imagens = IMAGENS_AZUL
        elif cor == "VERMELHO":
            imagens = IMAGENS_VERMELHO
        else:
            return None

        if not imagens:
            print(f"⚠️ Não há imagens cadastradas para a cor {cor}")
            return None

        imagem = random.choice(list(imagens))
        imagem = str(imagem).strip()
        if not imagem:
            return None

        # As listas podem conter o código puro ou a URL completa da imagem.
        if imagem.lower().startswith(("http://", "https://")):
            return imagem
        return url_imagem(imagem.removesuffix(".PNG").removesuffix(".png"))

    except Exception as e:
        print(f"⚠️ Erro ao escolher imagem aleatória da cor {cor}: {e}")
    return None


# =========================================================
# GERAR IMAGEM TENDÊNCIA (6x10 + BIG ROYAL)
# =========================================================
def gerar_imagem_tendencia():

    historico = carregar_historico_completo()

    largura = 1400
    altura = 1500

    img = Image.new("RGB", (largura, altura), (15, 15, 15))
    draw = ImageDraw.Draw(img)

    try:
        fonte = ImageFont.truetype("arial.ttf", 22)
        fonte_titulo = ImageFont.truetype("arial.ttf", 38)
    except:
        fonte = ImageFont.load_default()
        fonte_titulo = ImageFont.load_default()

    draw.text((350, 20), "TENDÊNCIA DOS 60 PERÍODOS", fill="white", font=fonte_titulo)

    ultimos = historico[-60:]
    tamanho = 55
    espacamento = 8

    # =====================================================
    # 6x10 VERTICAL
    # =====================================================
    draw.text((80, 90), "GRADE VERTICAL 6x10", fill="white", font=fonte_titulo)

    inicio_x = 80
    inicio_y = 150

    idx = 0

    for col in range(10):
        for row in range(6):

            x1 = inicio_x + col * (tamanho + espacamento)
            y1 = inicio_y + row * (tamanho + espacamento)
            x2 = x1 + tamanho
            y2 = y1 + tamanho

            cor_fundo = (40, 40, 40)

            if idx < len(ultimos):

                cor = ultimos[idx][1]

                if cor == "AZUL":
                    cor_fundo = (0, 102, 255)

                elif cor == "VERMELHO":
                    cor_fundo = (255, 0, 0)

            draw.rounded_rectangle(
                [x1, y1, x2, y2],
                radius=10,
                fill=cor_fundo,
                outline=(90, 90, 90),
                width=2
            )

            if idx < len(ultimos):
                draw.text((x1 + 16, y1 + 14), str(idx + 1), fill="white", font=fonte)

            idx += 1

    # =====================================================
    # BIG ROYAL (corrigido)
    # =====================================================
    draw.text((80, 650), "BIG ROYAL", fill="white", font=fonte_titulo)

    inicio_x = 80
    inicio_y = 730

    coluna = 0
    linha = 0
    ultima_cor = None

    for idx, item in enumerate(ultimos):

        cor = item[1]

        if ultima_cor is None:
            coluna = 0
            linha = 0

        else:

            if cor == ultima_cor:
                linha += 1
                if linha >= 10:
                    linha = 9
                    coluna += 1

            else:
                coluna += 1
                linha = 0

        x1 = inicio_x + coluna * (tamanho + espacamento)
        y1 = inicio_y + linha * (tamanho + espacamento)
        x2 = x1 + tamanho
        y2 = y1 + tamanho

        cor_fundo = (0, 102, 255) if cor == "AZUL" else (255, 0, 0)

        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=10,
            fill=cor_fundo,
            outline=(90, 90, 90),
            width=2
        )

        draw.text((x1 + 16, y1 + 14), str(idx + 1), fill="white", font=fonte)

        ultima_cor = cor

    draw.text((420, 1420), f"TOTAL: {len(ultimos)}", fill="white", font=fonte_titulo)

    caminho = "tendencia.png"
    img.save(caminho)

    return caminho


# =========================================================
# COMANDO /TENDENCIA
# =========================================================
async def tendencia(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        caminho = gerar_imagem_tendencia()

        with open(caminho, "rb") as foto:
            await update.message.reply_photo(
                photo=foto,
                caption="📈 Tendência atualizada"
            )

    except Exception as e:
        print(f"❌ Erro /tendencia: {e}")
        await update.message.reply_text("❌ Erro ao gerar tendência")


# =========================================================
# PREVISÃO
# =========================================================
async def enviar_previsao(
    cor_prevista,
    codigo_previsto=None,
    confianca=None,
    acessorio=None,
    tipo_codigo="numero"
):

    if not cor_prevista:
        return False

    horario = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cor_base = (cor_prevista["cor"] if isinstance(cor_prevista, dict) else cor_prevista)
    cor_base = str(cor_base).upper()
    # Prioriza a imagem do código previsto. Se não houver código válido,
    # usa uma imagem oficial de referência da cor.
    img_url = url_imagem(codigo_previsto) if codigo_previsto else None
    if not img_url:
        img_url = escolher_imagem_exata(cor_base)
    print(f"DEBUG cor = {cor_base}; código = {codigo_previsto}; imagem = {img_url}")

    # =====================================================
    # MENSAGEM BASE
    # =====================================================
    linha_previsao = f"🎯 Próxima previsão: {cor_base}"


    mensagem = (
        f"⏰ {horario}\n"
        f"{linha_previsao}"
    )

    # =====================================================
    # CÓDIGO PREVISTO — rótulo conforme a análise que gerou o sinal
    # =====================================================
    if codigo_previsto:
        tipo_rotulo = str(tipo_codigo or "numero").strip().lower()
        if tipo_rotulo in ("acessorio", "acessório", "codigo", "código", "exata"):
            rotulo_codigo = "Código do acessório previsto"
        else:
            # A estratégia por transições prevê um número, não um acessório.
            rotulo_codigo = "Código do número previsto"
        mensagem += f"\n🔑 {rotulo_codigo}: {codigo_previsto}"

    # =====================================================
    # CONFIANÇA
    # =====================================================
    if confianca is not None:
        mensagem += f"\n📊 Confiança: {confianca:.1%}"

    # =====================================================
    # ENVIO ROBUSTO
    # Uma falha ao carregar a imagem não pode bloquear o sinal.
    # =====================================================
    if img_url:
        try:
            await bot.send_photo(
                chat_id=CHAT_ID,
                photo=img_url,
                caption=mensagem
            )
            print(f"📤 Previsão enviada com imagem: {cor_base}")
            return True
        except TelegramError as erro_foto:
            print(f"⚠️ Falha ao enviar imagem da previsão: {erro_foto}")
        except Exception as erro_foto:
            print(f"⚠️ Erro inesperado ao enviar imagem: {erro_foto}")

    # Se a foto falhar ou não existir, envia a previsão como texto.
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=mensagem
        )
        print(f"📤 Previsão enviada como texto: {cor_base}")
        return True
    except TelegramError as erro_texto:
        print(f"❌ Telegram recusou o envio da previsão em texto: {erro_texto}")
    except Exception as erro_texto:
        print(f"❌ Erro inesperado ao enviar previsão em texto: {erro_texto}")

    return False
        
# =========================================================
# RESULTADO
# =========================================================
async def enviar_resultado(acertou):

    try:

        sticker = (
            STICKER_WIN
            if acertou
            else STICKER_LOSS
        )

        await bot.send_sticker(
            chat_id=CHAT_ID,
            sticker=sticker
        )

    except Exception as e:
        print(f"⚠️ Erro sticker: {e}")


# =========================================================
# RELATÓRIO
# =========================================================
async def enviar_relatorio():

    global resultados

    arquivo_resultados = "resultados.csv"

    # =====================================================
    # CRIAR CSV CASO NÃO EXISTA
    # =====================================================
    if not os.path.exists(arquivo_resultados):

        with open(arquivo_resultados, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestamp",
                "Cor",
                "Horario",
                "Resultado"
            ])

    # =====================================================
    # RESET POR HORA
    # =====================================================
    agora = datetime.now()
    hora_atual = agora.strftime("%Y-%m-%d %H")

    try:

        with open(arquivo_resultados, "r", encoding="utf-8") as f:
            leitor = csv.reader(f)
            linhas_csv = list(leitor)

        # Mantém o CSV até o relatório ser entregue com sucesso.
        # O arquivo não é apagado aqui: se o Telegram falhar na virada
        # da hora, o bot precisa conseguir reenviar o mesmo placar.

    except Exception as e:
        print(f"⚠️ Erro reset CSV: {e}")

    # =====================================================
    # SALVAR RESULTADOS
    # =====================================================
    try:

        # Evita gravar duplicados se o Telegram falhar e o relatório
        # precisar ser tentado novamente.
        existentes = set()
        try:
            with open(arquivo_resultados, "r", newline="", encoding="utf-8") as f:
                leitor_existente = csv.DictReader(f)
                for linha in leitor_existente:
                    existentes.add((
                        str(linha.get("Cor", "")).strip(),
                        str(linha.get("Horario", "")).strip(),
                        str(linha.get("Resultado", "")).strip().upper(),
                    ))
        except Exception:
            pass

        with open(arquivo_resultados, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            for item in resultados:
                if not item or len(item) < 3:
                    continue

                cor = item[0]
                horario = item[1]
                win = item[2]
                if isinstance(cor, dict):
                    cor = cor.get("cor", "DESCONHECIDO")

                cor = str(cor)
                horario = str(horario)
                resultado_texto = "WIN" if win else "LOSS"
                chave = (cor, horario, resultado_texto)
                if chave in existentes:
                    continue

                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    cor,
                    horario,
                    resultado_texto
                ])
                existentes.add(chave)
                print(f"💾 Resultado salvo: {resultado_texto}")

    except Exception as e:
        print(f"⚠️ Erro salvando CSV: {e}")

    # =====================================================
    # CONTAGEM REAL DO CSV
    # =====================================================
    wins = 0
    losses = 0

    try:

        with open(arquivo_resultados, "r", encoding="utf-8") as f:

            leitor = csv.DictReader(f)

            for linha in leitor:

                resultado = linha["Resultado"].strip().upper()

                if resultado == "WIN":
                    wins += 1

                elif resultado == "LOSS":
                    losses += 1

        print(f"📊 WIN: {wins} | LOSS: {losses}")

    except Exception as e:
        print(f"⚠️ Erro lendo CSV: {e}")

    # =====================================================
    # ACESSÓRIOS
    # =====================================================
    try:

        acc = obter_resultado_acessorio()

        acessorio_wins = acc.get("wins", 0)
        acessorio_losses = acc.get("loss", 0)

    except Exception as e:

        print(f"⚠️ Erro acessório: {e}")

        acessorio_wins = 0
        acessorio_losses = 0

    # =====================================================
    # RELATÓRIO VISUAL (LENDO CSV)
    # =====================================================
    linhas = []

    try:

        with open(arquivo_resultados, "r", encoding="utf-8") as f:

            leitor = csv.DictReader(f)

            for linha in leitor:

                cor = str(linha["Cor"]).strip()
                horario = str(linha["Horario"]).strip()
                resultado = str(linha["Resultado"]).strip().upper()

                # =========================================
                # CORRIGE REGISTROS ANTIGOS COM DICT
                # =========================================
                if "AZUL" in cor:
                    cor = "AZUL"

                elif "VERMELHO" in cor:
                    cor = "VERMELHO"

                simbolo = "✅" if resultado == "WIN" else "❌"

                cor_icon = (
                    "🔵"
                    if cor == "AZUL"
                    else "🔴"
                )

                linhas.append(
                    f"{cor_icon} {cor:<8} {horario} ➧ {simbolo}"
                )

    except Exception as e:

        print(f"⚠️ Erro montando relatório: {e}")

    # =====================================================
    # RELATÓRIO FINAL
    # =====================================================
    relatorio = (
        "━━━━━━◥◣◆◢◤━━━━━━\n"
        "PLATAFORMA PAPA JOGO\n"
        " RELATÓRIO DAS ENTRADAS\n"
        "━━━━━━◢◤◆◥◣━━━━━━\n\n"

        + "\n".join(linhas)

        + "\n\n"

        f"✅ WINS: {wins}\n"
        f"❌ LOSS: {losses}\n\n"

        "🎩 RESULTADO ACESSÓRIOS\n"
        f"✅ WINS: {acessorio_wins}\n"
        f"❌ LOSS: {acessorio_losses}\n\n"

        "🚀 Enquanto muitos estão testando estratégia, aqui é resultado real!\n"
        "💹 Se ainda está só assistindo… tá perdendo oportunidade.\n\n"

        "🎯 plataforma PAPA JOGO https://pa3333.com/?invite_code=UPJCSWGP\n"
        "Suporte @souza999br\n"
    )

    enviado = False
    for tentativa in range(1, 4):
        try:
            await bot.send_message(
                chat_id=CHAT_ID,
                text=relatorio
            )
            print(f"📊 Relatório enviado ao Telegram (tentativa {tentativa}/3).")
            enviado = True
            break
        except Exception as e:
            print(f"⚠️ Falha ao enviar relatório (tentativa {tentativa}/3): {e}")
            if tentativa < 3:
                await asyncio.sleep(2)

    # Só limpa as previsões da memória após confirmação do envio.
    # Se as 3 tentativas falharem, o loop horário tentará novamente.
    if enviado:
        resultados.clear()

    return enviado
    
# =========================================================
# RESET
# =========================================================
async def resetar_bot():

    print("🔄 Resetando bot...")

    try:
        await enviar_relatorio()

    except Exception as e:
        print(f"⚠️ Erro relatório final: {e}")

    try:

        subprocess.run(
            [sys.executable, "padrao.py"],
            check=True
        )

    except Exception as e:
        print(f"⚠️ Erro padrao.py: {e}")

    print("♻️ Reiniciando processo...")

    os.execv(
        sys.executable,
        [sys.executable] + sys.argv
    )

# =========================================================
# LOOP PRINCIPAL
# =========================================================
async def loop_previsoes():

    global ultima_previsao
    global resultados
    global ultima_hora_reset
    global historico_tendencia
    global ultima_hora_relatorio
    global ultima_validacao_acessorio

    print("🚀 Sistema iniciado!")

    while True:

        try:

            agora = datetime.now()

            # ================= LIMPEZA DAS 3 PRIMEIRAS HORAS DO BLOCO =================
            resetar_transicoes_se_necessario(agora)

            # ================= RESET TENDÊNCIA =================
            resetar_tendencia_se_necessario()

            # ================= RESET BOT =================
            bloco_reset = bloco_atual()
            if bloco_reset != ultima_hora_reset:
                ultima_hora_reset = bloco_reset
                await resetar_bot()

            # ================= RELATÓRIO POR HORA =================
            if "ultima_hora_relatorio" not in globals():
                ultima_hora_relatorio = agora.hour

            if agora.hour != ultima_hora_relatorio:
                print(f"📊 Enviando placar da hora {ultima_hora_relatorio:02d}...")

                # Envia mesmo que a lista esteja vazia, para não perder
                # o placar da hora. Só avança a hora quando Telegram confirmar.
                relatorio_enviado = await enviar_relatorio()
                if relatorio_enviado:
                    ultima_hora_relatorio = agora.hour
                else:
                    print("⚠️ Placar não confirmado pelo Telegram; nova tentativa em breve.")
                    await asyncio.sleep(5)
                    continue

            # =====================================================
            # COLETA FINAL DAS APOSTAS
            # =====================================================
            segundos = agora.second

            if segundos >= 57:
                print("📊 Coletando apostas finais do minuto...")
                pegar_valores_apostas()

            # ================= RESULTADO =================
            resultado = pegar_ultima_cor()

            if not resultado:
                await asyncio.sleep(5)
                continue

            cor_atual, codigo_atual = resultado

            if cor_atual not in ["AZUL", "VERMELHO"]:
                await asyncio.sleep(5)
                continue

            salvar_historico(cor_atual, codigo_atual)

            # ================= HISTÓRICO =================
            historico_tendencia.append(
                (
                    agora.strftime("%Y-%m-%d %H:%M:%S"),
                    cor_atual,
                    codigo_atual
                )
            )

            historico_tendencia = historico_tendencia[-60:]

            historico = carregar_historico_completo()
            registrar_transicao(historico, agora.strftime("%Y-%m-%d %H:%M:%S"))

            # ================= VALIDAR RESULTADO =================
            if ultima_previsao:

                hora_ref = (agora - timedelta(minutes=1)).strftime("%H:%M")

                cor_esperada = ultima_previsao.get("cor")

                acertou = (cor_atual == cor_esperada)

                await enviar_resultado(acertou)

                resultados.append(
                    (cor_esperada, hora_ref, acertou)
                )

                # ================= VALIDAÇÃO ACESSÓRIO =================
                try:
                    chave_validacao = (
                        agora.strftime("%Y-%m-%d %H:%M"),
                        codigo_atual
                    )
                    if chave_validacao != ultima_validacao_acessorio:
                        processar_validacao_acessorio()
                        ultima_validacao_acessorio = chave_validacao
                        
                except Exception as e:
                    print(f"⚠️ Erro validação acessório: {e}")

                # ================= SALVAR CSV =================
                try:

                    arquivo_resultados = "resultados.csv"

                    if not os.path.exists(arquivo_resultados):
                        with open(arquivo_resultados, "w", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)
                            writer.writerow(["Timestamp", "Cor", "Horario", "Resultado"])

                    with open(arquivo_resultados, "a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            agora.strftime("%Y-%m-%d %H:%M:%S"),
                            cor_esperada,
                            hora_ref,
                            "WIN" if acertou else "LOSS"
                        ])

                except Exception as e:
                    print(f"⚠️ Erro salvando resultado: {e}")

                ultima_previsao = None

            # ================= PREVISÕES =================
            # Executa as duas estratégias independentes. Se ambas gerarem
            # sinal no mesmo ciclo, a previsão por CÓDIGO tem prioridade.
            previsao_cor = None
            previsao_codigo = None
            confianca = None
            tipo_previsao = "numero"
            previsao_transicao_cor = None
            previsao_transicao_codigo = None
            confianca_transicao = None

            # =====================================================
            # 1 - PRESSÃO (mantida como alternativa)
            # =====================================================
            resultado_pressao = calcular_pressao_apostas()
            if resultado_pressao:
                cor_pressao = resultado_pressao.get("cor")
                forca_pressao = resultado_pressao.get("forca")
                if cor_pressao in ["AZUL", "VERMELHO"]:
                    previsao_cor = cor_pressao
                    try:
                        confianca = min(float(forca_pressao) / 1000, 0.99)
                    except (TypeError, ValueError):
                        confianca = None

            # =====================================================
            # 2 - PREVISÃO POR CÓDIGO (PRIORIDADE MÁXIMA)
            # =====================================================
            resultado_codigo = calcular_previsao_exata(historico)
            if resultado_codigo:
                try:
                    codigo_prev, cor_prev, confianca_prev = resultado_codigo[:3]
                    cor_prev = str(cor_prev).upper() if cor_prev else None
                    if codigo_prev and cor_prev in ("AZUL", "VERMELHO"):
                        previsao_codigo = str(codigo_prev).strip().upper()
                        previsao_cor = cor_prev
                        confianca = confianca_prev
                        # calcular_previsao_exata gera o código do acessório.
                        tipo_previsao = "acessorio"
                        print(f"🔑 Prioridade código/acessório: {previsao_codigo} ({previsao_cor})")
                except (TypeError, ValueError, IndexError) as e:
                    print(f"⚠️ Retorno da previsão por código inválido: {e}")

            # =====================================================
            # 3 - PREVISÃO POR TRANSIÇÃO (USADA SE CÓDIGO NÃO EXISTIR)
            # =====================================================
            try:
                resultado_transicao = prever_transicao(historico)
                if resultado_transicao:
                    if isinstance(resultado_transicao, dict):
                        previsao_transicao_codigo = (
                            resultado_transicao.get("codigo")
                            or resultado_transicao.get("codigo_previsto")
                            or resultado_transicao.get("codigo_numero")
                        )
                        previsao_transicao_cor = (
                            resultado_transicao.get("cor")
                            or resultado_transicao.get("cor_prevista")
                        )
                        confianca_transicao = (
                            resultado_transicao.get("confianca")
                            or resultado_transicao.get("confidence")
                        )
                        numero_transicao = (
                            resultado_transicao.get("numero")
                            or resultado_transicao.get("numero_previsto")
                        )
                        if not previsao_transicao_codigo and numero_transicao:
                            # Não inventa código de acessório: a transição é por número.
                            previsao_transicao_codigo = None
                            if not previsao_transicao_cor:
                                try:
                                    previsao_transicao_cor = "VERMELHO" if int(numero_transicao) % 2 else "AZUL"
                                except (TypeError, ValueError):
                                    pass
                    elif isinstance(resultado_transicao, (tuple, list)):
                        if len(resultado_transicao) >= 3:
                            primeiro, segundo, terceiro = resultado_transicao[:3]
                            # Formato comum: (código, cor, confiança) ou (número, cor, confiança).
                            if isinstance(segundo, str) and segundo.upper() in ("AZUL", "VERMELHO"):
                                previsao_transicao_cor = segundo.upper()
                                confianca_transicao = terceiro
                                valor = str(primeiro).strip().upper()
                                if len(valor) >= 20 and all(c in "0123456789ABCDEF" for c in valor):
                                    previsao_transicao_codigo = valor
                                else:
                                    try:
                                        numero_transicao = int(primeiro)
                                        previsao_transicao_cor = "VERMELHO" if numero_transicao % 2 else "AZUL"
                                    except (TypeError, ValueError):
                                        pass
                    if previsao_transicao_cor:
                        previsao_transicao_cor = str(previsao_transicao_cor).upper()
                        if previsao_transicao_cor not in ("AZUL", "VERMELHO"):
                            previsao_transicao_cor = None
                    if previsao_transicao_codigo:
                        previsao_transicao_codigo = str(previsao_transicao_codigo).strip().upper()
            except Exception as e:
                print(f"⚠️ Erro na previsão por transição: {e}")

            # Código vence se as duas estratégias sinalizarem simultaneamente.
            if not previsao_codigo and previsao_transicao_cor:
                previsao_cor = previsao_transicao_cor
                previsao_codigo = previsao_transicao_codigo
                confianca = confianca_transicao
                tipo_previsao = "transicao"
                print("🔁 Usando previsão por transição (sem previsão válida por código).")

            # =====================================================
            # 4 - COR (fallback; preservado)
            # =====================================================
            resultado_cor = calcular_previsao_exata_por_cor(historico)
            if resultado_cor and not previsao_cor:
                previsao_cor = resultado_cor.get("cor")

            # =====================================================
            # ENVIO FINAL
            # =====================================================
            if previsao_cor:

                acessorio_previsto = None

                try:

                    usar_acessorio = True

                    if (
                        previsao_codigo
                        and confianca is not None
                        and confianca >= 0.74
                    ):
                        usar_acessorio = False

                        print(
                            f"🔑 Código forte detectado ({confianca:.1%}) - acessório bloqueado"
                        )
                        
                        cancelar_previsao_acessorio()

                    if usar_acessorio:

                        resultado_acessorio = prever_proximo_acessorio()

                        print(f"DEBUG ACESSÓRIO: {resultado_acessorio}")

                        if resultado_acessorio:
                            acessorio_previsto = resultado_acessorio.get("acessorio")

                            if acessorio_previsto == "DESCONHECIDO":
                                acessorio_previsto = None

                except Exception as e:
                    print(f"⚠️ Erro previsão acessório: {e}")

                # Só registra a previsão para o placar se o Telegram confirmar
                # o envio da foto ou da mensagem de texto.
                enviado_telegram = await enviar_previsao(
                    previsao_cor,
                    previsao_codigo,
                    confianca,
                    acessorio_previsto,
                    tipo_codigo=tipo_previsao
                )

                if enviado_telegram:
                    ultima_previsao = {
                        "cor": previsao_cor,
                        "codigo": previsao_codigo,
                        "enviada_telegram": True
                    }
                    print("✅ Previsão registrada para validação e placar: enviada ao Telegram.")

                    if usar_acessorio and acessorio_previsto:
                        ativar_previsao_acessorio()
                else:
                    ultima_previsao = None
                    print("⚠️ Previsão não enviada ao Telegram; não será incluída no placar.")

            # ================= ESPERA =================
            proximo = (agora + timedelta(minutes=1)).replace(
                second=15,
                microsecond=0
            )

            tempo = (proximo - agora).total_seconds()

            if tempo <= 0:
                proximo += timedelta(minutes=1)
                tempo = (proximo - agora).total_seconds()

            print(f"⏳ Esperando {tempo:.1f}s")

            await asyncio.sleep(tempo)

        except Exception as e:
            print(f"❌ Erro loop: {e}")
            await asyncio.sleep(5)
            
# =========================================================
# MAIN
# =========================================================
async def main():

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .request(request)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "tendencia",
            tendencia
        )
    )

    # =====================================================
    # INICIALIZA O BOT ANTES DE ALTERAR O WEBHOOK
    # =====================================================
    await app.initialize()

    # =====================================================
    # REMOVE WEBHOOK ANTES DO POLLING
    #
    # O Telegram nao permite getUpdates (polling) enquanto
    # existir um webhook ativo para o mesmo bot.
    # Fazemos a remocao e confirmamos o estado antes de
    # iniciar o updater. Isso evita o Conflict no Discloud.
    # =====================================================
    webhook_removido = False

    for tentativa in range(1, 4):

        try:
            webhook_info = await app.bot.get_webhook_info()
            webhook_url = webhook_info.url or ""

            if webhook_url:
                print(
                    f"⚠️ Webhook ativo detectado "
                    f"(tentativa {tentativa}/3): {webhook_url}"
                )
            else:
                print(
                    f"ℹ️ Nenhum webhook ativo "
                    f"(tentativa {tentativa}/3)."
                )

            await app.bot.delete_webhook(
                drop_pending_updates=True
            )

            # Confirma que o Telegram realmente ficou sem webhook.
            webhook_check = await app.bot.get_webhook_info()

            if not webhook_check.url:
                webhook_removido = True
                print("✅ Webhook removido. Polling liberado.")
                break

            print(
                "⚠️ O webhook ainda aparece ativo. "
                "Tentando novamente..."
            )

        except Exception as e:

            print(
                f"⚠️ Erro ao remover webhook "
                f"(tentativa {tentativa}/3): {e}"
            )

        if tentativa < 3:
            await asyncio.sleep(2)

    if not webhook_removido:
        print(
            "❌ Não foi possível confirmar a remoção do webhook. "
            "O polling não será iniciado para evitar conflito com o Telegram."
        )

        await app.shutdown()
        return

    # =====================================================
    # INICIA A APLICAÇÃO
    # =====================================================
    await app.start()

    # =====================================================
    # INICIA O POLLING SOMENTE DEPOIS DO WEBHOOK REMOVIDO
    # =====================================================
    await app.updater.start_polling(
        drop_pending_updates=True
    )

    print("🤖 Bot comandos iniciado!")
    print("📡 Polling iniciado com sucesso!")

    # =====================================================
    # LOOP DE PREVISÕES
    # =====================================================
    asyncio.create_task(
        loop_previsoes()
    )

    # =====================================================
    # MANTÉM O PROCESSO ATIVO NO DISCLOUD
    # =====================================================
    try:

        while True:
            await asyncio.sleep(3600)

    except asyncio.CancelledError:

        print("🛑 Encerrando bot...")

        try:
            await app.updater.stop()
        except Exception:
            pass

        try:
            await app.stop()
        except Exception:
            pass

        try:
            await app.shutdown()
        except Exception:
            pass

        raise

# =========================================================
# START
# =========================================================
if __name__ == "__main__":

    try:

        # =========================================
        # SEQ_HIST_FILE
        # =========================================
        with open(
            SEQ_HIST_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            writer.writerow([
                "Timestamp",
                "Cor",
                "Codigo"
            ])

        # =========================================
        # RESULTADOS.CSV
        # =========================================
        with open(
            "resultados.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            writer.writerow([
                "Timestamp",
                "Cor",
                "Horario",
                "Resultado"
            ])

        # =========================================
        # SEQUENCIAS.CSV
        # =========================================
        with open(
            "sequencias.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            writer.writerow([
                "Timestamp",
                "Cor",
                "Codigo"
            ])

        print("📂 CSVs resetados!")

    except Exception as e:

        print(f"⚠️ Erro CSV: {e}")

    asyncio.run(main())