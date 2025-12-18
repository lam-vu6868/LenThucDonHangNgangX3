#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để liệt kê tất cả users trong database
"""
import os
import sys
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.database import engine
from app import models

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load .env
load_dotenv()

def list_all_users():
    """Liệt kê tất cả users"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        users = session.query(models.User).all()
        
        if not users:
            print("📭 Không có user nào trong database")
            return
        
        print(f"📋 Danh sách tất cả users ({len(users)} users):")
        print("=" * 80)
        print(f"{'ID':<5} {'Email':<30} {'Tên':<20} {'Role':<10} {'Trạng thái':<15}")
        print("-" * 80)
        
        for user in users:
            status = "✅ Hoạt động" if user.is_active else "❌ Vô hiệu"
            name = user.full_name or "N/A"
            print(f"{user.id:<5} {user.email:<30} {name:<20} {user.role:<10} {status:<15}")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Lỗi khi lấy danh sách users: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    list_all_users()

