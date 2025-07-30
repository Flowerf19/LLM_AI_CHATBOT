# filepath: discord-bot-gemini/src/services/admin_channels_service.py

import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import logging
from typing import Optional

logger = logging.getLogger('discord_bot.AdminChannelsService')

class AdminChannelsService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'bot_channels.json')
        self.bot_channels = self.load_bot_channels()

    def load_bot_channels(self):
        """Load bot channels from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading bot channels: {e}")
            return {}

    def save_bot_channels(self):
        """Save bot channels to file"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.bot_channels, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving bot channels: {e}")

    def is_bot_channel(self, guild_id: int, channel_id: int) -> bool:
        """Check if channel is designated as bot channel"""
        guild_str = str(guild_id)
        if guild_str not in self.bot_channels:
            return True  # If no bot channels set, bot works everywhere
        return channel_id in self.bot_channels[guild_str]

    # Slash Commands
    @app_commands.command(name="addbotchannel", description="Thêm kênh cho bot hoạt động")
    @app_commands.describe(channel="Kênh muốn thêm bot")
    @commands.has_permissions(manage_channels=True)
    async def add_bot_channel_slash(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Add a channel where bot can operate"""
        if not interaction.guild:
            await interaction.response.send_message("Lệnh này chỉ dùng trong server.", ephemeral=True)
            return
        guild_id = str(interaction.guild.id)
        
        if guild_id not in self.bot_channels:
            self.bot_channels[guild_id] = []
        
        if channel.id not in self.bot_channels[guild_id]:
            self.bot_channels[guild_id].append(channel.id)
            self.save_bot_channels()
            
            embed = discord.Embed(
                title="✅ Đã thêm kênh bot",
                description=f"Bot bây giờ có thể hoạt động trong {channel.mention}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="⚠️ Kênh đã tồn tại",
                description=f"{channel.mention} đã được thêm trước đó",
                color=discord.Color.yellow()
            )
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="removebotchannel", description="Xóa kênh khỏi danh sách bot")
    @app_commands.describe(channel="Kênh muốn xóa bot")
    @commands.has_permissions(manage_channels=True)
    async def remove_bot_channel_slash(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Remove a channel from bot operation"""
        if not interaction.guild:
            await interaction.response.send_message("Lệnh này chỉ dùng trong server.", ephemeral=True)
            return
        guild_id = str(interaction.guild.id)
        
        if guild_id in self.bot_channels and channel.id in self.bot_channels[guild_id]:
            self.bot_channels[guild_id].remove(channel.id)
            
            # Remove guild entry if no channels left
            if not self.bot_channels[guild_id]:
                del self.bot_channels[guild_id]
                
            self.save_bot_channels()
            
            embed = discord.Embed(
                title="✅ Đã xóa kênh bot",
                description=f"Bot không còn hoạt động trong {channel.mention}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="⚠️ Kênh không tồn tại",
                description=f"{channel.mention} không có trong danh sách bot channels",
                color=discord.Color.yellow()
            )
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="listbotchannels", description="Xem danh sách kênh bot")
    async def list_bot_channels_slash(self, interaction: discord.Interaction):
        """List all bot channels for this guild"""
        if not interaction.guild:
            await interaction.response.send_message("Lệnh này chỉ dùng trong server.", ephemeral=True)
            return
        guild_id = str(interaction.guild.id)
        
        embed = discord.Embed(
            title="📋 Danh sách kênh bot",
            color=discord.Color.blue()
        )
        
        if guild_id not in self.bot_channels or not self.bot_channels[guild_id]:
            embed.description = "Bot có thể hoạt động ở tất cả các kênh (chưa có hạn chế)"
        else:
            channels = []
            for channel_id in self.bot_channels[guild_id]:
                channel = interaction.guild.get_channel(channel_id) if interaction.guild else None
                if channel:
                    channels.append(f"• {channel.mention}")
                else:
                    channels.append(f"• Kênh đã bị xóa (ID: {channel_id})")
            
            embed.description = "\n".join(channels) if channels else "Không có kênh nào"
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clearbotchannels", description="Xóa tất cả kênh bot (bot hoạt động ở mọi nơi)")
    @commands.has_permissions(manage_channels=True)
    async def clear_bot_channels_slash(self, interaction: discord.Interaction):
        """Clear all bot channels for this guild"""
        if not interaction.guild:
            await interaction.response.send_message("Lệnh này chỉ dùng trong server.", ephemeral=True)
            return
        guild_id = str(interaction.guild.id)
        
        if guild_id in self.bot_channels:
            del self.bot_channels[guild_id]
            self.save_bot_channels()
        
        embed = discord.Embed(
            title="✅ Đã xóa tất cả kênh bot",
            description="Bot bây giờ có thể hoạt động ở tất cả các kênh",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    # Prefix Commands (for backward compatibility)
    @commands.command(name='addbotchannel')
    @commands.has_permissions(manage_channels=True)
    async def add_bot_channel(self, ctx, channel: Optional[discord.TextChannel] = None):
        """Add a channel where bot can operate"""
        if channel is None:
            if isinstance(ctx.channel, discord.TextChannel):
                channel = ctx.channel
            else:
                await ctx.send("Lệnh này chỉ dùng trong kênh văn bản.")
                return
        if not ctx.guild:
            await ctx.send("Lệnh này chỉ dùng trong server.")
            return
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.bot_channels:
            self.bot_channels[guild_id] = []
        
        if channel.id not in self.bot_channels[guild_id]:
            self.bot_channels[guild_id].append(channel.id)
            self.save_bot_channels()
            await ctx.send(f"✅ Đã thêm {channel.mention} vào danh sách kênh bot")
        else:
            await ctx.send(f"⚠️ {channel.mention} đã có trong danh sách")

    @commands.command(name='removebotchannel')
    @commands.has_permissions(manage_channels=True)
    async def remove_bot_channel(self, ctx, channel: Optional[discord.TextChannel] = None):
        """Remove a channel from bot operation"""
        if channel is None:
            if isinstance(ctx.channel, discord.TextChannel):
                channel = ctx.channel
            else:
                await ctx.send("Lệnh này chỉ dùng trong kênh văn bản.")
                return
        if not ctx.guild:
            await ctx.send("Lệnh này chỉ dùng trong server.")
            return
        guild_id = str(ctx.guild.id)
        
        if guild_id in self.bot_channels and channel.id in self.bot_channels[guild_id]:
            self.bot_channels[guild_id].remove(channel.id)
            
            if not self.bot_channels[guild_id]:
                del self.bot_channels[guild_id]
                
            self.save_bot_channels()
            await ctx.send(f"✅ Đã xóa {channel.mention} khỏi danh sách kênh bot")
        else:
            await ctx.send(f"⚠️ {channel.mention} không có trong danh sách")

    @commands.command(name='listbotchannels')
    async def list_bot_channels(self, ctx):
        """List all bot channels for this guild"""
        if not ctx.guild:
            await ctx.send("Lệnh này chỉ dùng trong server.")
            return
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.bot_channels or not self.bot_channels[guild_id]:
            await ctx.send("📋 Bot có thể hoạt động ở tất cả các kênh")
        else:
            channels = []
            for channel_id in self.bot_channels[guild_id]:
                channel = ctx.guild.get_channel(channel_id) if ctx.guild else None
                if channel:
                    channels.append(f"• {channel.mention}")
            
            if channels:
                await ctx.send(f"📋 **Danh sách kênh bot:**\n" + "\n".join(channels))
            else:
                await ctx.send("📋 Không có kênh bot nào")

    @commands.command(name='clearbotchannels')
    @commands.has_permissions(manage_channels=True)
    async def clear_bot_channels(self, ctx):
        """Clear all bot channels for this guild"""
        if not ctx.guild:
            await ctx.send("Lệnh này chỉ dùng trong server.")
            return
        guild_id = str(ctx.guild.id)
        
        if guild_id in self.bot_channels:
            del self.bot_channels[guild_id]
            self.save_bot_channels()
        
        await ctx.send("✅ Đã xóa tất cả kênh bot. Bot bây giờ hoạt động ở mọi kênh.")

    # Error handlers
    @add_bot_channel_slash.error
    @remove_bot_channel_slash.error
    @clear_bot_channels_slash.error
    async def slash_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Không có quyền",
                description="Bạn cần quyền **Manage Channels** để sử dụng lệnh này",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminChannelsService(bot))