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
BOT_TOKEN = "5965310119:AAFbNw-r1UgaqMkDn0Ivx4-j-HBPgCKQgFU"

CHAT_ID = "-1003937478657"

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

resultados = []

ultima_hora_reset = datetime.now().hour

# ================= CONTROLE TENDÊNCIA =================
hora_reset_tendencia = datetime.now().hour

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

    global hora_reset_tendencia
    global historico_tendencia

    hora_atual = datetime.now().hour

    if hora_atual != hora_reset_tendencia:

        hora_reset_tendencia = hora_atual

        historico_tendencia = []

        print(f"🔄 Tendência resetada às {hora_atual}:00")


# =========================================================
# ESCOLHER IMAGEM
# =========================================================
def escolher_imagem_exata(cor):

    try:

        if cor == "AZUL" and IMAGENS_AZUL:
            return random.choice(IMAGENS_AZUL)

        if cor == "VERMELHO" and IMAGENS_VERMELHO:
            return random.choice(IMAGENS_VERMELHO)

    except Exception as e:
        print(f"⚠️ Erro imagem: {e}")

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
    confianca=None
):

    if not cor_prevista:
        return

    img_url = escolher_imagem_exata(
        cor_prevista
    )

    horario = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    mensagem = (
        f"⏰ {horario}\n"
        f"🎯 Próxima previsão: {cor_prevista}"
    )

    if codigo_previsto:

        mensagem += (
            f"\n🔑 Código previsto: "
            f"{codigo_previsto}"
        )

    if confianca is not None:

        mensagem += (
            f"\n📊 Confiança: "
            f"{confianca:.1%}"
        )

    try:

        if img_url:

            await bot.send_photo(
                chat_id=CHAT_ID,
                photo=img_url,
                caption=mensagem
            )

        else:

            await bot.send_message(
                chat_id=CHAT_ID,
                text=mensagem
            )

        print(
            f"📤 Previsão enviada: "
            f"{cor_prevista}"
        )

    except Exception as e:
        print(f"⚠️ Erro previsão: {e}")


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

        with open(
            arquivo_resultados,
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

    # =====================================================
    # ZERAR RESULTADOS A CADA HORA
    # =====================================================

    agora = datetime.now()

    hora_atual = agora.strftime("%Y-%m-%d %H")

    try:

        with open(
            arquivo_resultados,
            "r",
            encoding="utf-8"
        ) as f:

            leitor = csv.reader(f)

            linhas_csv = list(leitor)

        # =================================================
        # VERIFICA TROCA DE HORA
        # =================================================

        if len(linhas_csv) > 1:

            ultima_hora_csv = (
                linhas_csv[-1][0][:13]
            )

            if ultima_hora_csv != hora_atual:

                with open(
                    arquivo_resultados,
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

                print(
                    f"🗑️ resultados.csv resetado "
                    f"às {hora_atual}:00"
                )

    except Exception as e:

        print(
            f"⚠️ Erro reset CSV: {e}"
        )

    # =====================================================
    # SALVAR RESULTADOS
    # =====================================================

    try:

        with open(
            arquivo_resultados,
            "a",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            for cor, horario, win in resultados:

                resultado_texto = (
                    "WIN"
                    if win
                    else "LOSS"
                )

                writer.writerow([
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    cor,
                    horario,
                    resultado_texto
                ])

                print(
                    f"💾 Resultado salvo: "
                    f"{resultado_texto}"
                )

    except Exception as e:

        print(
            f"⚠️ Erro salvando CSV: {e}"
        )

    # =====================================================
    # CONTAGEM REAL DIRETO DO CSV
    # =====================================================

    wins = 0
    losses = 0

    try:

        with open(
            arquivo_resultados,
            "r",
            encoding="utf-8"
        ) as f:

            leitor = csv.DictReader(f)

            for linha in leitor:

                resultado = (
                    linha["Resultado"]
                    .strip()
                    .upper()
                )

                if resultado == "WIN":

                    wins += 1

                elif resultado == "LOSS":

                    losses += 1

        print(
            f"📊 WIN: {wins} | LOSS: {losses}"
        )

    except Exception as e:

        print(
            f"⚠️ Erro lendo CSV: {e}"
        )

    # =====================================================
    # RELATÓRIO VISUAL
    # =====================================================

    linhas = []

    for cor, horario, win in resultados:

        simbolo = (
            "✅"
            if win
            else "❌"
        )

        cor_icon = (
            "🔵"
            if cor == "AZUL"
            else "🔴"
        )

        linhas.append(
            f"{cor_icon} {cor:<8} "
            f"{horario} ➧ {simbolo}"
        )

    relatorio = (
        "━━━━━━◥◣◆◢◤━━━━━━\n"
        "PLATAFORMA PAPA JOGO\n"
        " RELATÓRIO DAS ENTRADAS\n"
        "━━━━━━◢◤◆◥◣━━━━━━\n\n"

        + "\n".join(linhas)

        + "\n\n"

        f"✅ WINS: {wins}\n"
        f"❌ LOSS: {losses}\n\n"

        " 🚀 Enquanto muitos estão testando \n"
        "sorte, aqui é resultado com estratégia!\n"
        "💹 Se ainda está só assistindo de fora… \n"
        "tá esperando o quê?\n\n"

        "🎯 plataforma PAPA JOGO https://pa3333.com/?invite_code=UPJCSWGP\n"
        "receba sinais FREE, Suporte @souza999br\n"
    )

    try:

        await bot.send_message(
            chat_id=CHAT_ID,
            text=relatorio
        )

        print("📊 Relatório enviado!")

    except Exception as e:

        print(
            f"⚠️ Relatório erro: {e}"
        )

    # =====================================================
    # LIMPA MEMÓRIA
    # =====================================================

    resultados.clear()
    
# =========================================================
# RESET
# =========================================================
async def resetar_bot():

    print("🔄 Resetando bot...")

    try:

        # =========================================
        # ENVIAR RELATÓRIO
        # =========================================
        if resultados:

            await enviar_relatorio()

            print("📊 Relatório enviado!")

    except Exception as e:

        print(f"⚠️ Erro relatório final: {e}")

    try:

        # =========================================
        # ATUALIZAR PADRÕES
        # =========================================
        subprocess.run(
            [sys.executable, "padrao.py"],
            check=True
        )

        print("✅ padrao.py executado!")

    except Exception as e:

        print(f"⚠️ Erro padrao.py: {e}")

    try:

        # =========================================
        # RESET SOMENTE DOS DADOS TEMPORÁRIOS
        # =========================================
        resultados.clear()

        historico_tendencia.clear()

        global ultima_previsao
        ultima_previsao = None

        print("✅ Dados temporários resetados!")

    except Exception as e:

        print(f"⚠️ Erro resetando memória: {e}")

    print("🚀 Bot continua rodando normalmente!")
    

# =========================================================
# LOOP PRINCIPAL
# =========================================================
async def loop_previsoes():

    global ultima_previsao
    global resultados
    global ultima_hora_reset
    global historico_tendencia
    global ultima_hora_relatorio

    print("🚀 Sistema iniciado!")

    while True:

        try:

            agora = datetime.now()

            # ================= RESET TENDÊNCIA =================
            resetar_tendencia_se_necessario()

            # ================= RESET BOT =================
            if agora.hour != ultima_hora_reset:

                ultima_hora_reset = agora.hour

                try:

        # =========================================
        # RESET APENAS DOS DADOS TEMPORÁRIOS
        # =========================================

                    historico_tendencia.clear()

                    print("✅ Reset realizado sem reiniciar o bot")

                except Exception as e:

                    print(f"⚠️ Erro reset: {e}")

            # ================= RELATÓRIO POR HORA =================
            if "ultima_hora_relatorio" not in globals():
                ultima_hora_relatorio = agora.hour

            if agora.hour != ultima_hora_relatorio:

                print(f"📊 Enviando relatório da hora {ultima_hora_relatorio:02d}...")

                if resultados:

                    await enviar_relatorio()
                    resultados.clear()

                ultima_hora_relatorio = agora.hour

            # =====================================================
            # COLETA FINAL DAS APOSTAS (57~59 SEGUNDOS)
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

            # ================= HISTÓRICO TENDÊNCIA =================
            historico_tendencia.append(
                (
                    agora.strftime("%Y-%m-%d %H:%M:%S"),
                    cor_atual,
                    codigo_atual
                )
            )

            historico_tendencia = historico_tendencia[-60:]

            historico = carregar_historico_completo()

            # ================= VALIDAR =================
            if ultima_previsao:

                # 🔥 CORREÇÃO: resultado sempre 1 ciclo atrás
                hora_ref = (agora - timedelta(minutes=1)).strftime("%H:%M")

                cor_esperada = ultima_previsao[0]

                acertou = (cor_atual == cor_esperada)

                await enviar_resultado(acertou)

                resultados.append(
                    (
                        cor_esperada,
                        hora_ref,
                        acertou
                    )
                )

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

            # ================= PREVISÃO =================
            previsao_cor = None
            previsao_codigo = None
            confianca = None

            # =====================================================
            # 1 - ANÁLISE POR PRESSÃO DAS APOSTAS
            # =====================================================
            resultado_pressao = calcular_pressao_apostas()

            if resultado_pressao:

                cor_pressao = resultado_pressao.get("cor")
                forca_pressao = resultado_pressao.get("forca")

                if cor_pressao in ["AZUL", "VERMELHO"]:

                    previsao_cor = cor_pressao
                    confianca = min(forca_pressao / 1000, 0.99)

            # =====================================================
            # 2 - PREVISÃO POR CÓDIGO
            # =====================================================
            resultado_codigo = calcular_previsao_exata(historico)

            if resultado_codigo:

                codigo_prev, cor_prev, confianca_prev = resultado_codigo

                if previsao_cor:

                    if cor_prev == previsao_cor:

                        previsao_codigo = codigo_prev
                        confianca = max(confianca or 0, confianca_prev)

                else:

                    previsao_cor = cor_prev
                    previsao_codigo = codigo_prev
                    confianca = confianca_prev

            # =====================================================
            # 3 - PREVISÃO POR COR
            # =====================================================
            resultado_cor = calcular_previsao_exata_por_cor(historico)

            if resultado_cor:

                if not previsao_cor:
                    previsao_cor = resultado_cor

            # =====================================================
            # ENVIO FINAL
            # =====================================================
            if previsao_cor:

                ultima_previsao = (previsao_cor, previsao_codigo)

                await enviar_previsao(
                    previsao_cor,
                    previsao_codigo,
                    confianca
                )

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
        .build()
    )

    app.add_handler(
        CommandHandler(
            "tendencia",
            tendencia
        )
    )

    asyncio.create_task(
        loop_previsoes()
    )

    print("🤖 Bot comandos iniciado!")

    await app.initialize()

    await app.start()

    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)


# =========================================================
# START
# =========================================================
if __name__ == "__main__":

    try:

        # =========================================
        # SEQ_HIST_FILE
        # =========================================
        if not os.path.exists(SEQ_HIST_FILE):

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

            print("✅ seq_hist criado!")

        # =========================================
        # RESULTADOS.CSV
        # =========================================
        if not os.path.exists("resultados.csv"):

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

            print("✅ resultados.csv criado!")

        # =========================================
        # SEQUENCIAS.CSV
        # =========================================
        if not os.path.exists("sequencias.csv"):

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

            print("✅ sequencias.csv criado!")

        print("📂 Sistema iniciado com histórico preservado!")

    except Exception as e:

        print(f"⚠️ Erro CSV: {e}")

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print("🛑 Bot encerrado manualmente")

    except Exception as e:

        print(f"❌ Erro fatal: {e}")