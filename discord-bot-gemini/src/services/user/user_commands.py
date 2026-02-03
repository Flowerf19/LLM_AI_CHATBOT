from discord.ext import commands
import discord
from typing import Optional

class UserCommandsCog(commands.Cog):
    """User-facing commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='ping')
    async def ping_command(self, ctx):
        """Simple ping command to test if bot is responsive"""
        await ctx.reply("🏓 Pong! Bot đang hoạt động!")

    @commands.command(name='status')
    async def status_command(self, ctx):
        """Check bot status and configuration"""
        llm_service = self.bot.get_cog('LLMMessageService')
        if not llm_service:
            await ctx.reply("❌ LLM service not available")
            return
            
        embed = discord.Embed(title="🤖 Bot Status", color=discord.Color.green())
        
        # Basic info
        if ctx.guild:
            admin_service = self.bot.get_cog('AdminChannelsService')
            if admin_service and admin_service.is_bot_channel(ctx.guild.id, ctx.channel.id):
                embed.add_field(name="Kênh này", value="✅ Bot channel", inline=True)
            else:
                embed.add_field(name="Kênh này", value="⚠️ Cần mention bot", inline=True)
        else:
            embed.add_field(name="Loại kênh", value="📩 DM", inline=True)
        
        # User stats - Simplified without summary service
        user_id = str(ctx.author.id)
        
        embed.add_field(name="User ID", value=user_id, inline=True)
        embed.add_field(name="Status", value="✅ Bot hoạt động", inline=True)
        
        await ctx.reply(embed=embed)

    @commands.command(name='relationships', aliases=['mq', 'relation'])
    async def relationships_command(self, ctx, target_user: Optional[str] = None):
        """Xem mối quan hệ của người dùng - TÍNH NĂNG TẠM THỜI KHÔNG KHẢ DỤNG"""
        await ctx.reply("❌ Tính năng relationship tracking tạm thời không khả dụng")

    @commands.command(name='conversation', aliases=['cv', 'convo'])
    async def conversation_command(self, ctx, user1: str, user2: Optional[str] = None, days: int = 7):
        """Xem tóm tắt cuộc trò chuyện giữa hai người - TÍNH NĂNG TẠM THỜI KHÔNG KHẢ DỤNG"""
        await ctx.reply("❌ Tính năng conversation tracking tạm thời không khả dụng")

    @commands.command(name='analysis', aliases=['analyze', 'phântích'])
    async def analysis_command(self, ctx, target_user: Optional[str] = None):
        """Phân tích mối quan hệ bằng AI - TÍNH NĂNG TẠM THỜI KHÔNG KHẢ DỤNG"""
        await ctx.reply("❌ Tính năng relationship analysis tạm thời không khả dụng")

    @commands.command(name='search_relations', aliases=['sr', 'tìm'])
    async def search_relations_command(self, ctx, *, keyword: str):
        """Tìm kiếm mối quan hệ theo từ khóa - TÍNH NĂNG TẠM THỜI KHÔNG KHẢ DỤNG"""
        await ctx.reply("❌ Tính năng search relationships tạm thời không khả dụng")

    @commands.command(name='mentions', aliases=['tag'])
    async def mentions_command(self, ctx, user1: str, user2: str):
        """Xem lịch sử mentions giữa hai người"""
        llm_service = self.bot.get_cog('LLMMessageService')
        if not llm_service or not hasattr(llm_service, 'relationship_service'):
            await ctx.reply("❌ Relationship service không khả dụng")
            return
        
        try:
            mentions = llm_service.relationship_service.get_user_mentions_to(user1, user2)
            
            if not mentions:
                user1_name = llm_service.relationship_service.get_user_display_name(
                    llm_service.relationship_service._resolve_user_identifier(user1) or user1
                )
                user2_name = llm_service.relationship_service.get_user_display_name(
                    llm_service.relationship_service._resolve_user_identifier(user2) or user2
                )
                await ctx.reply(f"❌ Không tìm thấy mentions từ {user1_name} đến {user2_name}")
                return
            
            embed = discord.Embed(
                title=f"🏷️ Mentions: {user1} → {user2}",
                color=discord.Color.purple()
            )
            
            recent_mentions = mentions[-10:]  # 10 mentions gần nhất
            mention_text = ""
            for mention in recent_mentions:
                mention_text += f"• **{mention['type']}**: {mention['context'][:50]}...\n"
            
            embed.description = mention_text
            embed.add_field(name="Tổng mentions", value=str(len(mentions)), inline=True)
            
            await ctx.reply(embed=embed)
            
        except Exception as e:
            await ctx.reply(f"❌ Lỗi khi lấy mentions: {str(e)}")

    @commands.command(name='all_users', aliases=['users', 'members'])
    @commands.has_permissions(manage_messages=True)
    async def all_users_command(self, ctx):
        """Xem tóm tắt tất cả users (Admin only)"""
        llm_service = self.bot.get_cog('LLMMessageService')
        if not llm_service or not hasattr(llm_service, 'relationship_service'):
            await ctx.reply("❌ Relationship service không khả dụng")
            return
        
        try:
            summary = llm_service.relationship_service.get_all_users_summary()
            
            embed = discord.Embed(
                title="👥 Tóm tắt tất cả users",
                color=discord.Color.gold()
            )
            
            embed.add_field(
                name="Thống kê tổng",
                value=f"Users: {summary['total_users']}\n"
                      f"Relationships: {summary['total_relationships']}\n"
                      f"Interactions: {summary['total_interactions']}",
                inline=False
            )
            
            # Top active users
            top_users = summary['users'][:10]
            users_text = ""
            for user in top_users:
                users_text += f"• **{user['display_name']}**: {user['interaction_stats'].get('total_interactions', 0)} tương tác\n"
            
            embed.add_field(name="Top Users", value=users_text, inline=False)
            
            await ctx.reply(embed=embed)
            
        except Exception as e:
            await ctx.reply(f"❌ Lỗi khi lấy dữ liệu: {str(e)}")

    # ...existing code...

async def setup(bot):
    await bot.add_cog(UserCommandsCog(bot))