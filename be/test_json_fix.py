"""
Test script để kiểm tra JSON fixing functions
"""
import json
import re

def _fix_json_at_position(text: str, error_pos: int) -> str:
    """
    Cố gắng sửa lỗi JSON tại vị trí cụ thể
    """
    print(f"[FIX] Trying to fix JSON at position {error_pos}")
    
    if error_pos < len(text):
        char_at_error = text[error_pos]
        prev_char = text[error_pos - 1] if error_pos > 0 else ''
        
        print(f"[FIX] Char at error: '{char_at_error}', Prev char: '{prev_char}'")
        
        # Nếu ký tự hiện tại là " và trước đó là } hoặc ] hoặc số
        if char_at_error == '"' and prev_char in ['}', ']', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            text = text[:error_pos] + ',' + text[error_pos:]
            print(f"[FIX] Added comma before quote")
            return text
        
        # Nếu ký tự hiện tại là { và trước đó là }
        if char_at_error == '{' and prev_char == '}':
            text = text[:error_pos] + ',' + text[error_pos:]
            print(f"[FIX] Added comma between }} and {{")
            return text
    
    return text

def _clean_json_text(text: str) -> str:
    """
    Làm sạch JSON text để tránh lỗi parsing
    """
    # Loại bỏ BOM
    if text.startswith('\ufeff'):
        text = text[1:]
    
    # Loại bỏ comments
    text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    
    # Loại bỏ trailing commas
    text = re.sub(r',(\s*[}\]])', r'\1', text)
    
    # Sửa thiếu dấu phẩy
    text = re.sub(r'"\s*\n\s*"', '",\n"', text)
    text = re.sub(r'}\s*\n\s*{', '},\n{', text)
    text = re.sub(r']\s*\n\s*\[', '],\n[', text)
    text = re.sub(r'}\s*{', '},{', text)
    text = re.sub(r'}\s*\[', '},[', text)
    text = re.sub(r']\s*{', '],{', text)
    
    # Sửa lỗi với key-value
    text = re.sub(r'(\d|true|false|null)\s+(")', r'\1,\2', text)
    text = re.sub(r'(})\s+(")', r'\1,\2', text)
    text = re.sub(r'(])\s+(")', r'\1,\2', text)
    
    return text

# Test cases
test_cases = [
    # Case 1: Missing comma after number before string
    '{"name": "Test", "value": 123 "next": "value"}',
    
    # Case 2: Missing comma after } before {
    '{"a": {"x": 1}{"b": 2}}',
    
    # Case 3: Realistic case - missing comma after object
    '{"items": [{"name": "A", "value": 1}{"name": "B", "value": 2}]}',
]

print("Testing JSON cleaning and fixing functions...\n")

for i, test_json in enumerate(test_cases, 1):
    print(f"Test Case {i}:")
    print(f"Original: {test_json}")
    
    cleaned = _clean_json_text(test_json)
    print(f"Cleaned:  {cleaned}")
    
    try:
        parsed = json.loads(cleaned)
        print(f"✅ Success after clean! Parsed: {parsed}")
    except json.JSONDecodeError as e:
        print(f"❌ Failed after clean: {str(e)} at position {e.pos}")
        
        # Try fix at position
        fixed = _fix_json_at_position(cleaned, e.pos)
        print(f"Fixed:    {fixed}")
        
        try:
            parsed = json.loads(fixed)
            print(f"✅ Success after fix! Parsed: {parsed}")
        except json.JSONDecodeError as e2:
            print(f"❌ Still failed: {str(e2)}")
    
    print()
