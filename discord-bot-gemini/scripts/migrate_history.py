"""
Migrate conversation history từ src/data/user_summaries/ sang data/user_profiles/
"""
import json
import shutil
from pathlib import Path

def migrate_history():
    old_dir = Path("src/data/user_summaries")
    new_base_dir = Path("data/user_profiles")
    
    if not old_dir.exists():
        print("❌ Old directory không tồn tại")
        return
    
    print("🔄 Migrating conversation history...\n")
    
    migrated = 0
    for old_file in old_dir.glob("*_history.json"):
        user_id = old_file.stem.replace("_history", "")
        
        # Create new structure
        new_user_dir = new_base_dir / user_id
        new_user_dir.mkdir(parents=True, exist_ok=True)
        
        new_file = new_user_dir / "history.json"
        
        # Copy file
        shutil.copy2(old_file, new_file)
        print(f"✅ Migrated: {user_id}")
        print(f"   From: {old_file}")
        print(f"   To:   {new_file}\n")
        
        migrated += 1
    
    print(f"\n✅ Migrated {migrated} history files")
    print("\n💡 Old files still exist in src/data/user_summaries/")
    print("   You can delete them after verifying migration worked")

if __name__ == "__main__":
    migrate_history()
