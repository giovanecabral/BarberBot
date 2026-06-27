# ✂️ BarberBot — Bot de Agendamento para Barbearias

Bot do Telegram desenvolvido em Python para automatizar o agendamento de clientes em barbearias. Permite que o barbeiro gerencie horários, visualize agendamentos do dia e cancele reservas diretamente pelo Telegram.

---

## Funcionalidades

- Agendamento de clientes com nome, dia e horário
- Horários disponíveis das 09:00 às 18:00 (intervalos de 30 minutos)
- Horários ocupados exibidos com 🔒 para evitar conflitos
- Listagem de todos os agendamentos organizados por dia
- Cancelamento de agendamentos
- Validação de entradas — o bot só aceita opções válidas

---

## Tecnologias

- Python 3.9+
- [python-telegram-bot](https://python-telegram-bot.org/) v20.7
- Telegram Bot API

---

## Como rodar

### 1. Clone o repositório

\```bash
git clone https://github.com/gio1411/barberbot.git
cd barberbot
\```

### 2. Instale as dependências

\```bash
pip install python-telegram-bot==20.7
\```

### 3. Configure o token

Crie um bot no Telegram pelo [@BotFather](https://t.me/BotFather) e copie o token gerado.

Renomeie o arquivo `.env.example` para `.env` e coloque seu token:

\```
TOKEN=seu_token_aqui
\```

### 4. Rode o bot

\```bash
python bot.py
\```

---

## Comandos disponíveis

| Comando | Descrição |
|---|---|
| `/start` | Exibe o menu principal |
| `/agendar` | Inicia o fluxo de agendamento |
| `/agendamentos` | Lista todos os agendamentos por dia |
| `/cancelar` | Cancela um agendamento existente |

---

## Autor

Desenvolvido por **Giovane Cabral**
• [GitHub](https://github.com/gio1411)

---

## Licença

MIT License
