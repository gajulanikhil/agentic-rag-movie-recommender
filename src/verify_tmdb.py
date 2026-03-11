"""
Verification script for TMDB integration
"""

import sys
import os
from dotenv import load_dotenv

def verify_tmdb():
    """Verify TMDB setup"""
    
    print("\n" + "="*70)
    print("TMDB INTEGRATION VERIFICATION")
    print("="*70 + "\n")
    
    checks_passed = 0
    total_checks = 5
    
    # Check 1: .env file exists
    print("1️⃣ Checking .env file...")
    if os.path.exists('.env'):
        print("   ✅ .env file found")
        checks_passed += 1
    else:
        print("   ❌ .env file not found")
        print("   Create .env file with: TMDB_API_KEY=your_key")
    
    # Check 2: API key is set
    print("\n2️⃣ Checking API key...")
    load_dotenv()
    api_key = os.getenv('TMDB_API_KEY')
    
    if api_key:
        print(f"   ✅ API key found (starts with: {api_key[:8]}...)")
        checks_passed += 1
    else:
        print("   ❌ TMDB_API_KEY not found in .env")
    
    # Check 3: Import module
    print("\n3️⃣ Importing TMDB module...")
    try:
        from tmdb_integration import TMDBClient
        print("   ✅ Module imported")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Check 4: Initialize client
    print("\n4️⃣ Initializing TMDB client...")
    try:
        client = TMDBClient()
        print("   ✅ Client initialized")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Check 5: Test API call
    print("\n5️⃣ Testing API call...")
    try:
        images = client.get_movie_images("The Matrix", 1999)
        
        if images.get('poster_url'):
            print(f"   ✅ API working")
            print(f"   Poster URL: {images['poster_url'][:50]}...")
            checks_passed += 1
        else:
            print("   ❌ No poster returned")
    except Exception as e:
        print(f"   ❌ API call failed: {e}")
    
    # Summary
    print("\n" + "="*70)
    print(f"RESULTS: {checks_passed}/{total_checks} checks passed")
    print("="*70)
    
    if checks_passed == total_checks:
        print("\n🎉 TMDB integration is fully working!")
        return True
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = verify_tmdb()
    sys.exit(0 if success else 1)