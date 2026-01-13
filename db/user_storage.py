import json
import sqlite3
from typing import Dict, Optional
from models.user import CheckinUser
from datetime import datetime
import os
import tempfile


class UserStorage:
    """用户数据存储 - 支持Vercel环境版（支持内存和文件存储）"""
    
    def __init__(self, db_path: str = None):
        # 检测是否在Vercel等无服务器环境中强制使用内存存储
        if os.environ.get("USE_MEMORY_DB", "").lower() == "true":
            self.use_memory = True
            self.users = {}  # 使用字典作为内存存储
        else:
            self.use_memory = False
            if db_path is None:
                if os.environ.get("VERCEL") or os.environ.get("LAMBDA_TASK_ROOT"):
                    # 在Vercel环境中使用临时目录
                    temp_dir = os.environ.get("TMPDIR", tempfile.gettempdir())
                    self.db_path = os.path.join(temp_dir, "user_data.db")
                else:
                    self.db_path = "user_data.db"
            else:
                self.db_path = db_path
            
            self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        if self.use_memory:
            return  # 内存模式不需要初始化文件数据库
        
        # 确保目录存在
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                timeout_duration INTEGER NOT NULL,
                push_rules TEXT NOT NULL,
                last_checkin_time TEXT,
                timezone TEXT DEFAULT 'Asia/Shanghai'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user(self, user_id: str) -> Optional[CheckinUser]:
        """获取用户"""
        if self.use_memory:
            return self.users.get(user_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT user_id, timeout_duration, push_rules, last_checkin_time, timezone FROM users WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        
        conn.close()
        
        if row is None:
            return None
        
        # 反序列化数据
        user_id, timeout_duration, push_rules_str, last_checkin_time_str, timezone = row
        
        # 解析JSON格式的push_rules
        from models.push_rule import PushRule
        push_rules_data = json.loads(push_rules_str)
        push_rules = [PushRule(**rule_data) for rule_data in push_rules_data]
        
        # 解析时间字符串
        last_checkin_time = None
        if last_checkin_time_str:
            last_checkin_time = datetime.fromisoformat(last_checkin_time_str)
        
        return CheckinUser(
            user_id=user_id,
            timeout_duration=timeout_duration,
            push_rules=push_rules,
            last_checkin_time=last_checkin_time,
            timezone=timezone
        )
    
    def save_user(self, user: CheckinUser):
        """保存用户"""
        if self.use_memory:
            self.users[user.user_id] = user
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 序列化数据
        push_rules_str = json.dumps([rule.dict() for rule in user.push_rules])
        last_checkin_time_str = user.last_checkin_time.isoformat() if user.last_checkin_time else None
        
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, timeout_duration, push_rules, last_checkin_time, timezone)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user.user_id,
            user.timeout_duration,
            push_rules_str,
            last_checkin_time_str,
            user.timezone
        ))
        
        conn.commit()
        conn.close()
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        if self.use_memory:
            if user_id in self.users:
                del self.users[user_id]
                return True
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        affected_rows = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return affected_rows > 0
    
    def get_all_users(self) -> Dict[str, CheckinUser]:
        """获取所有用户"""
        if self.use_memory:
            return self.users.copy()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT user_id, timeout_duration, push_rules, last_checkin_time, timezone FROM users"
        )
        rows = cursor.fetchall()
        
        conn.close()
        
        users = {}
        for row in rows:
            user_id, timeout_duration, push_rules_str, last_checkin_time_str, timezone = row
            
            # 解析JSON格式的push_rules
            from models.push_rule import PushRule
            push_rules_data = json.loads(push_rules_str)
            push_rules = [PushRule(**rule_data) for rule_data in push_rules_data]
            
            # 解析时间字符串
            last_checkin_time = None
            if last_checkin_time_str:
                last_checkin_time = datetime.fromisoformat(last_checkin_time_str)
            
            user = CheckinUser(
                user_id=user_id,
                timeout_duration=timeout_duration,
                push_rules=push_rules,
                last_checkin_time=last_checkin_time,
                timezone=timezone
            )
            users[user_id] = user
        
        return users