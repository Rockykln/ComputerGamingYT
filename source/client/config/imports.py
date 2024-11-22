import discord

from discord import Status, ActivityType, Interaction, SelectOption, ButtonStyle, ui, Embed, Member, Role, TextChannel, app_commands, FFmpegPCMAudio, PCMVolumeTransformer
from discord.ext import commands, tasks
from discord.ext.commands import has_permission
from discord.ui import View, Select, Button, Modal, TextInput
from discord.enums import Status, ActivityType
from discord.gateway import DiscordWebSocket, _log
from discord.utils import get
from discord.app_commands import CommandInvokeError

import os
import io
import sys
import nacl
import asyncio
import threading
import logging
import subprocess
import aiohttp
import importlib
import platform
import psutil
import urllib.parse
import tracemalloc
import uvicorn
import json
import requests

from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from typing import Optional
from flask import Flask, render_template
from pytube import YouTube
from pydub import AudioSegment
from youtube_dl import YoutubeDL
from yt_dlp as youtube_dl