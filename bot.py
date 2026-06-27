import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

TOKEN = os.getenv("TOKEN")

# {dia: [{"hora": "09:00", "cliente": "João", "user_id": 123}]}
agendamentos_por_dia = {}

ESCOLHER_DIA, ESCOLHER_HORA, DIGITAR_NOME = range(3)

DIAS_VALIDOS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]

def gerar_horarios():
    horarios = []
    for h in range(9, 12):
        for m in ["00", "30"]:
            horarios.append(f"{h:02d}:{m}")
    for h in range(14, 18):
        for m in ["00", "30"]:
            horarios.append(f"{h:02d}:{m}")
    horarios.append("18:00")
    return horarios

TODOS_HORARIOS = gerar_horarios()

def horarios_ocupados_no_dia(dia):
    return [ag["hora"] for ag in agendamentos_por_dia.get(dia, [])]

def gerar_teclado_horarios(dia):
    ocupados = horarios_ocupados_no_dia(dia)
    botoes = []
    linha = []
    for i, h in enumerate(TODOS_HORARIOS):
        label = f"🔒 {h}" if h in ocupados else h
        linha.append(label)
        if len(linha) == 3:
            botoes.append(linha)
            linha = []
    if linha:
        botoes.append(linha)
    return botoes

def gerar_teclado_dias():
    return [DIAS_VALIDOS[:3], DIAS_VALIDOS[3:]]

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! Bem-vindo à Barbearia Demo ✂️\n\n"
        "Comandos disponíveis:\n"
        "/agendar — Marcar um horário\n"
        "/agendamentos — Ver todos os agendamentos do dia\n"
        "/cancelar — Cancelar um agendamento",
        reply_markup=ReplyKeyboardRemove()
    )

async def agendar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Qual dia você quer agendar?",
        reply_markup=ReplyKeyboardMarkup(
            gerar_teclado_dias(),
            one_time_keyboard=True,
            resize_keyboard=True,
            is_persistent=True
        )
    )
    return ESCOLHER_DIA

async def escolher_dia(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text

    if texto not in DIAS_VALIDOS:
        await update.message.reply_text(
            "Por favor, escolha um dia usando os botões:",
            reply_markup=ReplyKeyboardMarkup(
                gerar_teclado_dias(),
                one_time_keyboard=True,
                resize_keyboard=True,
                is_persistent=True
            )
        )
        return ESCOLHER_DIA

    ctx.user_data["dia"] = texto
    teclado = gerar_teclado_horarios(texto)

    await update.message.reply_text(
        f"Horários para {texto}:\n🔒 = indisponível",
        reply_markup=ReplyKeyboardMarkup(
            teclado,
            one_time_keyboard=True,
            resize_keyboard=True,
            is_persistent=True
        )
    )
    return ESCOLHER_HORA

async def escolher_hora(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    dia = ctx.user_data.get("dia")

    if texto.startswith("🔒"):
        await update.message.reply_text(
            "Esse horário já está ocupado! Escolha outro:",
            reply_markup=ReplyKeyboardMarkup(
                gerar_teclado_horarios(dia),
                one_time_keyboard=True,
                resize_keyboard=True,
                is_persistent=True
            )
        )
        return ESCOLHER_HORA

    if texto not in TODOS_HORARIOS:
        await update.message.reply_text(
            "Por favor, escolha um horário usando os botões:",
            reply_markup=ReplyKeyboardMarkup(
                gerar_teclado_horarios(dia),
                one_time_keyboard=True,
                resize_keyboard=True,
                is_persistent=True
            )
        )
        return ESCOLHER_HORA

    ctx.user_data["hora"] = texto

    await update.message.reply_text(
        f"Horário {texto} selecionado!\n\nAgora digite o nome do cliente:",
        reply_markup=ReplyKeyboardRemove()
    )
    return DIGITAR_NOME

async def digitar_nome(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    nome = update.message.text.strip()

    if len(nome) < 2:
        await update.message.reply_text("Por favor, digite um nome válido:")
        return DIGITAR_NOME

    dia = ctx.user_data["dia"]
    hora = ctx.user_data["hora"]
    user_id = update.message.from_user.id

    if dia not in agendamentos_por_dia:
        agendamentos_por_dia[dia] = []

    agendamentos_por_dia[dia].append({
        "hora": hora,
        "cliente": nome,
        "user_id": user_id
    })

    agendamentos_por_dia[dia].sort(key=lambda x: x["hora"])

    await update.message.reply_text(
        f"Agendamento confirmado! ✅\n\n"
        f"Cliente: {nome}\n"
        f"Dia: {dia}\n"
        f"Horário: {hora}\n\n"
        f"Te esperamos! ✂️"
    )
    return ConversationHandler.END

async def ver_agendamentos(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not any(agendamentos_por_dia.values()):
        await update.message.reply_text("Nenhum agendamento encontrado.")
        return

    mensagem = "📋 Agendamentos:\n"
    for dia in DIAS_VALIDOS:
        ags = agendamentos_por_dia.get(dia, [])
        if ags:
            mensagem += f"\n📅 {dia}:\n"
            for ag in ags:
                mensagem += f"  ✂️ {ag['hora']} — {ag['cliente']}\n"

    await update.message.reply_text(mensagem)

async def cancelar_agendamento(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    todos = []
    for dia, ags in agendamentos_por_dia.items():
        for ag in ags:
            todos.append((dia, ag))

    if not todos:
        await update.message.reply_text("Não há agendamentos para cancelar.")
        return

    mensagem = "Agendamentos atuais:\n\n"
    for i, (dia, ag) in enumerate(todos):
        mensagem += f"{i+1}. {dia} {ag['hora']} — {ag['cliente']}\n"
    mensagem += "\nDigite o número do agendamento que deseja cancelar:"

    ctx.user_data["todos_agendamentos"] = todos
    await update.message.reply_text(mensagem, reply_markup=ReplyKeyboardRemove())
    return

async def mensagem_invalida(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Não entendi. Use um dos comandos:\n\n"
        "/agendar — Marcar um horário\n"
        "/agendamentos — Ver todos os agendamentos\n"
        "/cancelar — Cancelar agendamento"
    )

def main():
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .build()
    )

    conv = ConversationHandler(
        entry_points=[CommandHandler("agendar", agendar)],
        states={
            ESCOLHER_DIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, escolher_dia)],
            ESCOLHER_HORA: [MessageHandler(filters.TEXT & ~filters.COMMAND, escolher_hora)],
            DIGITAR_NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, digitar_nome)],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("agendamentos", ver_agendamentos))
    app.add_handler(CommandHandler("cancelar", cancelar_agendamento))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensagem_invalida))

    print("Bot rodando...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
