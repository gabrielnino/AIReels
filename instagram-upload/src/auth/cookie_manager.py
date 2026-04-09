"""
Cookie Manager for Instagram automation.

Handles persistent cookie storage and management for Instagram sessions,
including encryption for security and expiration tracking.

Created by: Sam Lead Developer (Main Developer)
Date: 2026-04-08
"""

import json
import os
import base64
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load Instagram configuration
load_dotenv('.env.instagram')


@dataclass
class CookieRecord:
    """Individual cookie record with metadata."""
    name: str
    value: str
    domain: str
    path: str
    expires: Optional[float] = None
    http_only: bool = False
    secure: bool = False
    same_site: Optional[str] = None

    def is_expired(self) -> bool:
        """Check if cookie is expired."""
        if not self.expires:
            return False
        return datetime.now().timestamp() > self.expires

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for browser context."""
        cookie_dict = {
            'name': self.name,
            'value': self.value,
            'domain': self.domain,
            'path': self.path
        }

        if self.expires:
            cookie_dict['expires'] = self.expires

        if self.http_only:
            cookie_dict['httpOnly'] = self.http_only

        if self.secure:
            cookie_dict['secure'] = self.secure

        if self.same_site:
            cookie_dict['sameSite'] = self.same_site

        return cookie_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CookieRecord':
        """Create CookieRecord from dictionary."""
        return cls(
            name=data.get('name', ''),
            value=data.get('value', ''),
            domain=data.get('domain', ''),
            path=data.get('path', '/'),
            expires=data.get('expires'),
            http_only=data.get('httpOnly', False),
            secure=data.get('secure', False),
            same_site=data.get('sameSite')
        )


@dataclass
class SessionInfo:
    """Session information for tracking."""
    username: str
    created_at: datetime
    last_used: datetime
    is_valid: bool = True
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update_usage(self) -> None:
        """Update last used timestamp."""
        self.last_used = datetime.now()

    def mark_invalid(self) -> None:
        """Mark session as invalid."""
        self.is_valid = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat(),
            'is_valid': self.is_valid,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionInfo':
        """Create SessionInfo from dictionary."""
        expires_at = None
        if data.get('expires_at'):
            expires_at = datetime.fromisoformat(data['expires_at'])

        return cls(
            username=data['username'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_used=datetime.fromisoformat(data['last_used']),
            is_valid=data.get('is_valid', True),
            expires_at=expires_at,
            metadata=data.get('metadata', {})
        )


class CookieManager:
    """Manages Instagram session cookies with encryption."""

    def __init__(self):
        """Initialize cookie manager."""
        self.cookies_path = os.getenv('INSTAGRAM_COOKIES_PATH', './data/instagram_cookies.json')
        self.session_path = os.getenv('INSTAGRAM_SESSION_PATH', './data/instagram_session.json')
        self.encryption_key = os.getenv('INSTAGRAM_ENCRYPTION_KEY')
        self.session_timeout = int(os.getenv('INSTAGRAM_SESSION_TIMEOUT', '3600'))

        # Create directories if they don't exist
        Path(self.cookies_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.session_path).parent.mkdir(parents=True, exist_ok=True)

        self._fernet = None
        if self.encryption_key:
            self._setup_encryption()

    def _setup_encryption(self) -> None:
        """Setup Fernet encryption using provided key."""
        try:
            # Ensure key is 32 bytes and URL-safe base64 encoded
            key_bytes = self.encryption_key.encode()
            if len(key_bytes) != 32:
                # Hash to get 32 bytes
                key_hash = hashlib.sha256(key_bytes).digest()
                key_b64 = base64.urlsafe_b64encode(key_hash)
            else:
                key_b64 = base64.urlsafe_b64encode(key_bytes)

            self._fernet = Fernet(key_b64)
        except Exception as e:
            print(f"⚠️  Encryption setup failed: {e}. Cookies will be stored unencrypted.")
            self._fernet = None

    def encrypt_cookies(self, cookies: List[Dict[str, Any]]) -> str:
        """Encrypt cookies for storage."""
        if not self._fernet:
            # Return as JSON string if encryption not available
            return json.dumps(cookies)

        cookies_json = json.dumps(cookies)
        encrypted = self._fernet.encrypt(cookies_json.encode())
        return encrypted.decode()

    def decrypt_cookies(self, encrypted_data: str) -> List[Dict[str, Any]]:
        """Decrypt cookies from storage."""
        if not self._fernet:
            # Assume it's JSON if encryption not available
            try:
                return json.loads(encrypted_data)
            except json.JSONDecodeError:
                return []

        try:
            decrypted = self._fernet.decrypt(encrypted_data.encode())
            return json.loads(decrypted.decode())
        except Exception as e:
            print(f"❌ Cookie decryption failed: {e}")
            return []

    def save_cookies(self, cookies: List[Dict[str, Any]], username: str) -> bool:
        """Save cookies to file with encryption."""
        try:
            # Encrypt cookies
            encrypted_data = self.encrypt_cookies(cookies)

            # Save encrypted cookies
            with open(self.cookies_path, 'w') as f:
                f.write(encrypted_data)

            # Create or update session info
            session_info = self._create_or_update_session(username)

            print(f"💾 Cookies saved for user: {username}")
            print(f"   Location: {self.cookies_path}")
            print(f"   Session expires: {session_info.expires_at}")

            return True

        except Exception as e:
            print(f"❌ Failed to save cookies: {e}")
            return False

    def load_cookies(self) -> Tuple[List[Dict[str, Any]], Optional[SessionInfo]]:
        """Load cookies from file with decryption."""
        if not Path(self.cookies_path).exists():
            print(f"❌ Cookies file not found: {self.cookies_path}")
            return [], None

        try:
            # Read encrypted data
            with open(self.cookies_path, 'r') as f:
                encrypted_data = f.read().strip()

            # Decrypt cookies
            cookies = self.decrypt_cookies(encrypted_data)

            # Load session info
            session_info = self.load_session_info()

            if session_info and not session_info.is_valid:
                print("⚠️  Session marked as invalid")
                return [], session_info

            if session_info and session_info.expires_at and session_info.expires_at < datetime.now():
                print("⚠️  Session expired")
                session_info.mark_invalid()
                self.save_session_info(session_info)
                return [], session_info

            if cookies and session_info:
                session_info.update_usage()
                self.save_session_info(session_info)
                print(f"✅ Cookies loaded for user: {session_info.username}")
                return cookies, session_info

            return cookies, session_info

        except Exception as e:
            print(f"❌ Failed to load cookies: {e}")
            return [], None

    def _create_or_update_session(self, username: str) -> SessionInfo:
        """Create or update session information."""
        session_info = self.load_session_info()

        if session_info and session_info.username == username:
            # Update existing session
            session_info.update_usage()
            session_info.expires_at = datetime.now() + timedelta(seconds=self.session_timeout)
        else:
            # Create new session
            now = datetime.now()
            session_info = SessionInfo(
                username=username,
                created_at=now,
                last_used=now,
                expires_at=now + timedelta(seconds=self.session_timeout)
            )

        self.save_session_info(session_info)
        return session_info

    def save_session_info(self, session_info: SessionInfo) -> bool:
        """Save session information to file."""
        try:
            session_dict = session_info.to_dict()
            with open(self.session_path, 'w') as f:
                json.dump(session_dict, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"❌ Failed to save session info: {e}")
            return False

    def load_session_info(self) -> Optional[SessionInfo]:
        """Load session information from file."""
        if not Path(self.session_path).exists():
            return None

        try:
            with open(self.session_path, 'r') as f:
                session_dict = json.load(f)
            return SessionInfo.from_dict(session_dict)
        except Exception as e:
            print(f"❌ Failed to load session info: {e}")
            return None

    def invalidate_session(self) -> bool:
        """Invalidate current session."""
        session_info = self.load_session_info()
        if session_info:
            session_info.mark_invalid()
            return self.save_session_info(session_info)
        return False

    def has_valid_session(self) -> bool:
        """Check if there's a valid session."""
        session_info = self.load_session_info()

        if not session_info or not session_info.is_valid:
            return False

        if session_info.expires_at and session_info.expires_at < datetime.now():
            session_info.mark_invalid()
            self.save_session_info(session_info)
            return False

        return True

    def get_session_username(self) -> Optional[str]:
        """Get username from current session."""
        session_info = self.load_session_info()
        return session_info.username if session_info else None

    def clear_all(self) -> bool:
        """Clear all cookies and session data."""
        try:
            # Remove cookie file
            if Path(self.cookies_path).exists():
                Path(self.cookies_path).unlink()

            # Remove session file
            if Path(self.session_path).exists():
                Path(self.session_path).unlink()

            print("🧹 All cookies and session data cleared")
            return True

        except Exception as e:
            print(f"❌ Failed to clear data: {e}")
            return False

    def backup_cookies(self, backup_path: Optional[str] = None) -> bool:
        """Create backup of cookies."""
        if not backup_path:
            backup_dir = Path(self.cookies_path).parent / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"cookies_backup_{timestamp}.json"

        try:
            if Path(self.cookies_path).exists():
                import shutil
                shutil.copy2(self.cookies_path, backup_path)
                print(f"📂 Cookies backed up to: {backup_path}")
                return True
            else:
                print("❌ No cookies file to backup")
                return False

        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False


