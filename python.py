import datetime
import json
import math
import os
import platform
import random
import subprocess
import sys
import time
from io import BytesIO

import qrcode
import requests
from PIL import Image, ImageDraw, ImageFont
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

# ============================================================================
# 🎨 BANNER Y COLORES
# ============================================================================
BANNER_URL = "https://media.discordapp.net/attachments/1510358661065605372/1522172755234127942/standard13.gif"

# Colores para degradados (usando emojis)
GRADIENT_START = "🟣"
GRADIENT_MID = "🟦"
GRADIENT_END = "🟧"


# ============================================================================
# 🤖 FUNCIONES DE FORMATO
# ============================================================================
def gradient_text(text, start=GRADIENT_START, mid=GRADIENT_MID, end=GRADIENT_END):
    """Crea texto con efecto de degradado"""
    length = len(text)
    gradient = []
    for i in range(length):
        if i < length // 3:
            gradient.append(start)
        elif i < 2 * length // 3:
            gradient.append(mid)
        else:
            gradient.append(end)
    return "".join(gradient) + text


def header(text):
    """Encabezado con degradado"""
    return f"{GRADIENT_START}{GRADIENT_MID}{GRADIENT_END} {text} {GRADIENT_END}{GRADIENT_MID}{GRADIENT_START}"


def bold(text):
    """Texto en negrita"""
    return f"<b>{text}</b>"


def italic(text):
    """Texto en cursiva"""
    return f"<i>{text}</i>"


def code(text):
    """Texto en código"""
    return f"<code>{text}</code>"


