import os, logging, asyncio, io, sys, traceback
from datetime import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
LOGGER = logging.getLogger(__name__)

# --- STARTING BOT --- #
api_id = int(os.environ.get("APP_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("TG_BOT_TOKEN")
auth_chts = {int(x) for x in os.environ.get("AUTH_USERS", "").split()}
banned_usrs = {int(x) for x in os.environ.get("BANNED_USRS", "").split()}
client = TelegramClient('client', api_id, api_hash).start(bot_token=bot_token)

# --- PINGING BOT --- #
@client.on(events.NewMessage(pattern="/ping"))
async def pingE(event):
    start = datetime.now()
    catevent = await event.respond("`!....`")
    await asyncio.sleep(0.3)
    await catevent.edit("`..!..`")
    await asyncio.sleep(0.3)
    await catevent.edit("`....!`")
    end = datetime.now()
    tms = (end - start).microseconds / 1000
    ms = round((tms - 0.6) / 3, 3)
    await catevent.edit(f"Pong!\n`{ms} ms`")

# --- UPDATE BOT --- #
@client.on(events.NewMessage(pattern="/update"))
async def updateE(event):
    if event.sender_id != 1252058587:
        return
    k = await event.respond("Initializing...")
    os.system("git init")
    os.system("git remote add origin https://github.com/AnjanaMadu/HerokuTerminalBot.git")
    os.system("rm -rf *")
    await k.edit("Pushing...")
    os.system("git pull origin main")
    await k.edit("Restarting")
    executable = sys.executable.replace(" ", "\\ ")
    args = [executable, "main.py"]
    os.execle(executable, *args, os.environ)
    sys.exit(0)

# --- RESTART BOT --- #
@client.on(events.NewMessage(pattern="/restart"))
async def restartE(event):
    if event.sender_id != 1252058587:
        return
    await event.respond("Restarting")
    executable = sys.executable.replace(" ", "\\ ")
    args = [executable, "main.py"]
    os.execle(executable, *args, os.environ)
    sys.exit(0)

# --- EVAL DEF HERE --- #
async def aexec(code, smessatatus):
    message = event = smessatatus
    p = lambda _x: print(_format.yaml_format(_x))
    reply = await event.get_reply_message()
    exec(
        (
            'async def __aexec(message, event , reply, client, p, chat): '
            + "".join(f"\n {l}" for l in code.split("\n"))
        )
    )

    return await locals()["__aexec"](
        message, event, reply, message.client, p, message.chat_id
    )
 
# --- EVAL EVENT HERE --- # 
@client.on(events.NewMessage(chats=auth_chts, pattern="/eval ?(.*)"))
async def evalE(event):
    if event.sender_id in banned_usrs:
        return await event.respond("You are Banned!")
    cmd = "".join(event.message.message.split(maxsplit=1)[1:])
    if not cmd:
        return
    cmd = (
        cmd.replace("send_message", "send_message")
        .replace("send_file", "send_file")
        .replace("edit_message", "edit_message")
    )
    catevent = await event.respond("`Running ...`")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, event)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = (
        f"**•  Eval : **\n```{cmd}``` \n\n**•  Result : **\n```{evaluation}``` \n"
    )
    await catevent.edit(final_output)

# --- BASH DEF HERE --- #
async def bash(cmd):

    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    err = stderr.decode().strip()
    out = stdout.decode().strip()
    return out, err

# --- BASH EVENT HERE --- #
@client.on(events.NewMessage(chats=auth_chts, pattern="/bash ?(.*)"))
async def bashE(event):
    if event.sender_id in banned_usrs:
        return await event.respond("You are Banned!")
    cmd = "".join(event.message.message.split(maxsplit=1)[1:])
    out, err = await bash(cmd)
    if out:
        await event.respond(f'**CMD:** `{cmd}`\n**OUTPUT:**\n `{out}`')
    elif err:
        await event.respond(f'**CMD:** `{cmd}`\n**ERROR:**\n `{err}`')
    else:
        await event.respond(f'**CMD:** `{cmd}`')

print('>> BOT STARTED <<')
os.system("python -V")
client.run_until_disconnected()


