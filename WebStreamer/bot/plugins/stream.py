# This file is a part of TG-FileStreamBot
# Coding : Jyothis Jayanth [@EverythingSuckz]

import logging
from pyrogram import filters, Client
from WebStreamer.vars import Var
from urllib.parse import quote_plus
from WebStreamer.bot import StreamBot
from WebStreamer.utils.file_id import get_unique_id
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

def detect_type(media_msg: Message):
    attribute = None
    for attr in (
        "audio",
        "document",
        "photo",
        "sticker",
        "animation",
        "video",
        "voice",
        "video_note",
    ):
        try:
            attribute = getattr(media_msg, attr)
            if attribute:
                break
        except AttributeError:
            continue
    return attribute

@StreamBot.on_message(
    filters.private
    & (
        filters.document
        | filters.video
        | filters.audio
        | filters.animation
        | filters.voice
        | filters.video_note
        | filters.photo
        | filters.sticker
    ),
    group=4,
)
async def media_receive_handler(c: Client, m: Message):
    file = detect_type(m)
    file_name = ""
    if file:
        # Uso getattr para evitar errores si el archivo (ej. foto) no tiene nombre
        file_name = getattr(file, "file_name", "")

    try:
        # Intento normal de reenvío
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
    except Exception:
        # Si falla por "Peer id invalid", forzamos al bot a buscar el canal primero
        try:
            await c.get_chat(Var.BIN_CHANNEL)
            log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        except Exception as e:
            # Si sigue fallando, imprimimos el error real y paramos
            logging.error(f"Error reenviando al BIN_CHANNEL: {e}")
            return

    stream_link = f"{Var.URL}{log_msg.id}/{quote_plus(file_name)}?hash={get_unique_id(log_msg)}"
    short_link = f"{Var.URL}{get_unique_id(log_msg)}{log_msg.id}"
    logging.info(f"Generated link: {stream_link} for {m.from_user.first_name}")
    
    await m.reply_text(
        text="<code>{}</code>\n(<a href='{}'>shortened</a>)".format(
            stream_link, short_link
        ),
        quote=True,
        parse_mode="html",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Open", url=stream_link)]]
        ),
    )
