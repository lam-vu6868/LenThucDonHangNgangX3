"""
Test TẤT CẢ models của Gemini để tìm model nào còn quota
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

load_dotenv()

# API Keys
API_KEYS = [
    "AIzaSyBlN21NOLGdiVoWqK0g0ggBpQfmV5trKoE",
    "AIzaSyDbVPDJ5ZIdiUEKiO958iZcJncSPetWCP8",
    os.getenv("GEMINI_API_KEY"),
]

def test_model_with_key(model_name, api_key):
    """Test 1 model với 1 key"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        # Test với prompt siêu ngắn để tiết kiệm quota
        response = model.generate_content("Hi")
        
        return True, response.text[:30]
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return False, "QUOTA"
        elif "404" in error_msg or "not found" in error_msg.lower():
            return False, "NOT_FOUND"
        else:
            return False, f"ERROR: {error_msg[:50]}"

def main():
    print("=" * 70)
    print("🚀 VÉT CẠN TẤT CẢ MODELS VÀ KEYS CỦA GEMINI")
    print("=" * 70)
    
    # Lấy tất cả models
    genai.configure(api_key=API_KEYS[0])
    all_models = []
    
    print("📋 Đang lấy danh sách models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            all_models.append(m.name)
    
    print(f"✅ Tìm thấy {len(all_models)} models\n")
    
    working_combinations = []
    
    # Test từng model với từng key
    for key_idx, api_key in enumerate(API_KEYS, 1):
        if not api_key:
            continue
            
        print(f"\n{'=' * 70}")
        print(f"🔑 KEY {key_idx}: {api_key[:25]}...")
        print(f"{'=' * 70}")
        
        for model_idx, model_name in enumerate(all_models, 1):
            # Chỉ test model name ngắn để dễ nhìn
            short_name = model_name.replace("models/", "")
            
            success, result = test_model_with_key(model_name, api_key)
            
            if success:
                print(f"✅ {model_idx:2d}. {short_name:40s} → HOẠT ĐỘNG!")
                working_combinations.append({
                    "key": api_key,
                    "model": model_name,
                    "response": result
                })
            else:
                status = "❌" if result == "QUOTA" else "⚠️"
                print(f"{status} {model_idx:2d}. {short_name:40s} → {result}")
            
            # Đợi giữa các requests để tránh spam
            time.sleep(0.3)
    
    # Kết quả
    print("\n" + "=" * 70)
    print("📊 KẾT QUẢ CUỐI CÙNG")
    print("=" * 70)
    print(f"Tổng models test: {len(all_models)}")
    print(f"Tổng keys test: {len([k for k in API_KEYS if k])}")
    print(f"✅ Tổ hợp hoạt động: {len(working_combinations)}")
    
    if working_combinations:
        print("\n🎉 TÌM THẤY MODELS CÒN HOẠT ĐỘNG!")
        print("=" * 70)
        for i, combo in enumerate(working_combinations, 1):
            model_name = combo['model'].replace('models/', '')
            key_short = combo['key'][:30]
            print(f"\n{i}. MODEL: {model_name}")
            print(f"   KEY: {key_short}...")
            print(f"   Response test: {combo['response']}")
        
        # Gợi ý model tốt nhất
        best = working_combinations[0]
        print("\n" + "=" * 70)
        print("💡 SỬ DỤNG NGAY:")
        print(f"   Model: {best['model']}")
        print(f"   Key: {best['key']}")
        print("\n📝 Thêm vào .env:")
        print(f"   GEMINI_API_KEY={best['key']}")
        print("\n📝 Update trong ai_service.py:")
        print(f"   model = genai.GenerativeModel('{best['model']}')")
        
    else:
        print("\n❌ TẤT CẢ MODELS ĐỀU HẾT QUOTA HOẶC LỖI!")
        print("\n💡 GỢI Ý:")
        print("   1. Đợi 60 giây rồi chạy lại script này")
        print("   2. Tạo key mới từ tài khoản Google khác")
        print("   3. Nâng cấp lên Paid Plan (không giới hạn)")

if __name__ == "__main__":
    main()
