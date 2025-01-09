
# Standard library imports
import asyncio
import io
import importlib
import json
import logging
import os
import platform
import psutil
import subprocess
import sys
import threading
import tracemalloc
import urllib.parse
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

# Third-party imports
import aiohttp
import nacl
import requests
import uvicorn
from dotenv import load_dotenv
from flask import Flask, render_template
from pydub import AudioSegment

# Discord imports
import discord
import discord.voice_client
from discord import (
	Status,
	ActivityType,
	ButtonStyle,
	Embed,
	FFmpegPCMAudio,
	Interaction,
	Member,
	PCMVolumeTransformer,
	Permissions,
	Role,
	SelectOption,
	TextChannel,
	app_commands,
	ui
)
from discord.app_commands import CommandInvokeError
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from discord.gateway import DiscordWebSocket, _log
from discord.ui import View, Select, Button, Modal, TextInput
from discord.utils import get



