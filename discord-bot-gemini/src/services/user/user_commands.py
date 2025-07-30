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
        
        # User stats
        user_id = str(ctx.author.id)
        history = llm_service.summary_service.get_user_history(user_id)
        summary = llm_service.summary_service.get_user_summary(user_id)
        
        embed.add_field(name="Lịch sử", value=f"{len(history)} tin nhắn", inline=True)
        embed.add_field(name="Tóm tắt", value="✅ Có" if summary else "❌ Chưa có", inline=True)
        
        await ctx.reply(embed=embed)

    @commands.command(name='relationships', aliases=['mq', 'relation'])
    async def relationships_command(self, ctx, target_user: Optional[str] = None):
        """Xem mối quan hệ của người dùng"""
        llm_service = self.bot.get_cog('LLMMessageService')
        if not llm_service or not hasattr(llm_service, 'relationship_service'):
            await ctx.reply("❌ Relationship service không khả dụng")
            return
        
        # Xác định user để xem
        if target_user:
            # Admin hoặc user được quyền có thể xem của người khác
            user_id = llm_service.relationship_service._resolve_user_identifier(target_user)
            if not user_id:
                await ctx.reply(f"❌ Không tìm thấy người dùng: {target_user}")
                return
        else:
            user_id = str(ctx.author.id)
        
        user_display_name = llm_service.relationship_service.get_user_display_name(user_id)
        relationships = llm_service.relationship_service.get_user_relationships(user_id)
        interaction_stats = llm_service.relationship_service.get_interaction_stats(user_id)
        
        embed = discord.Embed(
            title=f"🔗 Mối quan hệ của {user_display_name}",
            color=discord.Color.blue()
        )
        
        # Relationships
        if relationships:
            rel_text = ""
            for rel in relationships[:10]:  # Top 10
                rel_text += f"• **{rel['other_person']}**: {rel['relationship_type']}\n"
            embed.add_field(name="Mối quan hệ", value=rel_text, inline=False)
        
        # Interaction stats
        if interaction_stats.get('total_interactions', 0) > 0:
            stats_text = f"Mentions gửi: {interaction_stats.get('mentions_sent', 0)}\n"
            stats_text += f"Mentions nhận: {interaction_stats.get('mentions_received', 0)}\n"
            stats_text += f"Tổng tương tác: {interaction_stats.get('total_interactions', 0)}"
            embed.add_field(name="Thống kê tương tác", value=stats_text, inline=True)
        
        # Top contacts
        if interaction_stats.get('top_contacts'):
            contacts_text = ""
            for contact in interaction_stats['top_contacts'][:5]:
                contacts_text += f"• {contact['name']}: {contact['interaction_count']} lần\n"
            embed.add_field(name="Liên lạc thường xuyên", value=contacts_text, inline=True)
        
        if not relationships and not interaction_stats.get('total_interactions', 0):
            embed.description = "Chưa có thông tin mối quan hệ nào được ghi nhận."
        
        await ctx.reply(embed=embed)

    @commands.command(name='conversation', aliases=['cv', 'convo'])
    async def conversation_command(self, ctx, user1: str, user2: Optional[str] = None, days: int = 7):
        """Xem tóm tắt cuộc trò chuyện giữa hai người"""
        llm_service = self.bot.get_cog('LLMMessageService')
        if not llm_service or not hasattr(llm_service, 'relationship_service'):
            await ctx.reply("❌ Relationship service không khả dụng")
            return
        
        if not user2:
            # Nếu chỉ có 1 user, xem cuộc trò chuyện với chính mình
            user2 = str(ctx.author.id)
        
        try:
            summary = llm_service.relationship_service.get_conversation_summary(user1, user2, days)
            
            embed = discord.Embed(
                title=f"💬 Cuộc trò chuyện ({days} ngày qua)",
                description=summary,
                color=discord.Color.green()
            )
            
            await ctx.reply(embed=embed)
            
        except Exception as e:
            await ctx.reply(f"❌ Lỗi khi lấy cuộc trò chuyện: {str(e)}")

    @commands.command(name='analysis', aliases=['analyze', 'phântích'])
    async def analysis_command(self, ctx, target_user: Optional[str] = None):
        """Phân tích mối quan hệ bằng AI"""
        llm_service = self.bot.get_cog('LLMMessageService')
        if not llm_service or not hasattr(llm_service, 'relationship_service'):
            await ctx.reply("❌ Relationship service không khả dụng")
            return
        
        # Xác định user để phân tích
        if target_user:
            user_identifier = target_user
        else:
            user_identifier = str(ctx.author.id)
        
        try:
            async with ctx.typing():
                analysis = await llm_service.relationship_service.generate_relationship_analysis(user_identifier)
            
            # Split long analysis into multiple messages if needed
            if len(analysis) > 2000:
                parts = [analysis[i:i+2000] for i in range(0, len(analysis), 2000)]
                for i, part in enumerate(parts):
                    if i == 0:
                        await ctx.reply(part)
                    else:
                        await ctx.send(part)
            else:
                await ctx.reply(analysis)
                
        except Exception as e:
            await ctx.reply(f"❌ Lỗi khi tạo phân tích: {str(e)}")

    @commands.command(name='search_relations', aliases=['sr', 'tìm'])
    async def search_relations_command(self, ctx, *, keyword: str):
        """Tìm kiếm mối quan hệ theo từ khóa"""
        llm_service = self.bot.get_cog('LLMMessageService')
        if not llm_service or not hasattr(llm_service, 'relationship_service'):
            await ctx.reply("❌ Relationship service không khả dụng")
            return
        
        try:
            results = llm_service.relationship_service.search_relationships_by_keyword(keyword)
            
            if not results:
                await ctx.reply(f"❌ Không tìm thấy mối quan hệ nào với từ khóa: '{keyword}'")
                return
            
            embed = discord.Embed(
                title=f"🔍 Kết quả tìm kiếm: '{keyword}'",
                color=discord.Color.orange()
            )
            
            for i, result in enumerate(results[:5], 1):  # Top 5 results
                embed.add_field(
                    name=f"{i}. {result['person1']} ↔ {result['person2']}",
                    value=f"**{result['relationship_type']}**\n"
                          f"Context: {result['context'][:100]}...\n"
                          f"Reported by: {result['reported_by']}",
                    inline=False
                )
            
            await ctx.reply(embed=embed)
            
        except Exception as e:
            await ctx.reply(f"❌ Lỗi khi tìm kiếm: {str(e)}")

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