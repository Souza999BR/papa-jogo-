import asyncio
import requests
from datetime import datetime
from telegram import Bot

# Configuração do Telegram
TELEGRAM_TOKEN = "5965310119:AAFbNw-r1UgaqMkDn0Ivx4-j-HBPgCKQgFU"
CHAT_ID = "-4666794010"

bot = Bot(token=TELEGRAM_TOKEN)

API_URL = "https://game.pa3333.com/api/game/get_game?lang=pt"

def coletar_codigo():
    """
    Coleta o código da última imagem disponível na API do jogo
    """
    try:
        resp = requests.get(API_URL, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            imagens = data["data"]["issue_records_image"]
            if imagens:
                ultima = imagens[-1]  # última imagem
                return ultima.replace(".png", "")
    except Exception as e:
        print(f"❌ Erro ao coletar código da API: {e}")
    return None

async def enviar_resultado(cor_codigo):
    """
    Envia imagem + link da cor para o Telegram
    """
    url_imagem = f"https://www.pa3333.com/static/game/{cor_codigo}.png"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    legenda = f"🎲 Resultado detectado: {cor_codigo}\n🕒 {timestamp}\n🔗 {url_imagem}"

    try:
        await bot.send_photo(chat_id=CHAT_ID, photo=url_imagem, caption=legenda)
        print(f"✅ Resultado enviado: {cor_codigo}")
    except Exception as e:
        print(f"❌ Erro ao enviar para Telegram: {e}")

async def main():
    """
    Envia resultados durante 1 hora coletando da API
    """
    inicio = datetime.now()
    ultimo_codigo = None

    while (datetime.now() - inicio).seconds < 3600:  # 1 hora
        cor_codigo = coletar_codigo()
        if cor_codigo and cor_codigo != ultimo_codigo:
            await enviar_resultado(cor_codigo)
            ultimo_codigo = cor_codigo
        else:
            print("⚠ Nenhuma nova imagem encontrada.")

        await asyncio.sleep(60)  # intervalo de 1 minuto

if __name__ == "__main__":
    asyncio.run(main())
