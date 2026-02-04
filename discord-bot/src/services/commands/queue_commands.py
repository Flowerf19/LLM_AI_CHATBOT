"""
Queue Commands - Commands for managing conversation queue and debugging duplicates.

Responsibility: Provide admin commands for queue inspection and management.
"""
import logging
import discord
from discord.ext import commands

logger = logging.getLogger('discord_bot.QueueCommands')


class QueueCommands(commands.Cog):
    """Commands for conversation queue management and debugging."""
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("📋 QueueCommands initialized")
    
    def _get_queue_manager(self):
        """Get MessageQueueManager from LLMMessageService."""
        llm_service = self.bot.get_cog('LLMMessageService')
        if llm_service and hasattr(llm_service, 'queue_manager'):
            return llm_service.queue_manager
        return None

    @commands.command(name='queue_status')
    async def queue_status_command(self, ctx):
        """Check conversation queue status."""
        queue_manager = self._get_queue_manager()
        if not queue_manager:
            await ctx.reply("❌ Queue manager not available")
            return
            
        status = queue_manager.get_queue_status()
        
        embed = discord.Embed(title="📋 Conversation Queue Status", color=discord.Color.blue())
        
        if status['currently_responding_to']:
            embed.add_field(
                name="🔒 Currently Responding To", 
                value=f"User ID: {status['currently_responding_to']} ({status['lock_duration']}s)", 
                inline=False
            )
        else:
            embed.add_field(name="🔓 Status", value="Available", inline=False)
        
        embed.add_field(name="⏳ Pending Messages", value=str(status['pending_count']), inline=True)
        
        if status['pending_users']:
            pending_display = ", ".join([f"User {uid}" for uid in status['pending_users']])
            embed.add_field(name="👥 Waiting Users", value=pending_display, inline=False)
        
        await ctx.reply(embed=embed)

    @commands.command(name='clear_queue')
    async def clear_queue_command(self, ctx):
        """Clear pending message queue (requires Manage Messages permission)."""
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.reply("❌ You need Manage Messages permission to use this command")
            return
            
        queue_manager = self._get_queue_manager()
        if not queue_manager:
            await ctx.reply("❌ Queue manager not available")
            return
            
        count = queue_manager.clear_pending_queue()
        await ctx.reply(f"✅ Cleared {count} pending messages from queue")

    @commands.command(name='debug_duplicate')
    async def debug_duplicate_command(self, ctx):
        """Debug duplicate response issues."""
        queue_manager = self._get_queue_manager()
        if not queue_manager:
            await ctx.reply("❌ Queue manager not available")
            return
            
        debug_info = queue_manager.message_processor.get_debug_info()
        
        embed = discord.Embed(title="🔍 Duplicate Response Debug", color=discord.Color.orange())
        embed.add_field(name="Processed Messages", value=debug_info['processed_count'], inline=True)
        embed.add_field(name="Currently Processing", value=debug_info['processing_count'], inline=True)
        embed.add_field(name="Message Locks", value=debug_info['locks_count'], inline=True)
        
        if debug_info['recent_processed']:
            recent = "\n".join([f"`{msg}`" for msg in debug_info['recent_processed']])
            embed.add_field(name="Recent Processed", value=recent, inline=False)
        
        if debug_info['current_processing']:
            current = "\n".join([f"`{msg}`" for msg in debug_info['current_processing']])
            embed.add_field(name="Currently Processing", value=current, inline=False)
        
        if debug_info['locked_messages']:
            locked = "\n".join([f"`{msg}`" for msg in debug_info['locked_messages']])
            embed.add_field(name="Locked Messages", value=locked, inline=False)
        
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(QueueCommands(bot))