# ============================================================================
# 🎯 COMANDOS DEL BOT
# ============================================================================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    keyboard = [
        [InlineKeyboardButton("📋 Comandos", callback_data="help")],
        [InlineKeyboardButton("🎲 Diversión", callback_data="fun")],
        [InlineKeyboardButton("🔧 Utilidades", callback_data="utils")],
        [InlineKeyboardButton("ℹ️ Información", callback_data="info")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    banner_text = header("AstroX Development")
    await update.message.reply_photo(
        photo=BANNER_URL,
        caption=f"{banner_text}\n\n"
        f"{bold('¡Bienvenido al Bot de Telegram!')}\n\n"
        f"Usa /help para ver todos los comandos o selecciona una categoría:",
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help - Lista todos los comandos"""
    commands = {
        "📋 Básicos": [
            "/start - Iniciar bot",
            "/help - Lista de comandos",
            "/ping - Comprueba si el bot está activo",
            "/echo [texto] - Repite tu mensaje",
            "/id - Muestra tu ID de usuario",
        ],
        "🕒 Tiempo/Fecha": [
            "/time - Hora actual",
            "/date - Fecha actual",
            "/countdown [fecha] - Cuenta regresiva a una fecha (DD/MM/YYYY)",
            "/timer [segundos] - Temporizador",
        ],
        "🎲 Diversión": [
            "/8ball [pregunta] - Pregunta a la bola 8",
            "/dice - Tira un dado",
            "/coin - Lanzar moneda",
            "/joke - Chiste aleatorio",
            "/meme - Meme aleatorio",
            "/cat - Imagen de gato aleatorio",
            "/dog - Imagen de perro aleatorio",
        ],
        "🔢 Matemáticas": [
            "/calc [expresión] - Calculadora",
            "/sqrt [número] - Raíz cuadrada",
            "/pow [base] [exponente] - Potencia",
            "/random [min] [max] - Número aleatorio",
        ],
        "🔧 Utilidades": [
            "/qr [texto] - Genera código QR",
            "/short [url] - Acortar URL",
            "/weather [ciudad] - Clima",
            "/ip - Muestra tu IP pública",
            "/bin [texto] - Codifica a binario",
            "/hex [texto] - Codifica a hexadecimal",
        ],
        "💻 Sistema": [
            "/system - Información del sistema",
            "/python - Versión de Python",
            "/pingdb - Ping a base de datos (simulado)",
            "/speedtest - Test de velocidad",
        ],
        "🎨 Estilo": [
            "/bold [texto] - Texto en negrita",
            "/italic [texto] - Texto en cursiva",
            "/code [texto] - Texto en código",
            "/gradient [texto] - Texto con degradado",
        ],
    }

    message = header("📋 Lista de Comandos") + "\n\n"
    for category, cmds in commands.items():
        message += f"{bold(category)}:\n"
        for cmd in cmds:
            message += f"  {code(cmd)}\n"
        message += "\n"

    await update.message.reply_text(message, parse_mode="HTML")


# ============================================================================
# 📊 COMANDOS BÁSICOS
# ============================================================================
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ping"""
    start_time = time.time()
    await update.message.reply_text("🏓 Pong!")
    end_time = time.time()
    latency = (end_time - start_time) * 1000
    await update.message.reply_text(f"⏱️ Latencia: {latency:.2f}ms", parse_mode="HTML")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /echo"""
    if not context.args:
        await update.message.reply_text("❌ Proporciona un texto para repetir.")
        return
    text = " ".join(context.args)
    await update.message.reply_text(f"{bold('Echo:')} {text}", parse_mode="HTML")


async def user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /id"""
    user = update.effective_user
    await update.message.reply_text(
        f"{bold('Tu ID:')} {code(str(user.id))}\n"
        f"{bold('Nombre:')} {user.first_name}\n"
        f"{bold('Usuario:')} @{user.username or 'N/A'}",
        parse_mode="HTML",
    )


# ============================================================================
# ⏰ COMANDOS DE TIEMPO
# ============================================================================
async def current_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /time"""
    ahora = datetime.datetime.now().strftime("%H:%M:%S")
    fecha = datetime.datetime.now().strftime("%d/%m/%Y")
    await update.message.reply_text(
        f"{header('🕒 Hora Actual')}\n\n"
        f"{bold('Hora:')} {code(ahora)}\n"
        f"{bold('Fecha:')} {code(fecha)}",
        parse_mode="HTML",
    )


async def current_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /date"""
    fecha = datetime.datetime.now().strftime("%A, %d de %B de %Y")
    await update.message.reply_text(
        f"{header('📅 Fecha Actual')}\n\n{bold('Fecha:')} {code(fecha)}",
        parse_mode="HTML",
    )


async def countdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /countdown [DD/MM/YYYY]"""
    if not context.args:
        await update.message.reply_text("❌ Proporciona una fecha (DD/MM/YYYY).")
        return

    try:
        date_str = context.args[0]
        target_date = datetime.datetime.strptime(date_str, "%d/%m/%Y")
        now = datetime.datetime.now()
        delta = target_date - now

        if delta.total_seconds() < 0:
            await update.message.reply_text("❌ La fecha ya pasó.")
            return

        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        await update.message.reply_text(
            f"{header('⏳ Cuenta Regresiva')}\n\n"
            f"{bold('Fecha objetivo:')} {code(date_str)}\n"
            f"{bold('Tiempo restante:')} {days}d {hours}h {minutes}m {seconds}s",
            parse_mode="HTML",
        )
    except ValueError:
        await update.message.reply_text("❌ Formato de fecha inválido. Usa DD/MM/YYYY.")


async def timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /timer [segundos]"""
    if not context.args:
        await update.message.reply_text("❌ Proporciona segundos para el temporizador.")
        return

    try:
        seconds = int(context.args[0])
        if seconds <= 0:
            await update.message.reply_text("❌ Los segundos deben ser mayores a 0.")
            return

        await update.message.reply_text(
            f"⏳ Temporizador de {seconds} segundos iniciado..."
        )
        time.sleep(seconds)
        await update.message.reply_text(
            f"⏰ ¡Tiempo terminado después de {seconds} segundos!"
        )
    except ValueError:
        await update.message.reply_text("❌ Proporciona un número válido de segundos.")


# ============================================================================
# 🎲 COMANDOS DE DIVERSIÓN
# ============================================================================
async def eight_ball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /8ball [pregunta]"""
    if not context.args:
        await update.message.reply_text("❌ Haz una pregunta a la bola 8.")
        return

    question = " ".join(context.args)
    answers = [
        "✅ Sí",
        "❌ No",
        "🤷 Tal vez",
        "⏳ Pregunta más tarde",
        "💯 Definitivamente sí",
        "🚫 Definitivamente no",
        "🌟 Las señales apuntan a que sí",
        "🌑 Las señales apuntan a que no",
        "🔮 No cuentes con ello",
        "🎯 Puedes contar con ello",
        "🌊 Mi respuesta es no",
        "🌈 Mi respuesta es sí",
        "🤔 Concentrate y pregunta de nuevo",
    ]
    answer = random.choice(answers)
    await update.message.reply_text(
        f"{header('🎱 Bola 8 Mágica')}\n\n"
        f"{bold('Pregunta:')} {italic(question)}\n"
        f"{bold('Respuesta:')} {answer}",
        parse_mode="HTML",
    )


async def dice_roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /dice"""
    result = random.randint(1, 6)
    await update.message.reply_text(
        f"{header('🎲 Dado')}\n\n🎲 Tiraste un dado y salió: {bold(str(result))}",
        parse_mode="HTML",
    )


async def coin_flip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /coin"""
    result = random.choice(["🪙 Cara", "⚪ Cruz"])
    await update.message.reply_text(
        f"{header('🪙 Moneda')}\n\n💰 La moneda cayó en: {bold(result)}",
        parse_mode="HTML",
    )


async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /joke"""
    jokes = [
        "¿Qué le dice un semáforo a otro? No me mires, que me estoy cambiando.",
        "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
        "¿Por qué los libros de terror siempre tienen frío? Porque tienen muchas páginas.",
        "¿Qué le dice un árbol a otro? ¡Qué hoja pasa!",
        "¿Cómo se despiden los químicos? Ácido un placer.",
        "¿Qué hace una impresora en el gimnasio? ¡Im-primir!",
    ]
    joke = random.choice(jokes)
    await update.message.reply_text(
        f"{header('😂 Chiste')}\n\n{italic(joke)}", parse_mode="HTML"
    )


async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /meme - Meme aleatorio de Reddit"""
    try:
        subreddits = ["memes", "dankmemes", "me_irl", "memeeconomy"]
        subreddit = random.choice(subreddits)
        response = requests.get(
            f"https://meme-api.com/gimme/{subreddit}",
            headers={"User-Agent": "AstroXBot/1.0"},
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("url"):
                await update.message.reply_photo(photo=data["url"])
            else:
                await update.message.reply_text("❌ No se pudo obtener un meme.")
        else:
            await update.message.reply_text("❌ Error al obtener meme.")
    except:
        await update.message.reply_text("❌ Error de conexión.")


async def cat_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /cat - Imagen de gato aleatorio"""
    try:
        response = requests.get("https://api.thecatapi.com/v1/images/search")
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                await update.message.reply_photo(photo=data[0]["url"])
            else:
                await update.message.reply_text("❌ No se pudo obtener imagen de gato.")
        else:
            await update.message.reply_text("❌ Error al obtener imagen de gato.")
    except:
        await update.message.reply_text("❌ Error de conexión.")


async def dog_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /dog - Imagen de perro aleatorio"""
    try:
        response = requests.get("https://api.thedogapi.com/v1/images/search")
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                await update.message.reply_photo(photo=data[0]["url"])
            else:
                await update.message.reply_text(
                    "❌ No se pudo obtener imagen de perro."
                )
        else:
            await update.message.reply_text("❌ Error al obtener imagen de perro.")
    except:
        await update.message.reply_text("❌ Error de conexión.")


# ============================================================================
# 🔢 COMANDOS DE MATEMÁTICAS
# ============================================================================
async def calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /calc [expresión]"""
    if not context.args:
        await update.message.reply_text("❌ Proporciona una expresión matemática.")
        return

    expression = " ".join(context.args)
    try:
        # Reemplazar símbolos comunes
        expression = expression.replace("x", "*").replace("X", "*")
        result = eval(expression)
        await update.message.reply_text(
            f"{header('🧮 Calculadora')}\n\n"
            f"{bold('Expresión:')} {code(expression)}\n"
            f"{bold('Resultado:')} {code(str(result))}",
            parse_mode="HTML",
        )
    except:
        await update.message.reply_text("❌ Expresión matemática inválida.")


async def square_root(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /sqrt [número]"""
    if not context.args:
        await update.message.reply_text("❌ Proporciona un número.")
        return

    try:
        num = float(context.args[0])
        if num < 0:
            await update.message.reply_text(
                "❌ No se puede calcular la raíz de un número negativo."
            )
            return
        result = math.sqrt(num)
        await update.message.reply_text(
            f"{header('√ Raíz Cuadrada')}\n\n"
            f"{bold('Número:')} {code(str(num))}\n"
            f"{bold('Raíz:')} {code(str(result))}",
            parse_mode="HTML",
        )
    except ValueError:
        await update.message.reply_text("❌ Número inválido.")


async def power(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /pow [base] [exponente]"""
    if len(context.args) < 2:
        await update.message.reply_text("❌ Proporciona base y exponente.")
        return

    try:
        base = float(context.args[0])
        exponent = float(context.args[1])
        result = math.pow(base, exponent)
        await update.message.reply_text(
            f"{header('^ Potencia')}\n\n"
            f"{bold('Base:')} {code(str(base))}\n"
            f"{bold('Exponente:')} {code(str(exponent))}\n"
            f"{bold('Resultado:')} {code(str(result))}",
            parse_mode="HTML",
        )
    except ValueError:
        await update.message.reply_text("❌ Números inválidos.")


async def random_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /random [min] [max]"""
    if len(context.args) < 2:
        await update.message.reply_text("❌ Proporciona minimo y máximo.")
        return

    try:
        min_val = int(context.args[0])
        max_val = int(context.args[1])
        if min_val > max_val:
            min_val, max_val = max_val, min_val
        result = random.randint(min_val, max_val)
        await update.message.reply_text(
            f"{header('🎲 Número Aleatorio')}\n\n"
            f"{bold('Rango:')} {code(f'{min_val}-{max_val}')}\n"
            f"{bold('Resultado:')} {code(str(result))}",
            parse_mode="HTML",
        )
    except ValueError:
        await update.message.reply_text("❌ Números inválidos.")


# ============================================================================
# 🔧 COMANDOS DE UTILIDADES
# ============================================================================
async def qr_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /qr [texto]"""
    if not context.args:
        await update.message.reply_text("❌ Proporciona texto para el código QR.")
        return

    text = " ".join(context.args)
    img = qrcode.make(text)
    bio = BytesIO()
    bio.name = "qr_code.png"
    img.save(bio, "PNG")
    bio.seek(0)
    await update.message.reply_photo(photo=bio)


async def shorten_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /short [url]"""
    if not context.args:
        await update.message.reply_text("❌ Proporciona una URL para acortar.")
        return

    url = context.args[0]
    if not url.startswith("http"):
        url = "https://" + url

    try:
        response = requests.get(
            f"https://api-ssl.bitly.com/v4/shorten",
            headers={
                "Authorization": "Bearer YOUR_BITLY_TOKEN",
                "Content-Type": "application/json",
            },
            json={"long_url": url},
        )
        if response.status_code == 200:
            data = response.json()
            await update.message.reply_text(
                f"{header('🔗 Acortador de URL')}\n\n"
                f"{bold('Original:')} {code(url)}\n"
                f"{bold('Acortada:')} {code(data['link'])}",
                parse_mode="HTML",
            )
        else:
            # Usar servicio alternativo si no hay token
            response = requests.get(f"https://is.gd/create.php?format=json&url={url}")
            if response.status_code == 200:
                data = response.json()
                await update.message.reply_text(
                    f"{header('🔗 Acortador de URL')}\n\n"
                    f"{bold('Original:')} {code(url)}\n"
                    f"{bold('Acortada:')} {code(data['shorturl'])}",
                    parse_mode="HTML",
                )
            else:
                await update.message.reply_text("❌ Error al acortar URL.")
    except:
        await update.message.reply_text("❌ Error de conexión.")


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /weather [ciudad]"""
    if not context.args:
        await update.message.reply_text("❌ Proporciona una ciudad.")
        return

    city = " ".join(context.args)
    try:
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=YOUR_OPENWEATHER_TOKEN&units=metric&lang=es"
        )
        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            weather_desc = data["weather"][0]["description"]
            country = data["sys"]["country"]
            await update.message.reply_text(
                f"{header('🌤️ Clima')}\n\n"
                f"{bold('Ciudad:')} {code(f'{city}, {country}')}\n"
                f"{bold('Temperatura:')} {code(f'{temp}°C')}\n"
                f"{bold('Humedad:')} {code(f'{humidity}%')}\n"
                f"{bold('Condición:')} {code(weather_desc)}",
                parse_mode="HTML",
            )
        else:
            await update.message.reply_text("❌ Ciudad no encontrada.")
    except:
        await update.message.reply_text("❌ Error de conexión.")


async def public_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ip"""
    try:
        response = requests.get("https://api.ipify.org?format=json")
        if response.status_code == 200:
            data = response.json()
            await update.message.reply_text(
                f"{header('🌐 IP Pública')}\n\n{bold('Tu IP:')} {code(data['ip'])}",
                parse_mode="HTML",
            )
        else:
            await update.message.reply_text("❌ Error al obtener IP.")
    except:
        await update.message.reply_text("❌ Error de conexión.")


async def to_binary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /bin [texto]"""
    if not context.args:
        await update.message.reply_text("❌ Proporciona texto para codificar.")
        return

    text = " ".join(context.args)
    binary = " ".join(format(ord(char), "08b") for char in text)
    await update.message.reply_text(
        f"{header('🔢 Binario')}\n\n"
        f"{bold('Texto:')} {code(text)}\n"
        f"{bold('Binario:')} {code(binary)}",
        parse_mode="HTML",
    )


async def to_hex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /hex [texto]"""
    if not context.args:
        await update.message.reply_text("❌ Proporciona texto para codificar.")
        return

    text = " ".join(context.args)
    hex_text = text.encode("utf-8").hex()
    await update.message.reply_text(
        f"{header('🔢 Hexadecimal')}\n\n"
        f"{bold('Texto:')} {code(text)}\n"
        f"{bold('Hex:')} {code(hex_text)}",
        parse_mode="HTML",
    )


# ============================================================================
# 💻 COMANDOS DE SISTEMA
# ============================================================================
async def system_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /system"""
    info = {
        "Sistema": platform.system(),
        "Versión": platform.version(),
        "Arquitectura": platform.machine(),
        "Procesador": platform.processor(),
        "Nombre PC": platform.node(),
        "Python": platform.python_version(),
        "Compilador": platform.python_compiler(),
    }

    message = header("💻 Información del Sistema") + "\n\n"
    for key, value in info.items():
        message += f"{bold(key + ':')} {code(value)}\n"

    await update.message.reply_text(message, parse_mode="HTML")


async def python_version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /python"""
    await update.message.reply_text(
        f"{header('🐍 Python')}\n\n"
        f"{bold('Versión:')} {code(platform.python_version())}\n"
        f"{bold('Implementación:')} {code(platform.python_implementation())}\n"
        f"{bold('Compilador:')} {code(platform.python_compiler())}",
        parse_mode="HTML",
    )


async def ping_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /pingdb - Simula ping a base de datos"""
    start_time = time.time()
    time.sleep(random.uniform(0.1, 0.5))  # Simular latencia
    end_time = time.time()
    latency = (end_time - start_time) * 1000
    await update.message.reply_text(
        f"{header('🗄️ Ping a Base de Datos')}\n\n"
        f"{bold('Latencia:')} {code(f'{latency:.2f}ms')}\n"
        f"{bold('Estado:')} {code('✅ Conectado')}",
        parse_mode="HTML",
    )


async def speed_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /speedtest - Simula test de velocidad"""
    start_time = time.time()
    # Simular descarga
    time.sleep(random.uniform(0.5, 1.5))
    download_speed = random.uniform(10, 100)
    # Simular subida
    time.sleep(random.uniform(0.3, 0.8))
    upload_speed = random.uniform(5, 50)
    end_time = time.time()

    await update.message.reply_text(
        f"{header('📡 Test de Velocidad')}\n\n"
        f"{bold('Descarga:')} {code(f'{download_speed:.2f} Mbps')}\n"
        f"{bold('Subida:')} {code(f'{upload_speed:.2f} Mbps')}\n"
        f"{bold('Ping:')} {code(f'{(end_time - start_time) * 1000:.0f}ms')}",
        parse_mode="HTML",
    )


# ============================================================================
# 🎨 COMANDOS DE ESTILO
# ============================================================================
async def bold_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /bold [texto]"""
    if not context.args:
        await update.message.reply_text("❌ Proporciona texto.")
        return
    text = " ".join(context.args)
    await update.message.reply_text(f"<b>{text}</b>", parse_mode="HTML")


async def italic_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /italic [texto]"""
    if not context.args:
        await update.message.reply_text("❌ Proporciona texto.")
        return
    text = " ".join(context.args)
    await update.message.reply_text(f"<i>{text}</i>", parse_mode="HTML")


async def code_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /code [texto]"""
    if not context.args:
        await update.message.reply_text("❌ Proporciona texto.")
        return
    text = " ".join(context.args)
    await update.message.reply_text(f"<code>{text}</code>", parse_mode="HTML")


async def gradient_text_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /gradient [texto]"""
    if not context.args:
        await update.message.reply_text("❌ Proporciona texto.")
        return
    text = " ".join(context.args)
    await update.message.reply_text(gradient_text(text))


# ============================================================================
# 🎯 MANEJO DE BOTONES
# ============================================================================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja las interacciones con botones"""
    query = update.callback_query
    await query.answer()

    if query.data == "help":
        await help_cmd(update, context)
    elif query.data == "fun":
        keyboard = [
            [InlineKeyboardButton("8Ball", callback_data="8ball")],
            [InlineKeyboardButton("Dado", callback_data="dice")],
            [InlineKeyboardButton("Moneda", callback_data="coin")],
            [InlineKeyboardButton("Chiste", callback_data="joke")],
            [InlineKeyboardButton("Meme", callback_data="meme")],
            [InlineKeyboardButton("Gato", callback_data="cat")],
            [InlineKeyboardButton("Perro", callback_data="dog")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_caption(
            caption=header("🎲 Comandos de Diversión") + "\n\nSelecciona una opción:",
            reply_markup=reply_markup,
        )
    elif query.data == "utils":
        keyboard = [
            [InlineKeyboardButton("QR", callback_data="qr")],
            [InlineKeyboardButton("Acortar URL", callback_data="short")],
            [InlineKeyboardButton("Clima", callback_data="weather")],
            [InlineKeyboardButton("IP", callback_data="ip")],
            [InlineKeyboardButton("Binario", callback_data="bin")],
            [InlineKeyboardButton("Hexadecimal", callback_data="hex")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_caption(
            caption=header("🔧 Comandos de Utilidades") + "\n\nSelecciona una opción:",
            reply_markup=reply_markup,
        )
    elif query.data == "info":
        keyboard = [
            [InlineKeyboardButton("Sistema", callback_data="system")],
            [InlineKeyboardButton("Python", callback_data="python")],
            [InlineKeyboardButton("Ping DB", callback_data="pingdb")],
            [InlineKeyboardButton("Speedtest", callback_data="speedtest")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_caption(
            caption=header("ℹ️ Comandos de Información") + "\n\nSelecciona una opción:",
            reply_markup=reply_markup,
        )
    elif query.data == "back":
        await start(update, context)


# ============================================================================
# 🚀 INICIO DEL BOT
# ============================================================================
print(r"""
    ___        _              __   __
   /   | _____(_)__________  / /__/ /
  / /| |/ ___/ / ___/ ___/ / / / _  /
 / ___ / /__/ / /  (__  ) /_/ /  __/
/_/  |_\___/_/_/  /____/\____/\___/

      AstroX Development
""")

TOKEN = input("Introduce el token de tu bot: ").strip()

# Crear aplicación
app = ApplicationBuilder().token(TOKEN).build()

# Registrar comandos
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("ping", ping))
app.add_handler(CommandHandler("echo", echo))
app.add_handler(CommandHandler("id", user_id))
app.add_handler(CommandHandler("time", current_time))
app.add_handler(CommandHandler("date", current_date))
app.add_handler(CommandHandler("countdown", countdown))
app.add_handler(CommandHandler("timer", timer))
app.add_handler(CommandHandler("8ball", eight_ball))
app.add_handler(CommandHandler("dice", dice_roll))
app.add_handler(CommandHandler("coin", coin_flip))
app.add_handler(CommandHandler("joke", joke))
app.add_handler(CommandHandler("meme", meme))
app.add_handler(CommandHandler("cat", cat_image))
app.add_handler(CommandHandler("dog", dog_image))
app.add_handler(CommandHandler("calc", calculator))
app.add_handler(CommandHandler("sqrt", square_root))
app.add_handler(CommandHandler("pow", power))
app.add_handler(CommandHandler("random", random_number))
app.add_handler(CommandHandler("qr", qr_code))
app.add_handler(CommandHandler("short", shorten_url))
app.add_handler(CommandHandler("weather", weather))
app.add_handler(CommandHandler("ip", public_ip))
app.add_handler(CommandHandler("bin", to_binary))
app.add_handler(CommandHandler("hex", to_hex))
app.add_handler(CommandHandler("system", system_info))
app.add_handler(CommandHandler("python", python_version))
app.add_handler(CommandHandler("pingdb", ping_db))
app.add_handler(CommandHandler("speedtest", speed_test))
app.add_handler(CommandHandler("bold", bold_text))
app.add_handler(CommandHandler("italic", italic_text))
app.add_handler(CommandHandler("code", code_text))
app.add_handler(CommandHandler("gradient", gradient_text_cmd))

# Registrar manejador de botones
app.add_handler(CallbackQueryHandler(button_handler))

print("✅ Bot iniciado correctamente. Presiona CTRL+C para detenerlo.")
app.run_polling()
