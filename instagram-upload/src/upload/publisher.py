"""
Publisher for Instagram video posts.

Handles the final sharing/publishing of video posts to Instagram,
including confirmation and error handling.

Created by: Sam Lead Developer (Main Developer)
Date: 2026-04-08
"""

import asyncio
import os
import time
import re
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from dotenv import load_dotenv

# Load Instagram configuration
load_dotenv('.env.instagram')


class PublishError(Exception):
    """Base error for publish operations."""
    pass


class ShareButtonNotFoundError(PublishError):
    """Error when share button not found."""
    pass


class PublishTimeoutError(PublishError):
    """Error when publish times out."""
    pass


class PublicationStatus(Enum):
    """Status of publication operation."""
    PENDING = "pending"
    SHARING = "sharing"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"


@dataclass
class PublicationResult:
    """Result of publication operation."""
    success: bool
    status: PublicationStatus
    message: str = ""
    post_url: Optional[str] = None
    post_id: Optional[str] = None
    published_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    duration_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class Publisher:
    """Handles final publication of Instagram posts."""

    def __init__(self, browser_service=None):
        """Initialize publisher.

        Args:
            browser_service: BrowserService instance.
                Required for actual publishing.
        """
        self.browser_service = browser_service
        self._publish_timeout = int(os.getenv('INSTAGRAM_PUBLISH_TIMEOUT', '120'))  # 2 minutes
        self._dry_run = os.getenv('INSTAGRAM_DRY_RUN', 'false').lower() == 'true'

    async def click_share_button(self) -> bool:
        """Click share button to publish post.

        Returns:
            bool: True if share button clicked successfully
        """
        print("📤 Clicking Share button...")

        if not self.browser_service:
            raise PublishError("BrowserService required for publishing")

        try:
            # Find share button
            share_button_selectors = [
                'div[role="button"]:has-text("Share")',
                'button:has-text("Share")',
                'div:has-text("Share")'
            ]

            share_button = None
            for selector in share_button_selectors:
                if await self.browser_service.wait_for_element(selector, timeout=15000):
                    share_button = selector
                    break

            if not share_button:
                print("❌ Share button not found")
                await self.browser_service.take_screenshot("share_button_missing")
                return False

            # In dry run mode, just log without clicking
            if self._dry_run:
                print("🔸 DRY RUN: Would click Share button (simulation)")
                return True

            # Click share button
            await self.browser_service.click_like_human(share_button)
            print("✅ Share button clicked")
            return True

        except Exception as e:
            print(f"❌ Error clicking share button: {e}")
            await self.browser_service.take_screenshot("share_button_error")
            return False

    async def wait_for_publication(self, timeout: int = None) -> Tuple[bool, str]:
        """Wait for publication to complete.

        Args:
            timeout: Timeout in seconds (default from config)

        Returns:
            Tuple of (success, message)
        """
        if timeout is None:
            timeout = self._publish_timeout

        print(f"⏳ Waiting for publication (timeout: {timeout}s)...")

        if not self.browser_service:
            raise PublishError("BrowserService required")

        start_time = time.time()

        try:
            # Look for success indicators
            success_indicators = [
                'div:has-text("Your post has been shared")',
                'div:has-text("Post shared")',
                'div:has-text("shared")',
                'svg[aria-label="Your post has been shared"]',
                # Sometimes Instagram shows a checkmark
                'svg[aria-label="Checkmark"]:has-text("Your post has been shared")',
                # Post published confirmation
                'div[role="dialog"]:has-text("Your post has been shared")'
            ]

            # Also look for error indicators
            error_indicators = [
                'div[role="alert"]',
                'div:has-text("error")',
                'div:has-text("failed")',
                'div:has-text("try again")',
                'div:has-text("Something went wrong")'
            ]

            while time.time() - start_time < timeout:
                # Check for success
                for indicator in success_indicators:
                    if await self.browser_service.is_element_visible(indicator, timeout=2000):
                        message = await self._get_publication_message()
                        print(f"✅ Publication successful: {message}")
                        return True, message

                # Check for errors
                for indicator in error_indicators:
                    if await self.browser_service.is_element_visible(indicator, timeout=2000):
                        error_text = await self.browser_service.get_element_text(indicator)
                        print(f"❌ Publication error: {error_text}")
                        await self.browser_service.take_screenshot("publication_error")
                        return False, error_text or "Unknown error"

                # Check if we're back to home page (another success indicator)
                try:
                    await self.browser_service.page.wait_for_selector(
                        'svg[aria-label="Home"]',
                        timeout=2000
                    )
                    print("✅ Back to home page - publication likely successful")
                    return True, "Returned to home page"
                except:
                    pass

                # Small delay before checking again
                await asyncio.sleep(2)
                elapsed = int(time.time() - start_time)
                if elapsed % 10 == 0:  # Log every 10 seconds
                    print(f"   Still publishing... ({elapsed}s)")

            # Timeout
            print(f"❌ Publication timeout after {timeout}s")
            await self.browser_service.take_screenshot("publication_timeout")
            return False, f"Publication timed out after {timeout}s"

        except Exception as e:
            print(f"❌ Error waiting for publication: {e}")
            await self.browser_service.take_screenshot("publication_wait_error")
            return False, f"Error: {str(e)}"

    async def _get_publication_message(self) -> str:
        """Get publication success message.

        Returns:
            Success message or default
        """
        if not self.browser_service:
            return "Publication completed"

        try:
            # Try to get success message text
            message_selectors = [
                'div:has-text("Your post has been shared")',
                'div[role="dialog"] div',
                'div[role="alert"]:has-text("shared")'
            ]

            for selector in message_selectors:
                text = await self.browser_service.get_element_text(selector)
                if text and "shared" in text.lower():
                    return text.strip()

        except:
            pass

        return "Publication completed successfully"

    async def get_post_url(self) -> Optional[str]:
        """Try to get URL of published post.

        Returns:
            Post URL if found, None otherwise
        """
        if not self.browser_service:
            return None

        try:
            # Wait a bit for any post confirmation dialog
            await asyncio.sleep(3)

            # Try to find "View post" or similar link
            view_post_selectors = [
                'a:has-text("View post")',
                'div[role="link"]:has-text("View post")',
                'button:has-text("View post")',
                'a[href*="/p/"]',
                'a[href*="/reel/"]'
            ]

            for selector in view_post_selectors:
                if await self.browser_service.is_element_visible(selector, timeout=3000):
                    # Get href attribute
                    href = await self.browser_service.page.evaluate(
                        f"(selector) => document.querySelector(selector)?.href",
                        selector
                    )

                    if href:
                        print(f"🔗 Post URL found: {href}")
                        return href

            # Check current URL (might be on post page)
            current_url = self.browser_service.page.url
            if "/p/" in current_url or "/reel/" in current_url:
                print(f"🔗 Currently on post page: {current_url}")
                return current_url

            # Try to extract from page content
            page_content = await self.browser_service.page.content()
            url_patterns = [
                r'https://www\.instagram\.com/p/[a-zA-Z0-9_-]+/?',
                r'https://www\.instagram\.com/reel/[a-zA-Z0-9_-]+/?'
            ]

            for pattern in url_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    print(f"🔗 Post URL extracted: {matches[0]}")
                    return matches[0]

        except Exception as e:
            print(f"⚠️  Could not get post URL: {e}")

        return None

    async def extract_post_id(self, post_url: Optional[str] = None) -> Optional[str]:
        """Extract post ID from URL.

        Args:
            post_url: Post URL (if None, tries to get from page)

        Returns:
            Post ID if found, None otherwise
        """
        if not post_url:
            post_url = await self.get_post_url()

        if not post_url:
            return None

        try:
            # Extract post ID from URL patterns
            patterns = [
                r'/p/([a-zA-Z0-9_-]+)',
                r'/reel/([a-zA-Z0-9_-]+)'
            ]

            for pattern in patterns:
                match = re.search(pattern, post_url)
                if match:
                    post_id = match.group(1)
                    print(f"🆔 Post ID extracted: {post_id}")
                    return post_id

        except Exception as e:
            print(f"⚠️  Could not extract post ID: {e}")

        return None

    async def publish_post(self) -> PublicationResult:
        """Publish the post.

        Returns:
            PublicationResult with publication status
        """
        start_time = time.time()
        result = PublicationResult(
            success=False,
            status=PublicationStatus.PENDING,
            message="Starting publication process"
        )

        print("\n🚀 Publishing post to Instagram...")

        # In dry run mode, simulate success
        if self._dry_run:
            result.status = PublicationStatus.PUBLISHED
            result.success = True
            result.message = "DRY RUN: Post would be published"
            result.duration_seconds = time.time() - start_time
            print("🔸 DRY RUN: Publication simulated successfully")
            return result

        # Click share button
        result.status = PublicationStatus.SHARING
        if not await self.click_share_button():
            result.status = PublicationStatus.FAILED
            result.message = "Failed to click share button"
            result.duration_seconds = time.time() - start_time
            print(f"❌ {result.message}")
            return result

        # Wait for publication
        result.status = PublicationStatus.PROCESSING
        success, message = await self.wait_for_publication()

        if success:
            result.status = PublicationStatus.PUBLISHED
            result.success = True
            result.message = message
            result.published_at = datetime.now()

            # Try to get post URL and ID
            result.post_url = await self.get_post_url()
            result.post_id = await self.extract_post_id(result.post_url)

            print("🎉 Post published successfully!")
        else:
            result.status = PublicationStatus.FAILED
            result.success = False
            result.message = message
            print(f"❌ Publication failed: {message}")

        result.duration_seconds = time.time() - start_time
        print(f"⏱️  Publication duration: {result.duration_seconds:.1f}s")

        return result

    async def schedule_post(self, schedule_time: datetime) -> PublicationResult:
        """Schedule post for future publication.

        Args:
            schedule_time: When to publish the post

        Returns:
            PublicationResult with scheduling status
        """
        print(f"📅 Scheduling post for {schedule_time}...")

        # In dry run mode, simulate success
        if self._dry_run:
            start_time = time.time()
            result = PublicationResult(
                success=True,
                status=PublicationStatus.SCHEDULED,
                message=f"DRY RUN: Post would be scheduled for {schedule_time}",
                scheduled_for=schedule_time,
                duration_seconds=time.time() - start_time
            )
            print("🔸 DRY RUN: Scheduling simulated successfully")
            return result

        if not self.browser_service:
            raise PublishError("BrowserService required for scheduling")

        result = PublicationResult(
            success=False,
            status=PublicationStatus.PENDING,
            message=f"Starting scheduling for {schedule_time}"
        )

        try:
            # First need to find schedule option
            schedule_selectors = [
                'div:has-text("Schedule")',
                'button:has-text("Schedule")',
                'div[role="button"]:has-text("Schedule")'
            ]

            schedule_button = None
            for selector in schedule_selectors:
                if await self.browser_service.wait_for_element(selector, timeout=10000):
                    schedule_button = selector
                    break

            if not schedule_button:
                result.status = PublicationStatus.FAILED
                result.message = "Schedule option not found"
                print(f"❌ {result.message}")
                return result

            # Click schedule button
            await self.browser_service.click_like_human(schedule_button)
            await asyncio.sleep(2)

            # Now would need to set date/time
            # This is complex and Instagram's UI may vary
            # For now, we'll simulate scheduling

            if self._dry_run:
                result.status = PublicationStatus.SCHEDULED
                result.success = True
                result.message = f"DRY RUN: Post would be scheduled for {schedule_time}"
                result.scheduled_for = schedule_time
                print(f"🔸 {result.message}")
            else:
                # In real mode, would need to implement date/time picker interaction
                result.status = PublicationStatus.FAILED
                result.message = "Scheduling not fully implemented (UI complexity)"
                print(f"⚠️  {result.message}")

        except Exception as e:
            result.status = PublicationStatus.FAILED
            result.message = f"Scheduling error: {str(e)}"
            print(f"❌ {result.message}")

        return result

    async def close_post_dialog(self) -> bool:
        """Close any post-publication dialog.

        Returns:
            bool: True if dialog closed successfully
        """
        print("🗑️  Closing post dialog...")

        if not self.browser_service:
            return False

        try:
            # Try different close methods
            close_selectors = [
                'svg[aria-label="Close"]',
                'button[aria-label="Close"]',
                'div[role="button"][aria-label="Close"]',
                'div[aria-label="Close"]'
            ]

            for selector in close_selectors:
                if await self.browser_service.is_element_visible(selector, timeout=3000):
                    await self.browser_service.click_like_human(selector)
                    await asyncio.sleep(1)
                    print("✅ Post dialog closed")
                    return True

            # Try pressing Escape
            await self.browser_service.page.keyboard.press('Escape')
            await asyncio.sleep(1)

            # Check if we're back to normal
            try:
                await self.browser_service.page.wait_for_selector(
                    'svg[aria-label="Home"]',
                    timeout=2000
                )
                print("✅ Back to home page")
                return True
            except:
                pass

            print("⚠️  Could not close post dialog (may have auto-closed)")
            return True  # Consider success anyway

        except Exception as e:
            print(f"⚠️  Error closing dialog: {e}")
            return False


