
import discord
import discord.voice_client
import wmi
import GPUtil

from discord import (
	Status, 
	ActivityType, 
	Interaction, 
	SelectOption, 
	ButtonStyle, 
	ui, 
	Embed, 
	Member, 
	Role, 
	TextChannel, 
	app_commands, 
	FFmpegPCMAudio, 
	PCMVolumeTransformer
)
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
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
import json
import requests

from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any






