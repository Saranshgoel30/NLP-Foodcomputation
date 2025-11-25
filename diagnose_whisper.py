"""
Network Diagnostic Tool for OpenAI API Connectivity
Run this to diagnose connection issues with Whisper API
"""

import socket
import requests
import sys

def check_internet():
    """Check basic internet connectivity"""
    print("1️⃣  Checking internet connectivity...")
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("   ✅ Internet connection: OK")
        return True
    except OSError:
        print("   ❌ No internet connection")
        return False

def check_dns():
    """Check DNS resolution"""
    print("\n2️⃣  Checking DNS resolution...")
    try:
        ip = socket.gethostbyname("api.openai.com")
        print(f"   ✅ DNS resolution: OK (api.openai.com → {ip})")
        return True
    except socket.gaierror as e:
        print(f"   ❌ DNS resolution failed: {e}")
        print("   💡 Try: ipconfig /flushdns (Windows) or restart your router")
        return False

def check_openai_reachable():
    """Check if OpenAI API is reachable"""
    print("\n3️⃣  Checking OpenAI API reachability...")
    try:
        response = requests.get("https://api.openai.com/v1/models", timeout=10)
        print(f"   ✅ OpenAI API reachable (Status: {response.status_code})")
        if response.status_code == 401:
            print("   ℹ️  401 is expected without API key - server is responding")
        return True
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Cannot reach OpenAI API: {e}")
        print("   💡 Check firewall or proxy settings")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ Connection timeout")
        print("   💡 Try: Use a different network or check VPN")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_api_key():
    """Check if API key is set"""
    print("\n4️⃣  Checking API key configuration...")
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("   ❌ OPENAI_API_KEY not found in .env file")
        print("   💡 Add: OPENAI_API_KEY=sk-proj-your-key-here to .env")
        return False
    elif not api_key.startswith("sk-"):
        print(f"   ⚠️  API key format looks incorrect: {api_key[:10]}...")
        print("   💡 OpenAI keys should start with 'sk-'")
        return False
    else:
        print(f"   ✅ API key found: {api_key[:10]}...{api_key[-4:]}")
        return True

def test_whisper_api():
    """Test actual Whisper API call with a tiny audio file"""
    print("\n5️⃣  Testing Whisper API (requires valid API key)...")
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("   ⏭️  Skipped - no API key configured")
        return False
    
    try:
        # Create a minimal audio file (silence)
        import io
        import wave
        
        # Create 1 second of silence
        audio_buffer = io.BytesIO()
        with wave.open(audio_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(b'\x00' * 32000)  # 1 second of silence
        
        audio_buffer.seek(0)
        
        files = {'file': ('test.wav', audio_buffer, 'audio/wav')}
        data = {'model': 'whisper-1'}
        
        response = requests.post(
            'https://api.openai.com/v1/audio/transcriptions',
            headers={'Authorization': f'Bearer {api_key}'},
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("   ✅ Whisper API call successful!")
            result = response.json()
            print(f"   📝 Transcription: '{result.get('text', '')}'")
            return True
        elif response.status_code == 401:
            print(f"   ❌ Invalid API key (401)")
            print("   💡 Check your API key at https://platform.openai.com/api-keys")
            return False
        elif response.status_code == 429:
            print(f"   ❌ Quota exceeded (429)")
            print("   💡 Add credits at https://platform.openai.com/account/billing")
            return False
        else:
            print(f"   ❌ API error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {str(e)}")
        return False

def suggest_fixes():
    """Suggest common fixes"""
    print("\n" + "="*70)
    print("💡 TROUBLESHOOTING SUGGESTIONS")
    print("="*70)
    print("""
If DNS resolution failed:
  Windows: 
    1. Open Command Prompt as Administrator
    2. Run: ipconfig /flushdns
    3. Run: ipconfig /registerdns
    4. Restart your computer
    
  Alternative DNS servers:
    - Google DNS: 8.8.8.8 and 8.8.4.4
    - Cloudflare: 1.1.1.1 and 1.0.0.1
    
If firewall is blocking:
  1. Windows Defender Firewall → Allow an app
  2. Add Python/your terminal to allowed apps
  3. Or temporarily disable firewall for testing
  
If using VPN:
  1. Try disconnecting VPN
  2. Some VPNs block OpenAI API
  3. Try a different VPN server location
  
If on corporate/university network:
  1. Network may block OpenAI API
  2. Try mobile hotspot or home network
  3. Ask IT to whitelist api.openai.com
  
If API key issues:
  1. Get new key: https://platform.openai.com/api-keys
  2. Add credits: https://platform.openai.com/account/billing
  3. Check usage: https://platform.openai.com/usage
""")

def main():
    print("\n" + "="*70)
    print("🔍 WHISPER API CONNECTIVITY DIAGNOSTIC")
    print("="*70 + "\n")
    
    results = {
        "internet": check_internet(),
        "dns": check_dns(),
        "reachable": check_openai_reachable(),
        "api_key": check_api_key(),
    }
    
    if all(results.values()):
        results["whisper"] = test_whisper_api()
    
    print("\n" + "="*70)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*70)
    
    for check, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check.replace('_', ' ').title()}: {'PASS' if status else 'FAIL'}")
    
    if all(results.values()):
        print("\n✅ All checks passed! Whisper should work.")
    else:
        print("\n❌ Some checks failed. See suggestions below.")
        suggest_fixes()
    
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnostic cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
