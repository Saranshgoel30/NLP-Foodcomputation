"""
Quick test for Whisper Speech-to-Text API integration
"""

import requests
import os
from pathlib import Path

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{API_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()

def test_stats():
    """Test stats endpoint (includes Whisper stats)"""
    print("📊 Testing stats endpoint...")
    response = requests.get(f"{API_URL}/api/stats")
    if response.status_code == 200:
        stats = response.json()
        if "whisper" in stats:
            print(f"   ✅ Whisper service detected!")
            print(f"   Model: {stats['whisper']['model']}")
            print(f"   Supported languages: {stats['whisper']['supported_languages']}")
            print(f"   Total transcriptions: {stats['whisper']['total_transcriptions']}")
            print(f"   Total cost: ${stats['whisper']['total_cost_usd']:.4f}")
        else:
            print("   ❌ Whisper not in stats!")
    else:
        print(f"   ❌ Stats failed: {response.status_code}")
    print()

def test_transcribe_with_sample():
    """Test transcription with a sample audio file"""
    print("🎤 Testing transcription endpoint...")
    
    # Check if sample audio exists
    sample_files = [
        "test_audio.webm",
        "test_audio.mp3",
        "test_audio.wav",
        "sample.webm"
    ]
    
    audio_file = None
    for filename in sample_files:
        if Path(filename).exists():
            audio_file = filename
            break
    
    if not audio_file:
        print("   ⚠️  No sample audio file found!")
        print("   Create a test audio file or record one from the browser")
        print("   Supported formats: .webm, .mp3, .wav, .m4a")
        return
    
    print(f"   Using audio file: {audio_file}")
    
    with open(audio_file, 'rb') as f:
        files = {'audio': f}
        response = requests.post(f"{API_URL}/api/transcribe", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Transcription successful!")
        print(f"   Text: '{result['transcription']}'")
        print(f"   Language: {result['detected_language']}")
        print(f"   Duration: {result['duration_minutes']:.2f} minutes")
        print(f"   Cost: ${result['cost_usd']:.6f}")
        print(f"   Processing time: {result['processing_time_seconds']:.2f}s")
        print(f"   Cached: {result['cached']}")
    else:
        print(f"   ❌ Transcription failed: {response.status_code}")
        print(f"   Error: {response.text}")
    print()

def main():
    print("\n" + "="*60)
    print("🎤 WHISPER SPEECH-TO-TEXT API TEST")
    print("="*60 + "\n")
    
    try:
        test_health()
        test_stats()
        test_transcribe_with_sample()
        
        print("✅ Basic tests completed!")
        print("\nTo test with browser recording:")
        print("1. Go to http://localhost:3000")
        print("2. Click the microphone button")
        print("3. Say something like 'I want dal without garlic'")
        print("4. Check the search results!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server!")
        print("   Make sure the server is running: python run_api.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
