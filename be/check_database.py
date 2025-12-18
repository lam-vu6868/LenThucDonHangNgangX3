#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script kiem tra database co du lieu chua
"""
import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("[ERROR] Khong tim thay DATABASE_URL trong .env")
    exit(1)

db_info = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'database'
print(f"[INFO] Dang ket noi den: {db_info}...")

try:
    # Tao engine
    engine = create_engine(DATABASE_URL)
    
    # Kiem tra ket noi
    with engine.connect() as conn:
        print("[OK] Ket noi database thanh cong!\n")
    
    # Lay danh sach cac bang
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        print("[INFO] Chua co bang nao trong database")
        print("[TIP] Chay backend de tu dong tao bang: uvicorn main:app --reload")
    else:
        print(f"[INFO] Tim thay {len(tables)} bang:")
        print("-" * 50)
        
        # Tao session de dem du lieu
        Session = sessionmaker(bind=engine)
        session = Session()
        
        total_records = 0
        for table_name in tables:
            try:
                # Dem so dong trong moi bang (dung text() cho SQLAlchemy 2.0)
                result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                total_records += count
                
                status = "[DATA]" if count > 0 else "[EMPTY]"
                print(f"{status} {table_name:30s} : {count:4d} dong")
            except Exception as e:
                print(f"[ERROR] {table_name:30s} : Loi - {str(e)}")
        
        session.close()
        
        print("-" * 50)
        if total_records > 0:
            print(f"[OK] Tong cong: {total_records} ban ghi trong database")
        else:
            print("[INFO] Database trong, chua co du lieu")
            print("[TIP] Dang ky user moi hoac tao recipe de co du lieu")
    
except Exception as e:
    print(f"[ERROR] Loi ket noi database: {str(e)}")
    print("\n[TIP] Kiem tra:")
    print("   1. PostgreSQL dang chay chua?")
    print("   2. Password trong .env dung chua?")
    print("   3. User meal_user da duoc tao chua?")

