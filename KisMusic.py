import asyncio
import os
import discord
import json
from discord import colour
import youtube_dl
from discord import voice_client
from discord import channel
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import Bot, has_permissions, CheckFailure
from youtube_dl import YoutubeDL

TOKEN = ''
song_queue = {}
queue_message = discord.message
bot = Bot('/')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="play something"))

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send("Hello World!")
    print(ctx.guild.id)

@bot.command(name='play', help='To play song')
async def play(ctx):
    channel = get(ctx.guild.text_channels, name='kis-music')
    if ctx.channel.id == channel.id:
        if ctx.guild.id in song_queue.keys():
            pass
        else:
            song_queue[ctx.guild.id] = []
        channel = ctx.message.author.voice.channel
        data = str(ctx.message.content)
        message = ctx.message
        await message.delete()

        if is_connected(ctx):
            voice_channel = get(bot.voice_clients, guild=ctx.guild)
        else:
            voice_channel : discord.VoiceClient = await channel.connect()

        #voice = get(bot.voice_clients, guild=ctx.guild)
        if playing(ctx):
            await add(data,ctx)
            return
        else:
            await add(data,ctx)
            await play_loop(ctx, voice_channel)
    else:
        embed = discord.Embed(title="Command restricted to #kis-music", colour=discord.Colour.blurple())
        await ctx.send(embed=embed)


@bot.command(name='pause')
async def pause(ctx):
    channel = get(ctx.guild.text_channels, name='kis-music')
    if ctx.channel.id == channel.id:
        voice = get(bot.voice_clients, guild=ctx.guild)

        if voice.is_playing():
            voice.pause()
            embed = discord.Embed(title='Music paused', colour=discord.Colour.blurple())
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Command restricted to #kis-music", colour=discord.Colour.blurple())
        await ctx.send(embed=embed)
    message = ctx.message
    await message.delete()

@bot.command(name='resume')
async def resume(ctx):
    channel = get(ctx.guild.text_channels, name='kis-music')
    if ctx.channel.id == channel.id:
        voice = get(bot.voice_clients, guild=ctx.guild)

        if not voice.is_playing():
            voice.resume()
            embed = discord.Embed(title='Music is resuming', colour=discord.Colour.blurple())
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Command restricted to #kis-music", colour=discord.Colour.blurple())
        await ctx.send(embed=embed)
    message = ctx.message
    await message.delete()

@bot.command(name='skip')
async def skip(ctx):
    channel = get(ctx.guild.text_channels, name='kis-music')
    if ctx.channel.id == channel.id:
        voice = get(bot.voice_clients, guild=ctx.guild)
        embed = discord.Embed(title='Song skipped', colour=discord.Colour.blurple())
        await ctx.send(embed=embed)
        voice.stop()
    else:
        embed = discord.Embed(title="Command restricted to #kis-music", colour=discord.Colour.blurple())
        await ctx.send(embed=embed)
    message = ctx.message
    await message.delete()

async def play_loop(ctx, voice_channel):
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if not voice_channel.is_playing():
        URL = song_queue[ctx.guild.id][0]['url']
        voice_channel.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS, executable="C:/FFmpeg/bin/ffmpeg.exe"), after=lambda _:asyncio.run_coroutine_threadsafe(play_loop(ctx, voice_channel), bot.loop))
        title = song_queue[ctx.guild.id][0]['webpage_url']
        del(song_queue[ctx.guild.id][0])
        voice_channel.is_playing()
        await ctx.send('Now playing on Kis Music:')
        await ctx.send(title)

    while voice_channel.is_playing():
        await asyncio.sleep(1)
    else:
        await asyncio.sleep(15)
        while voice_channel.is_playing():
            break 
        else:
            await voice_channel.disconnect() 

@bot.command(name='queue')
async def queue(ctx):
    channel = get(ctx.guild.text_channels, name='kis-music')
    if ctx.channel.id == channel.id:
        try:
            song_list = []
            for i in range(len(song_queue[ctx.guild.id])):
                song_list.append(song_queue[ctx.guild.id][i]['title'])

            embed = discord.Embed(title="Current Queue", colour=discord.Colour.blurple())
            embed.add_field(name='Songs', value=', \n'.join(song for song in song_list))
            await channel.send(embed=embed)
        except:
            embed = discord.Embed(title="Queue is empty", colour=discord.Colour.blurple())
            await channel.send(embed=embed)
    else:
        embed = discord.Embed(title="Command restricted to #kis-music", colour=discord.Colour.blurple())
        await ctx.send(embed=embed)
    message = ctx.message
    await message.delete()

@bot.command(name='setup')
async def setup(ctx):
    channel = get(ctx.guild.text_channels, name='kis-music')
    if channel == None:
        channel = await ctx.guild.create_text_channel('kis-music')
        embed = discord.Embed(title='Setup completed. Thank you using Kis Music', colour=discord.Colour.blurple())
        await channel.send(embed=embed)
    else:
        await ctx.send('Setup has already been completed')
    message = ctx.message
    await message.delete()

async def add(string,ctx):
    channel = get(ctx.guild.text_channels, name='kis-music')
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}

    song = string
    song.split(' ', 1)
    song = song.split(' ', 1)[1]

    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(f"ytsearch:{song}", download=False)['entries'][0]
    song_queue[ctx.guild.id].append(info)
    embed=discord.Embed(title=f"{info['title']} has been added",colour=discord.Colour.blurple())
    await channel.send(embed=embed)

def is_connected(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()

def playing(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    return voice.is_playing()


bot.run(TOKEN)