#!/usr/bin/env python3
"""
Simple test script for Instagram login with Playwright.
This version avoids module import issues.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the instagram-upload directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "instagram-upload"))

try:
    from src.auth.login_manager import InstagramLoginManager, main
    print("✅ Module imported successfully")

    # Run the main async function
    print("\n🚀 Starting Instagram Login Test")
    print("==================================")

    success = asyncio.run(main())

    if success:
        print("\n🎉 TEST PASSED!")
        sys.exit(0)
    else:
        print("\n💀 TEST FAILED!")
        sys.exit(1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n📋 Installation needed:")
    print("1. Install Playwright: pip install playwright")
    print("2. Install browsers: playwright install chromium")
    print("3. Try again")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)