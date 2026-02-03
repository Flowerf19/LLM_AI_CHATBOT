import os
import logging
import aiofiles
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import Counter
from config.settings import Config
from services.relationship.relationship_data import RelationshipDataManager

logger = logging.getLogger(__name__)

class RelationshipService:
    def __init__(self, llm_service):
        self.llm_service = llm_service
        
        # Use RelationshipDataManager for I/O operations (Repository Pattern)
        self.data_manager = RelationshipDataManager()
        
        self.data_dir = Config.DATA_DIR
        self.relationships_dir = self.data_dir / 'relationships'
        self.relationships_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing data using data_manager
        self.relationships = self.data_manager.load_relationships()
        self.user_names = self.data_manager.load_user_names()
        self.interactions = self.data_manager.load_interactions()
        self.conversation_history = self.data_manager.load_conversation_history()
        logger.info(f"🔗 RelationshipService initialized with {len(self.relationships)} relationships")
    
    async def update_server_relationships_summary(self):
        """Auto-generate and update server_relationships.txt with pure JSON data"""
        import json
        summary_data = self.get_all_users_summary()
        
        # Build pure JSON structure
        json_data = {
            "statistics": {
                "total_users": summary_data["total_users"],
                "total_relationships": summary_data["total_relationships"],
                "total_interactions": summary_data["total_interactions"]
            },
            "users": summary_data["users"],
            "relationships": list(self.relationships.values()),
            "interactions": self.interactions,
            "generated_at": datetime.now().isoformat()
        }
        
        server_summary_path = self.data_dir / "server_relationships.json"
        async with aiofiles.open(server_summary_path, mode="w", encoding="utf-8") as f:
            await f.write(json.dumps(json_data, ensure_ascii=False, indent=2))

    def _build_server_relationships_prompt(self, summary_data: dict) -> str:
        """Build prompt for AI to summarize all server relationships"""
        prompt_file = Config.PROMPTS_DIR / 'server_relationships_prompt.json'
        if not os.path.exists(prompt_file):
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        # Chèn số liệu tổng quan và chi tiết vào template
        summary_overview = f"TỔNG NGƯỜI DÙNG: {summary_data['total_users']}\nTỔNG MỐI QUAN HỆ: {summary_data['total_relationships']}\nTỔNG TƯƠNG TÁC: {summary_data['total_interactions']}\n"
        user_lines = []
        for user in summary_data['users']:
            user_lines.append(f"- User ID: {user['user_id']}: {user['relationship_count']} mối quan hệ, {user['interaction_stats'].get('total_interactions', 0)} tương tác")
        user_lines.append("\nDỮ LIỆU CHI TIẾT:")
        for user in summary_data['users']:
            user_lines.append(f"\n=== User ID: {user['user_id']} ===")
            user_lines.append(f"Tên thật: {user.get('real_name', '')}")
            user_lines.append(f"Số mối quan hệ: {user['relationship_count']}")
            user_lines.append(f"Tổng tương tác: {user['interaction_stats'].get('total_interactions', 0)}")
            if user['interaction_stats'].get('top_contacts'):
                contacts = ", ".join([f"User ID: {c['user_id']} ({c['interaction_count']})" for c in user['interaction_stats']['top_contacts']])
                user_lines.append(f"Liên lạc thường xuyên: {contacts}")
        prompt = prompt_template.replace('[TỔNG QUAN SỐ LIỆU SẼ ĐƯỢC CHÈN Ở ĐÂY]', summary_overview)
        prompt = prompt.replace('[DỮ LIỆU CHI TIẾT SẼ ĐƯỢC CHÈN Ở ĐÂY]', "\n".join(user_lines))
        return prompt

    async def auto_update_server_summary_on_change(self):
        """Call this after any relationship/interactions update to keep server_relationships.txt fresh."""
        await self.update_server_relationships_summary()
    
    def _save_relationships(self):
        """Save relationship data to file - delegates to RelationshipDataManager."""
        self.data_manager.save_relationships(self.relationships)
        # Trigger server summary update (fire and forget)
        try:
            import asyncio
            if asyncio.get_event_loop().is_running():
                asyncio.create_task(self.auto_update_server_summary_on_change())
        except Exception as e:
            logger.error(f"Error scheduling server summary update: {e}")
    
    def _save_user_names(self):
        """Save user names mapping to file - delegates to RelationshipDataManager."""
        self.data_manager.save_user_names(self.user_names)
    
    def _save_interactions(self):
        """Save interaction data to file - delegates to RelationshipDataManager."""
        self.data_manager.save_interactions(self.interactions)
        # Trigger server summary update (fire and forget)
        try:
            import asyncio
            if asyncio.get_event_loop().is_running():
                asyncio.create_task(self.auto_update_server_summary_on_change())
        except Exception as e:
            logger.error(f"Error scheduling server summary update: {e}")
    
    def _save_conversation_history(self):
        """Save conversation history - delegates to RelationshipDataManager."""
        self.data_manager.save_conversation_history(self.conversation_history)
        # Trigger server summary update (fire and forget)
        try:
            import asyncio
            if asyncio.get_event_loop().is_running():
                asyncio.create_task(self.auto_update_server_summary_on_change())
        except Exception as e:
            logger.error(f"Error scheduling server summary update: {e}")
    
    def update_user_name(self, user_id: str, username: str, display_name: Optional[str] = None, real_name: Optional[str] = None):
        """Update user name information"""
        if user_id not in self.user_names:
            self.user_names[user_id] = {
                'username': username,
                'display_name': display_name,
                'real_name': real_name,
                'name_history': [username],
                'first_seen': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        else:
            # Update existing info
            self.user_names[user_id]['username'] = username
            if display_name:
                self.user_names[user_id]['display_name'] = display_name
            if real_name and real_name != self.user_names[user_id].get('real_name'):
                self.user_names[user_id]['real_name'] = real_name
                logger.info(f"📝 Real name updated for {user_id}: {real_name}")
            
            # Track name history
            if username not in self.user_names[user_id]['name_history']:
                self.user_names[user_id]['name_history'].append(username)
            
            self.user_names[user_id]['last_updated'] = datetime.now().isoformat()
        
        self._save_user_names()
    
    def get_user_display_name(self, user_id: str) -> str:
        """Get the best display name for a user (real name > display name > username)"""
        if user_id not in self.user_names:
            return f"User_{user_id[-4:]}"  # Fallback với 4 số cuối của ID
        
        user_info = self.user_names[user_id]
        
        # Ưu tiên: tên thật > display name > username
        if user_info.get('real_name'):
            return user_info['real_name']
        elif user_info.get('display_name'):
            return user_info['display_name']
        else:
            return user_info['username']
    
    def process_message(self, author_id: str, author_username: str, message_content: str, mentioned_user_ids: Optional[List[str]] = None, channel_id: Optional[str] = None):
        """Process a message to update relationship information (giao cho LLM xử lý hoàn toàn)"""
        # Update author's name info
        self.update_user_name(author_id, author_username)
        # Record conversation for history
        self._record_conversation(author_id, message_content, mentioned_user_ids or [], channel_id)
        # Không còn extract relationship info bằng pattern, mọi phân tích sẽ do LLM xử lý khi cần
    
    def _record_interactions(self, author_id: str, target_user_ids: List[str], interaction_type: str, context: str = ""):
        """Record interactions between users"""
        timestamp = datetime.now().isoformat()
        
        for target_id in target_user_ids:
            # Create interaction key
            interaction_key = f"{author_id}_{target_id}"
            
            if interaction_key not in self.interactions:
                self.interactions[interaction_key] = {
                    'from_user': author_id,
                    'to_user': target_id,
                    'interactions': []
                }
            
            # Add interaction
            self.interactions[interaction_key]['interactions'].append({
                'type': interaction_type,
                'timestamp': timestamp,
                'context': context[:200]  # Limit context length
            })
            
            # Keep only recent interactions (last 100)
            if len(self.interactions[interaction_key]['interactions']) > 100:
                self.interactions[interaction_key]['interactions'] = \
                    self.interactions[interaction_key]['interactions'][-100:]
        
        self._save_interactions()
    
    def _record_conversation(self, author_id: str, message_content: str, mentioned_users: List[str], channel_id: Optional[str]):
        """Record conversation history between users"""
        timestamp = datetime.now().isoformat()
        
        # Record conversation entry
        conversation_entry = {
            'author_id': author_id,
            'message': message_content[:500],  # Limit message length
            'mentioned_users': mentioned_users,
            'channel_id': channel_id,
            'timestamp': timestamp
        }
        
        # Group conversations by participants
        participants = sorted([author_id] + mentioned_users)
        conversation_key = "_".join(participants)
        
        if conversation_key not in self.conversation_history:
            self.conversation_history[conversation_key] = {
                'participants': participants,
                'messages': []
            }
        
        self.conversation_history[conversation_key]['messages'].append(conversation_entry)
        
        # Keep only recent messages (last 50 per conversation)
        if len(self.conversation_history[conversation_key]['messages']) > 50:
            self.conversation_history[conversation_key]['messages'] = \
                self.conversation_history[conversation_key]['messages'][-50:]
        
        self._save_conversation_history()
    
    def _add_relationship(self, person1: str, person2: str, relationship_type: str, reported_by: str, context: str, confidence: float):
        """Add or update a relationship"""
        # Normalize names and create a consistent key
        person1_lower = person1.lower().strip()
        person2_lower = person2.lower().strip()
        
        # Create sorted key to avoid duplicates (A->B vs B->A)
        if person1_lower < person2_lower:
            rel_key = f"{person1_lower}_{person2_lower}"
            persons = (person1, person2)
        else:
            rel_key = f"{person2_lower}_{person1_lower}"
            persons = (person2, person1)
        
        timestamp = datetime.now().isoformat()
        
        if rel_key not in self.relationships:
            self.relationships[rel_key] = {
                'person1': persons[0],
                'person2': persons[1],
                'relationship_history': []
            }
        
        # Add relationship entry
        relationship_entry = {
            'type': relationship_type,
            'reported_by': reported_by,
            'context': context,
            'confidence': confidence,
            'timestamp': timestamp
        }
        
        self.relationships[rel_key]['relationship_history'].append(relationship_entry)
        
        # Keep only recent relationship updates (last 20)
        if len(self.relationships[rel_key]['relationship_history']) > 20:
            self.relationships[rel_key]['relationship_history'] = \
                self.relationships[rel_key]['relationship_history'][-20:]
        
        self._save_relationships()
        
        logger.info(f"🔗 Added relationship: {person1} - {person2} ({relationship_type}) reported by {reported_by}")
    
    def get_user_relationships(self, user_identifier: str) -> List[Dict]:
        """Get all relationships for a user (by ID, username, or real name)"""
        relationships = []
        
        # Find user ID from identifier
        user_id = self._resolve_user_identifier(user_identifier)
        if not user_id:
            return relationships
        
        # Get username from user_names (person1/person2 in relationships use username, not display_name)
        user_info = self.user_names.get(user_id, {})
        username = user_info.get('username', '').lower()
        if not username:
            return relationships
        
        for rel_key, rel_data in self.relationships.items():
            person1 = rel_data['person1'].lower()
            person2 = rel_data['person2'].lower()
            
            if username == person1 or username == person2:
                # Get the latest relationship status
                if rel_data['relationship_history']:
                    latest_rel = rel_data['relationship_history'][-1]
                    other_person = rel_data['person2'] if username == person1 else rel_data['person1']
                    
                    relationships.append({
                        'other_person': other_person,
                        'relationship_type': latest_rel['type'],
                        'reported_by': latest_rel['reported_by'],
                        'context': latest_rel['context'],
                        'timestamp': latest_rel['timestamp'],
                        'confidence': latest_rel['confidence']
                    })
        
        return relationships
    
    def get_interaction_stats(self, user_identifier: str) -> Dict:
        """Get interaction statistics for a user"""
        user_id = self._resolve_user_identifier(user_identifier)
        if not user_id:
            return {}
        
        # Count mentions and interactions
        mentions_sent = 0
        mentions_received = 0
        frequent_contacts = Counter()
        
        for interaction_key, interaction_data in self.interactions.items():
            if interaction_data['from_user'] == user_id:
                mentions_sent += len(interaction_data['interactions'])
                frequent_contacts[interaction_data['to_user']] += len(interaction_data['interactions'])
            elif interaction_data['to_user'] == user_id:
                mentions_received += len(interaction_data['interactions'])
        
        # Get top contacts
        top_contacts = []
        for contact_id, count in frequent_contacts.most_common(5):
            contact_name = self.get_user_display_name(contact_id)
            top_contacts.append({
                'name': contact_name,
                'user_id': contact_id,
                'interaction_count': count
            })
        
        return {
            'mentions_sent': mentions_sent,
            'mentions_received': mentions_received,
            'total_interactions': mentions_sent + mentions_received,
            'top_contacts': top_contacts
        }
    
    def get_conversation_summary(self, user1_identifier: str, user2_identifier: str, days_back: int = 7) -> str:
        """Get conversation summary between two users"""
        user1_id = self._resolve_user_identifier(user1_identifier)
        user2_id = self._resolve_user_identifier(user2_identifier)
        
        if not user1_id or not user2_id:
            return "Không tìm thấy thông tin người dùng."
        
        # Find conversation between these users
        participants = sorted([user1_id, user2_id])
        conversation_key = "_".join(participants)
        
        if conversation_key not in self.conversation_history:
            return f"Không có lịch sử trò chuyện giữa {self.get_user_display_name(user1_id)} và {self.get_user_display_name(user2_id)}."
        
        # Filter messages from the last N days
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_messages = []
        
        for msg in self.conversation_history[conversation_key]['messages']:
            msg_date = datetime.fromisoformat(msg['timestamp'])
            if msg_date >= cutoff_date:
                recent_messages.append(msg)
        
        if not recent_messages:
            return f"Không có cuộc trò chuyện nào trong {days_back} ngày qua giữa {self.get_user_display_name(user1_id)} và {self.get_user_display_name(user2_id)}."
        
        # Format conversation for summary
        conversation_text = ""
        for msg in recent_messages[-10:]:  # Last 10 messages
            author_name = self.get_user_display_name(msg['author_id'])
            conversation_text += f"{author_name}: {msg['message']}\n"
        
        return f"Cuộc trò chuyện gần đây giữa {self.get_user_display_name(user1_id)} và {self.get_user_display_name(user2_id)}:\n\n{conversation_text}"
    
    async def generate_relationship_analysis(self, user_identifier: str) -> str:
        """Generate AI analysis of user's relationships"""
        user_id = self._resolve_user_identifier(user_identifier)
        if not user_id:
            # Load message from file nếu muốn đa ngôn ngữ, còn không thì giữ lại string ngắn này
            return "Không tìm thấy thông tin người dùng."
        user_name = self.get_user_display_name(user_id)
        relationships = self.get_user_relationships(user_identifier)
        interaction_stats = self.get_interaction_stats(user_identifier)
        if not relationships and not interaction_stats.get('total_interactions', 0):
            # Load message từ file nếu muốn, còn không thì giữ lại string ngắn này
            return f"Chưa có thông tin về mối quan hệ của {user_name}."
        # Build relationship string
        relationships_str = ""
        for rel in relationships:
            relationships_str += f"- {rel['other_person']}: {rel['relationship_type']} (độ tin cậy: {rel['confidence']}, được báo cáo bởi: {self.get_user_display_name(rel['reported_by'])})\n"
        # Build top contacts string
        top_contacts_str = ""
        for contact in interaction_stats.get('top_contacts', []):
            top_contacts_str += f"- {contact['name']}: {contact['interaction_count']} lần tương tác\n"
        # Load prompt template from file
        prompt_file = os.path.join(self.data_dir, '..', 'prompts', 'relationship_analysis_prompt.txt')
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                analysis_prompt_template = f.read()
        except Exception as e:
            logger.error(f"Error loading relationship analysis prompt: {e}")
            # Nếu không load được file, trả về thông báo lỗi ngắn
            return f"Không thể tạo phân tích cho {user_name} lúc này."
        # Format prompt
        analysis_prompt = analysis_prompt_template.format(
            user_name=user_name,
            user_id=user_id,
            relationships=relationships_str.strip(),
            mentions_sent=interaction_stats.get('mentions_sent', 0),
            mentions_received=interaction_stats.get('mentions_received', 0),
            total_interactions=interaction_stats.get('total_interactions', 0),
            top_contacts=top_contacts_str.strip()
        )
        try:
            analysis = await self.llm_service.generate_response(analysis_prompt, user_id)
            return f"📊 **Phân tích mối quan hệ của {user_name}:**\n\n{analysis}"
        except Exception as e:
            logger.error(f"Error generating relationship analysis: {e}")
            return f"Không thể tạo phân tích cho {user_name} lúc này."
    
    def _resolve_user_identifier(self, identifier: str) -> Optional[str]:
        """Resolve user identifier (ID, username, or real name) to user ID"""
        # Direct ID match
        if identifier in self.user_names:
            return identifier
        
        # Search by username or real name
        identifier_lower = identifier.lower().strip()
        
        for user_id, user_info in self.user_names.items():
            # Check username
            if user_info.get('username', '').lower() == identifier_lower:
                return user_id
            
            # Check display name
            if user_info.get('display_name', '').lower() == identifier_lower:
                return user_id
            
            # Check real name
            if user_info.get('real_name', '').lower() == identifier_lower:
                return user_id
            
            # Check name history
            for name in user_info.get('name_history', []):
                if name.lower() == identifier_lower:
                    return user_id
        
        return None
    
    def search_relationships_by_keyword(self, keyword: str) -> List[Dict]:
        """Search relationships by keyword in context"""
        results = []
        keyword_lower = keyword.lower()
        
        for rel_key, rel_data in self.relationships.items():
            for rel_entry in rel_data['relationship_history']:
                if keyword_lower in rel_entry['context'].lower():
                    results.append({
                        'person1': rel_data['person1'],
                        'person2': rel_data['person2'],
                        'relationship_type': rel_entry['type'],
                        'context': rel_entry['context'],
                        'timestamp': rel_entry['timestamp'],
                        'reported_by': self.get_user_display_name(rel_entry['reported_by'])
                    })
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x['timestamp'], reverse=True)
        return results[:10]  # Return top 10 results
    
    def get_user_mentions_to(self, user_identifier: str, target_identifier: str) -> List[Dict]:
        """Get mentions from one user to another"""
        user_id = self._resolve_user_identifier(user_identifier)
        target_id = self._resolve_user_identifier(target_identifier)
        
        if not user_id or not target_id:
            return []
        
        interaction_key = f"{user_id}_{target_id}"
        
        if interaction_key in self.interactions:
            return self.interactions[interaction_key]['interactions']
        
        return []
    
    def get_all_users_summary(self) -> Dict:
        """Get summary of all tracked users"""
        summary = {
            'total_users': len(self.user_names),
            'total_relationships': len(self.relationships),
            'total_interactions': sum(len(data['interactions']) for data in self.interactions.values()),
            'users': []
        }
        
        for user_id, user_info in self.user_names.items():
            user_summary = {
                'user_id': user_id,
                'display_name': self.get_user_display_name(user_id),
                'username': user_info.get('username', ''),
                'real_name': user_info.get('real_name', ''),
                'first_seen': user_info.get('first_seen', ''),
                'relationship_count': len(self.get_user_relationships(user_id)),
                'interaction_stats': self.get_interaction_stats(user_id)
            }
            summary['users'].append(user_summary)
        
        # Sort users by total interactions
        summary['users'].sort(key=lambda x: x['interaction_stats'].get('total_interactions', 0), reverse=True)
        
        return summary
