"""
Script kiểm tra Gemini API key và tìm key còn requests
Chạy: python test_ai.py
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Danh sách API keys để test
API_KEYS = [
    "AIzaSyBlN21NOLGdiVoWqK0g0ggBpQfmV5trKoE",  # Key mới nhất
    "AIzaSyDbVPDJ5ZIdiUEKiO958iZcJncSPetWCP8",  # Key 2
    os.getenv("GEMINI_API_KEY"),  # Key cũ
]

def test_api_key(api_key, index):
    """Test một API key"""
    if not api_key:
        return False, "Key trống"
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Test với prompt đơn giản
        response = model.generate_content("Say hello in 3 words")
        
        # Nếu không lỗi = key còn quota
        print(f"✅ KEY {index}: HOẠT ĐỘNG TỐT")
        print(f"   Key: {api_key[:20]}...")
        print(f"   Response: {response.text[:50]}")
        return True, response.text
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            print(f"❌ KEY {index}: HẾT QUOTA")
            print(f"   Key: {api_key[:20]}...")
            print(f"   Lỗi: Đã vượt giới hạn requests")
        elif "401" in error_msg or "invalid" in error_msg.lower():
            print(f"❌ KEY {index}: KHÔNG HỢP LỆ")
            print(f"   Key: {api_key[:20]}...")
        else:
            print(f"❌ KEY {index}: LỖI KHÁC")
            print(f"   Key: {api_key[:20]}...")
            print(f"   Lỗi: {error_msg[:100]}")
        return False, error_msg

def list_available_models():
    """Liệt kê các models có thể dùng"""
    try:
        api_key = API_KEYS[0]
        if not api_key:
            print("⚠️  Không có API key để kiểm tra models")
            return
        
        genai.configure(api_key=api_key)
        print("\n📋 DANH SÁCH MODELS KHẢ DỤNG:")
        print("-" * 50)
        
        count = 0
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"   • {m.name}")
                count += 1
                if count >= 10:  # Chỉ hiện 10 models đầu
                    break
        
        print(f"\n   Tổng: {count} models")
        
    except Exception as e:
        print(f"⚠️  Không thể list models: {e}")

def main():
    import time
    
    print("=" * 60)
    print("🔍 KIỂM TRA GEMINI API KEYS")
    print("=" * 60)
    
    working_keys = []
    
    for i, key in enumerate(API_KEYS, 1):
        if key:
            success, result = test_api_key(key, i)
            if success:
                working_keys.append(key)
            print()
            time.sleep(0.5)  # Đợi giữa các requests
    
    print("=" * 60)
    print("📊 KẾT QUẢ:")
    print(f"   Tổng keys test: {len([k for k in API_KEYS if k])}")
    print(f"   ✅ Keys hoạt động: {len(working_keys)}")
    print(f"   ❌ Keys hết quota/lỗi: {len([k for k in API_KEYS if k]) - len(working_keys)}")
    print("=" * 60)
    
    if working_keys:
        print("\n✨ KEY TỐT NHẤT ĐỂ DÙNG:")
        print(f"   {working_keys[0][:30]}...")
        print("\n💡 Thêm vào .env:")
        print(f"   GEMINI_API_KEY={working_keys[0]}")
    else:
        print("\n⚠️  KHÔNG CÓ KEY NÀO HOẠT ĐỘNG!")
        print("\n📝 HƯỚNG DẪN LẤY KEY MỚI:")
        print("   1. Vào: https://aistudio.google.com/apikey")
        print("   2. Đăng nhập Google")
        print("   3. Nhấn 'Create API Key'")
        print("   4. Copy key và thêm vào test_ai.py")
        print("\n📊 GIỚI HẠN FREE TIER:")
        print("   • 15 requests/phút")
        print("   • 1,500 requests/ngày")
        print("   • Reset sau 1 phút nếu vượt quota")
    
    # List models
    if API_KEYS[0]:
        list_available_models()

if __name__ == "__main__":
    main()