# Complete publication flow
async def complete_publication_flow(browser_service, metadata=None) -> PublicationResult:
    """Complete publication flow from share screen to confirmation.

    Args:
        browser_service: BrowserService instance
        metadata: Optional metadata for scheduling

    Returns:
        PublicationResult with final status
    """
    publisher = Publisher(browser_service)

    try:
        # Check if we need to schedule
        if metadata and metadata.schedule_time:
            # Parse schedule time
            from datetime import datetime
            schedule_time = datetime.fromisoformat(metadata.schedule_time)
            return await publisher.schedule_post(schedule_time)
        else:
            # Publish immediately
            return await publisher.publish_post()

    except Exception as e:
        return PublicationResult(
            success=False,
            status=PublicationStatus.FAILED,
            message=f"Publication error: {str(e)}",
            errors=[str(e)]
        )


# Example usage
async def example_usage():
    """Example usage of Publisher."""
    print("Publisher Example Usage")
    print("======================")

    # Create publisher (no browser service for example)
    publisher = Publisher()

    print("\n1. Dry Run Simulation:")
    publisher._dry_run = True
    result = await publisher.publish_post()

    print(f"   Success: {'✅' if result.success else '❌'}")
    print(f"   Status: {result.status.value}")
    print(f"   Message: {result.message}")
    print(f"   Duration: {result.duration_seconds:.1f}s")

    print("\n2. URL Extraction Example:")
    test_url = "https://www.instagram.com/p/ABC123DEF456/"
    post_id = await publisher.extract_post_id(test_url)
    print(f"   Test URL: {test_url}")
    print(f"   Extracted ID: {post_id}")

    print("\n🎉 Example completed")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())