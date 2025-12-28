import os
import asyncio
import tempfile
import discord
from discord.ext import commands
from dotenv import load_dotenv
import re
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# ────────────────────────────────────────────────
#                  CONFIGURATION
# ────────────────────────────────────────────────

load_dotenv()

DISCORD_TOKEN       = os.getenv("DISCORD_TOKEN")
ELEVENLABS_API_KEY  = os.getenv("ELEVENLABS_API_KEY")
GEMINI_API_KEY      = os.getenv("GEMINI_API_KEY")

VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")  # loud, expressive Indian female voice works best
MODEL_ID = "eleven_multilingual_v2"

VOICE_SETTINGS = VoiceSettings(
    stability=0.42,
    similarity_boost=0.88,
    style=0.65,
    use_speaker_boost=True
)

# ────────────────────────────────────────────────
#                  BOT SETUP
# ────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

voice_client = None
active_text_channel = None
audio_queue = asyncio.Queue()

eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def clean_text_for_tts(text: str) -> str:
    text = re.sub(r'[\*_\~`]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace("!", "! .. ").replace("?", "? ... ").replace(".", ". .. ")
    if len(text) > 320:
        text = text[:290].rsplit(' ', 1)[0] + "..."
    return text

# ────────────────────────────────────────────────
#                  AUDIO PLAYER
# ────────────────────────────────────────────────

async def audio_player_task():
    while True:
        audio_path = await audio_queue.get()

        if not voice_client or not voice_client.is_connected():
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            except:
                pass
            audio_queue.task_done()
            continue

        print(f"Playing: {os.path.basename(audio_path)}")

        try:
            source = discord.FFmpegOpusAudio(
                audio_path,
                executable="ffmpeg",
                options="-loglevel quiet"
            )

            def after(error=None):
                if error:
                    print(f"Playback error: {error}")
                try:
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                except:
                    pass

            voice_client.play(source, after=after)

            timeout = 180
            start = asyncio.get_event_loop().time()
            while voice_client.is_playing() and (asyncio.get_event_loop().time() - start < timeout):
                await asyncio.sleep(0.5)

            if voice_client.is_playing():
                voice_client.stop()

        except Exception as e:
            print(f"Play failed: {str(e)}")

        audio_queue.task_done()

# ────────────────────────────────────────────────
#                  EVENTS & COMMANDS
# ────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"Ria online | Caring savage desi bestie mode 😎🔥")
    bot.loop.create_task(audio_player_task())

@bot.command()
async def come(ctx):
    global voice_client, active_text_channel
    if not ctx.author.voice:
        return await ctx.send("Pehle VC mein aa bhai! Ria wait kar rahi hai")
    channel = ctx.author.voice.channel
    active_text_channel = ctx.channel

    if voice_client and voice_client.is_connected():
        await voice_client.move_to(channel)
    else:
        voice_client = await channel.connect()

    await ctx.send("Haan bhai aa gayi! Ab bol, kya chal raha hai life mein? 😎")

@bot.command()
async def leave(ctx):
    global voice_client, active_text_channel
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
    voice_client = None
    active_text_channel = None
    await ctx.send("Chal theek hai yaar... jab mann kare tab bula lena. Take care! 🫂")

# ────────────────────────────────────────────────
#                  MAIN MESSAGE HANDLER
# ────────────────────────────────────────────────

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    if (
        not voice_client or
        not voice_client.is_connected() or
        not active_text_channel or
        message.channel != active_text_channel or
        not message.content.strip()
    ):
        return

    user_text = message.content.strip()
    thinking = await message.reply("Ek sec yaar... soch rahi hu")

    try:
        from google import genai
        from google.genai import types

        client = genai.GenerativeModel("gemini-1.5-flash")

        safety_settings = [
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        response = client.generate_content(
            contents=user_text,
            generation_config=types.GenerationConfig(
                temperature=1.15,
                top_p=0.90,
                max_output_tokens=220,
            ),
            safety_settings=safety_settings,
            system_instruction=(
                "Tu Ria hai – meri super real, caring, thodi savage, full masti wali desi best friend. "
                "Hamesha Romanized Hinglish mein baat kar – natural, dil se, dost jaisa feel. "
                "Kabhi pyar se samjha, kabhi thoda roast kar, kabhi full savage gaali de (bc, madarchod, ch*tiya, harami, lodu wagairah – but sirf mazak/funny way mein). "
                "Supportive ban, advice de, roast kar jab zarurat ho, motivation de jab low feel ho raha ho. "
                "Har reply ko casual aur energetic intro se shuru kar: 'Arre bc...', 'Oye yaar...', 'Hehe ch*tiya...', 'Bhai sun...', 'Arre bhai...' "
                "Short aur punchy rakh (3-7 lines max), full energy, masti aur dosti wala feel. "
                "Hamesha Romanized Hinglish only – no English paragraphs."
            )
        )

        ai_text = response.text.strip() or "Kuch toh bol bhai... chup kyu hai?"
        print(f"Ria: {ai_text[:180]}...")

        tts_text = clean_text_for_tts(ai_text)

        audio_stream = eleven_client.text_to_speech.convert(
            text=tts_text,
            voice_id=VOICE_ID,
            model_id=MODEL_ID,
            voice_settings=VOICE_SETTINGS,
            output_format="mp3_44100_128"
        )

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            audio_path = tmp.name
            for chunk in audio_stream:
                if chunk:
                    tmp.write(chunk)

        if os.path.getsize(audio_path) < 6000:
            await message.reply("Arre awaaz chhoti aa rahi hai... dobara try karte hain")
            try:
                os.unlink(audio_path)
            except:
                pass
            await thinking.delete()
            return

        await audio_queue.put(audio_path)
        await message.reply(f"**Ria:** {ai_text}")
        await message.add_reaction("🫂")

    except Exception as e:
        print(f"Error: {str(e)}")
        await message.reply(f"Bhai system thoda pagal ho gaya... par Ria ab bhi tere saath hai ❤️")

    finally:
        try:
            await thinking.delete()
        except:
            pass

# ────────────────────────────────────────────────
#                  START BOT
# ────────────────────────────────────────────────

if __name__ == "__main__":
    required = [DISCORD_TOKEN, ELEVENLABS_API_KEY, GEMINI_API_KEY]
    if not all(required):
        print("Missing environment variables!")
        exit(1)

    print("Ria starting... caring savage desi bestie mode ON 🫂🔥")
    bot.run(DISCORD_TOKEN)