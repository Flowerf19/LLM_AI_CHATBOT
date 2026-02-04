"""
Typing Commands - Commands for testing and configuring typing simulation.

Responsibility: Provide commands to test and view typing simulation settings.
"""
import logging
import discord
from discord.ext import commands
from src.config.settings import Config

logger = logging.getLogger('discord_bot.TypingCommands')


class TypingCommands(commands.Cog):
    """Commands for typing simulation testing and configuration."""
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("⌨️ TypingCommands initialized")

    def _get_llm_service(self):
        """Get LLMMessageService for typing functionality."""
        return self.bot.get_cog('LLMMessageService')

    @commands.command(name='test_typing')
    async def test_typing_command(self, ctx):
        """Test typing simulation effect."""
        test_response = """Đây là test typing effect!  😊

Câu này sẽ được gửi riêng lẻ với typing delay tự nhiên.  

Và cuối cùng là câu này!  (づ｡◕‿‿◕｡)づ"""
        
        llm_service = self._get_llm_service()
        if llm_service and hasattr(llm_service, 'send_response_in_parts'):
            await llm_service.send_response_in_parts(ctx.message, test_response, str(ctx.author.id))
        else:
            # Fallback: send without typing simulation
            await ctx.reply(test_response)

    @commands.command(name='typing_settings')
    @commands.has_permissions(manage_messages=True)
    async def typing_settings_command(self, ctx):
        """Show current typing simulation settings (Admin only)."""
        embed = discord.Embed(
            title="⌨️ Typing Simulation Settings",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Status", 
            value="✅ Enabled" if Config.ENABLE_TYPING_SIMULATION else "❌ Disabled",
            inline=True
        )
        embed.add_field(name="Speed (WPM)", value=str(Config.TYPING_SPEED_WPM), inline=True)
        embed.add_field(name="Min Delay (s)", value=str(Config.MIN_TYPING_DELAY), inline=True)
        embed.add_field(name="Max Delay (s)", value=str(Config.MAX_TYPING_DELAY), inline=True)
        embed.add_field(name="Break Delay (s)", value=str(Config.PART_BREAK_DELAY), inline=True)
        
        embed.set_footer(text="Để thay đổi, sửa file .env và restart bot")
        
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(TypingCommands(bot))