# Utility functions for browser integration
async def save_cookies_from_context(context, username: str, cookies_path: Optional[str] = None) -> bool:
    """Save cookies from Playwright browser context."""
    try:
        cookies = await context.cookies()

        manager = CookieManager()
        if cookies_path:
            manager.cookies_path = cookies_path

        return manager.save_cookies(cookies, username)

    except Exception as e:
        print(f"❌ Failed to save cookies from context: {e}")
        return False


async def load_cookies_to_context(context, cookies_path: Optional[str] = None) -> Tuple[bool, Optional[SessionInfo]]:
    """Load cookies to Playwright browser context."""
    try:
        manager = CookieManager()
        if cookies_path:
            manager.cookies_path = cookies_path

        cookies, session_info = manager.load_cookies()

        if cookies:
            await context.add_cookies(cookies)
            return True, session_info

        return False, session_info

    except Exception as e:
        print(f"❌ Failed to load cookies to context: {e}")
        return False, None


# Example usage
def example_usage():
    """Example usage of CookieManager."""
    print("CookieManager Example Usage")
    print("==========================")

    # Create cookie manager
    manager = CookieManager()

    # Example cookies
    example_cookies = [
        {
            'name': 'sessionid',
            'value': 'example_session_id',
            'domain': '.instagram.com',
            'path': '/',
            'expires': datetime.now().timestamp() + 3600,
            'httpOnly': True,
            'secure': True
        }
    ]

    # Save cookies
    print("\n1. Saving cookies...")
    if manager.save_cookies(example_cookies, "test_user"):
        print("✅ Cookies saved")

    # Load cookies
    print("\n2. Loading cookies...")
    cookies, session_info = manager.load_cookies()
    if cookies and session_info:
        print(f"✅ Cookies loaded for: {session_info.username}")
        print(f"   Session valid: {session_info.is_valid}")
        print(f"   Expires at: {session_info.expires_at}")

    # Check session validity
    print("\n3. Checking session validity...")
    if manager.has_valid_session():
        print("✅ Session is valid")
    else:
        print("❌ Session is invalid or expired")

    # Get username
    print("\n4. Getting session username...")
    username = manager.get_session_username()
    print(f"   Username: {username}")

    # Create backup
    print("\n5. Creating backup...")
    manager.backup_cookies()

    print("\n🎉 Example completed")


if __name__ == "__main__":
    example_usage()