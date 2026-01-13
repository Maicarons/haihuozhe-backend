#!/usr/bin/env python3
"""
测试修复后的 UserStorage 类
"""

import os
import tempfile
from db.user_storage import UserStorage
from models.user import CheckinUser
from models.push_rule import PushRule


def test_user_storage():
    print("Testing UserStorage with memory backend...")
    
    # 强制使用内存后端
    os.environ["USE_MEMORY_DB"] = "true"
    
    storage = UserStorage()
    
    # 创建一个测试用户
    test_rule = PushRule(
        id="test_rule_1",
        type="dingtalk",
        config={"webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=test"}
    )
    
    test_user = CheckinUser(
        user_id="test_user_1",
        timeout_duration=24,
        push_rules=[test_rule],
        timezone="Asia/Shanghai"
    )
    
    # 保存用户
    storage.save_user(test_user)
    print("User saved successfully")
    
    # 获取用户
    retrieved_user = storage.get_user("test_user_1")
    if retrieved_user:
        print(f"Retrieved user: {retrieved_user.user_id}")
        print(f"Timeout duration: {retrieved_user.timeout_duration}")
        print(f"Number of push rules: {len(retrieved_user.push_rules)}")
    else:
        print("Failed to retrieve user")
    
    # 获取所有用户
    all_users = storage.get_all_users()
    print(f"Total users: {len(all_users)}")
    
    # 删除用户
    deleted = storage.delete_user("test_user_1")
    print(f"User deleted: {deleted}")
    
    # 验证用户已被删除
    remaining_user = storage.get_user("test_user_1")
    print(f"User after deletion: {remaining_user}")


if __name__ == "__main__":
    test_user_storage()