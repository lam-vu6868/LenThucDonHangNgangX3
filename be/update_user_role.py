#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để cập nhật role của user thành admin
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

def update_user_role(email: str, new_role: str = "admin"):
    """Cập nhật role của user"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Tìm user theo email
        user = session.query(models.User).filter(models.User.email == email).first()
        
        if not user:
            print(f"❌ Không tìm thấy user với email: {email}")
            return False
        
        # Hiển thị thông tin hiện tại
        print(f"📋 Thông tin user hiện tại:")
        print(f"   Email: {user.email}")
        print(f"   Tên: {user.full_name or 'N/A'}")
        print(f"   Role hiện tại: {user.role}")
        print(f"   Trạng thái: {'Hoạt động' if user.is_active else 'Vô hiệu'}")
        
        # Cập nhật role
        old_role = user.role
        user.role = new_role
        
        # Lưu thay đổi
        session.commit()
        session.refresh(user)
        
        print(f"\n✅ Đã cập nhật thành công!")
        print(f"   Role cũ: {old_role}")
        print(f"   Role mới: {user.role}")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"❌ Lỗi khi cập nhật: {str(e)}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    # Email của user cần cập nhật (có thể truyền từ command line)
    if len(sys.argv) > 1:
        user_email = sys.argv[1]
    else:
        # Mặc định: tìm user có tên "akitok" hoặc email chứa "akitok"
        user_email = None
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            # Tìm theo email hoặc full_name
            user = session.query(models.User).filter(
                (models.User.email.contains("akitok")) |
                (models.User.full_name == "akitok")
            ).first()
            if user:
                user_email = user.email
            session.close()
        except:
            pass
    
    if not user_email:
        print("❌ Không tìm thấy user. Vui lòng chỉ định email:")
        print("   python update_user_role.py <email>")
        print("\nHoặc chạy list_users.py để xem danh sách users")
        sys.exit(1)
    
    print(f"🔧 Đang cập nhật role của user: {user_email}")
    print("-" * 50)
    
    success = update_user_role(user_email, "admin")
    
    if success:
        print("\n🎉 Hoàn tất! User đã được cập nhật thành admin.")
    else:
        print("\n⚠️  Không thể cập nhật user.")
        sys.exit(1)

