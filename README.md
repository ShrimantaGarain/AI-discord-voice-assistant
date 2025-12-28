# AI-discord-voice-assistant
Ria – Caring Savage Bestie Discord Bot 🫂🔥


# Ria – Supportive Voice Chat Discord Bot

A friendly, voice-enabled Discord bot designed to be a helpful and supportive companion in voice channels.

## Features

- Joins your voice channel using the !come command
- Leaves the voice channel with the !leave command
- Provides real-time voice responses using ElevenLabs text-to-speech
- Powered by Google's Gemini AI for natural language understanding and generation
- Responds in a supportive, encouraging, and occasionally humorous tone
- Message queue system to prevent overlapping audio playback
- Automatically cleans and prepares text for optimal speech synthesis

## Requirements

- Python 3.9 or higher
- FFmpeg installed on the system (required for audio processing)
- Discord bot token
- ElevenLabs API key
- Google Gemini API key

## Installation & Setup

1. Clone the repository
   git clone https://github.com/yourusername/ria-bot.git
   cd ria-bot

2. Install required dependencies
   pip install discord.py python-dotenv elevenlabs google-generativeai

3. Create a .env file in the project root with the following content:

   DISCORD_TOKEN=your_discord_bot_token_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   ELEVENLABS_VOICE_ID=your_preferred_voice_id          # optional - default used if not set
   GEMINI_API_KEY=your_google_gemini_api_key

4. Run the bot
   python main.py

## Commands

Command     Description
!come       Makes the bot join your current voice channel
!leave      Makes the bot leave the voice channel

After the bot joins your voice channel, simply type messages in the same text channel 
where you used the command — the bot will respond with both text and voice.

## How It Works

1. When you use !come, the bot connects to your voice channel
2. Any message you send in the linked text channel is processed by Gemini AI
3. The AI generates a helpful, supportive response
4. The response is converted to speech using ElevenLabs
5. The audio is played in the voice channel and shown as text

## Important Notes

- The bot only responds in channels where it was summoned using !come
- Make sure FFmpeg is installed and accessible in your system's PATH
- API keys are required for both ElevenLabs (text-to-speech) and Google Gemini (AI responses)

## License

This project is open source and available under the MIT License.

---
Created as a personal project to provide friendly voice companionship in Discord servers.
