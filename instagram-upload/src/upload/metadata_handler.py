"""
Metadata Handler for Instagram video uploads.

Handles caption, hashtags, location, and other metadata
for Instagram video posts.

Created by: Sam Lead Developer (Main Developer)
Date: 2026-04-08
"""

import asyncio
import os
import re
import random
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from dotenv import load_dotenv

# Load Instagram configuration
load_dotenv('.env.instagram')


class MetadataError(Exception):
    """Base error for metadata operations."""
    pass


class CaptionValidationError(MetadataError):
    """Error when caption validation fails."""
    pass


class HashtagError(MetadataError):
    """Error with hashtags."""
    pass


class MetadataStatus(Enum):
    """Status of metadata entry."""
    PENDING = "pending"
    ENTERING = "entering"
    VALIDATED = "validated"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class VideoMetadata:
    """Metadata for Instagram video post."""
    caption: str = ""
    hashtags: List[str] = field(default_factory=list)
    location: Optional[str] = None
    alt_text: Optional[str] = None
    hide_like_count: bool = False
    disable_comments: bool = False
    schedule_time: Optional[str] = None  # ISO format datetime

    def __post_init__(self):
        """Clean and validate metadata after initialization."""
        # Clean caption
        if self.caption:
            self.caption = self.caption.strip()

        # Clean hashtags
        self.hashtags = [self._clean_hashtag(tag) for tag in self.hashtags]

        # Clean location
        if self.location:
            self.location = self.location.strip()

    def _clean_hashtag(self, hashtag: str) -> str:
        """Clean a single hashtag."""
        hashtag = hashtag.strip()

        # Remove # if already present
        if hashtag.startswith('#'):
            hashtag = hashtag[1:]

        # Remove special characters (Instagram allows letters, numbers, underscore)
        hashtag = re.sub(r'[^\w]', '', hashtag)

        return hashtag

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate metadata.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Validate caption length
        max_caption_length = 2200  # Instagram limit
        if len(self.caption) > max_caption_length:
            errors.append(f"Caption too long: {len(self.caption)}/{max_caption_length} characters")

        # Validate hashtags
        max_hashtags = 30  # Instagram limit
        if len(self.hashtags) > max_hashtags:
            errors.append(f"Too many hashtags: {len(self.hashtags)}/{max_hashtags}")

        # Validate individual hashtags
        for i, tag in enumerate(self.hashtags):
            if not tag:
                errors.append(f"Hashtag {i + 1} is empty")
                continue

            if len(tag) > 50:  # Reasonable limit
                errors.append(f"Hashtag too long: #{tag}")

            if not re.match(r'^[a-zA-Z0-9_]+$', tag):
                errors.append(f"Invalid characters in hashtag: #{tag}")

        # Validate location (if provided)
        if self.location and len(self.location) > 100:
            errors.append(f"Location name too long: {len(self.location)} characters")

        return len(errors) == 0, errors

    def format_caption_with_hashtags(self) -> str:
        """Format caption with hashtags appended.

        Returns:
            Formatted caption string
        """
        caption_parts = []

        # Add caption
        if self.caption:
            caption_parts.append(self.caption)

        # Add hashtags
        if self.hashtags:
            # Add spacing if caption exists
            if self.caption:
                caption_parts.append("")  # Empty line

            hashtags_str = " ".join(f"#{tag}" for tag in self.hashtags)
            caption_parts.append(hashtags_str)

        return "\n".join(caption_parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'caption': self.caption,
            'hashtags': self.hashtags,
            'location': self.location,
            'alt_text': self.alt_text,
            'hide_like_count': self.hide_like_count,
            'disable_comments': self.disable_comments,
            'schedule_time': self.schedule_time,
            'formatted_caption': self.format_caption_with_hashtags()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoMetadata':
        """Create VideoMetadata from dictionary."""
        return cls(
            caption=data.get('caption', ''),
            hashtags=data.get('hashtags', []),
            location=data.get('location'),
            alt_text=data.get('alt_text'),
            hide_like_count=data.get('hide_like_count', False),
            disable_comments=data.get('disable_comments', False),
            schedule_time=data.get('schedule_time')
        )


class MetadataHandler:
    """Handles metadata entry for Instagram videos."""

    def __init__(self, browser_service=None):
        """Initialize metadata handler.

        Args:
            browser_service: BrowserService instance.
                Required for actual metadata entry.
        """
        self.browser_service = browser_service
        self._default_hashtags = self._load_default_hashtags()

    def _load_default_hashtags(self) -> List[str]:
        """Load default hashtags from environment."""
        default_hashtags_str = os.getenv('INSTAGRAM_DEFAULT_HASHTAGS', '')
        if not default_hashtags_str:
            return []

        # Parse hashtags (comma separated, with or without #)
        hashtags = []
        for tag in default_hashtags_str.split(','):
            tag = tag.strip()
            if tag.startswith('#'):
                tag = tag[1:]
            if tag:
                hashtags.append(tag)

        return hashtags

    def enhance_metadata(self, metadata: VideoMetadata, auto_add_hashtags: bool = True) -> VideoMetadata:
        """Enhance metadata with defaults and auto-generation.

        Args:
            metadata: Original metadata
            auto_add_hashtags: Whether to auto-add hashtags

        Returns:
            Enhanced VideoMetadata
        """
        enhanced = VideoMetadata(
            caption=metadata.caption,
            hashtags=metadata.hashtags.copy(),
            location=metadata.location,
            alt_text=metadata.alt_text,
            hide_like_count=metadata.hide_like_count,
            disable_comments=metadata.disable_comments,
            schedule_time=metadata.schedule_time
        )

        # Auto-add default hashtags if enabled
        if auto_add_hashtags and self._default_hashtags:
            # Add default hashtags not already in the list
            for tag in self._default_hashtags:
                if tag not in enhanced.hashtags:
                    enhanced.hashtags.append(tag)

        # Limit to max hashtags (remove from end if necessary)
        max_hashtags = 30
        if len(enhanced.hashtags) > max_hashtags:
            print(f"⚠️  Hashtags limited to {max_hashtags} (had {len(enhanced.hashtags)})")
            enhanced.hashtags = enhanced.hashtags[:max_hashtags]

        return enhanced

    async def enter_caption(self, caption: str) -> bool:
        """Enter caption in Instagram caption field.

        Args:
            caption: Caption text

        Returns:
            bool: True if caption entered successfully
        """
        print("📝 Entering caption...")

        if not self.browser_service:
            raise MetadataError("BrowserService required for caption entry")

        try:
            # Find caption textarea
            caption_selectors = [
                'textarea[aria-label="Write a caption..."]',
                'div[contenteditable="true"][aria-label="Write a caption..."]',
                'textarea[placeholder="Write a caption..."]'
            ]

            caption_field = None
            for selector in caption_selectors:
                if await self.browser_service.wait_for_element(selector, timeout=10000):
                    caption_field = selector
                    break

            if not caption_field:
                print("❌ Caption field not found")
                await self.browser_service.take_screenshot("caption_field_missing")
                return False

            # Type caption with human-like behavior
            await self.browser_service.type_like_human(caption_field, caption)
            print(f"✅ Caption entered ({len(caption)} characters)")
            return True

        except Exception as e:
            print(f"❌ Error entering caption: {e}")
            await self.browser_service.take_screenshot("caption_entry_error")
            return False

    async def add_hashtags(self, hashtags: List[str]) -> bool:
        """Add hashtags to caption.

        Args:
            hashtags: List of hashtags (without #)

        Returns:
            bool: True if hashtags added successfully
        """
        if not hashtags:
            print("ℹ️  No hashtags to add")
            return True

        print(f"🏷️  Adding {len(hashtags)} hashtags...")

        if not self.browser_service:
            raise MetadataError("BrowserService required for hashtag entry")

        try:
            # Find caption field (same as in enter_caption)
            caption_selectors = [
                'textarea[aria-label="Write a caption..."]',
                'div[contenteditable="true"][aria-label="Write a caption..."]',
                'textarea[placeholder="Write a caption..."]'
            ]

            caption_field = None
            for selector in caption_selectors:
                if await self.browser_service.wait_for_element(selector, timeout=5000):
                    caption_field = selector
                    break

            if not caption_field:
                print("❌ Caption field not found for hashtags")
                return False

            # Type hashtags at the end
            hashtags_text = " ".join(f"#{tag}" for tag in hashtags)

            # Click at the end of the caption
            await self.browser_service.page.click(caption_field)
            await asyncio.sleep(0.5)

            # Press End key to go to end of text
            await self.browser_service.page.keyboard.press('End')
            await asyncio.sleep(0.5)

            # Add newline if there's already text
            current_text = await self.browser_service.page.evaluate(
                f"(selector) => document.querySelector(selector).value || document.querySelector(selector).textContent",
                caption_field
            )

            if current_text and current_text.strip():
                await self.browser_service.page.keyboard.press('Enter')
                await asyncio.sleep(0.5)

            # Type hashtags
            await self.browser_service.type_like_human(caption_field, hashtags_text)
            print(f"✅ Hashtags added: {hashtags_text}")
            return True

        except Exception as e:
            print(f"❌ Error adding hashtags: {e}")
            await self.browser_service.take_screenshot("hashtag_entry_error")
            return False

    async def add_location(self, location_name: str) -> bool:
        """Add location to post.

        Args:
            location_name: Location name

        Returns:
            bool: True if location added successfully
        """
        print(f"📍 Adding location: {location_name}")

        if not self.browser_service:
            raise MetadataError("BrowserService required for location entry")

        try:
            # Click "Add location" button
            location_button_selectors = [
                'button:has-text("Add location")',
                'div[role="button"]:has-text("Add location")',
                'div:has-text("Add location")'
            ]

            location_button = None
            for selector in location_button_selectors:
                if await self.browser_service.wait_for_element(selector, timeout=10000):
                    location_button = selector
                    break

            if not location_button:
                print("❌ Add location button not found")
                # Location might be optional, not necessarily an error
                return True  # Return True because location is optional

            # Click location button
            await self.browser_service.click_like_human(location_button)
            await asyncio.sleep(2)

            # Find location search field
            location_search_selectors = [
                'input[placeholder="Search locations"]',
                'input[aria-label="Search locations"]',
                'input[type="text"]:has-text("locations")'
            ]

            search_field = None
            for selector in location_search_selectors:
                if await self.browser_service.wait_for_element(selector, timeout=5000):
                    search_field = selector
                    break

            if not search_field:
                print("❌ Location search field not found")
                await self.browser_service.take_screenshot("location_search_missing")
                return False

            # Type location name
            await self.browser_service.type_like_human(search_field, location_name)
            await asyncio.sleep(2)  # Wait for results

            # Select first result
            first_result_selectors = [
                'div[role="dialog"] div[role="button"]:first-child',
                'div[role="listbox"] div[role="option"]:first-child',
                'div:has-text("' + location_name + '"):first-child'
            ]

            for selector in first_result_selectors:
                if await self.browser_service.is_element_visible(selector, timeout=3000):
                    await self.browser_service.click_like_human(selector)
                    await asyncio.sleep(1)
                    print(f"✅ Location selected: {location_name}")
                    return True

            print("❌ Location not found in search results")
            await self.browser_service.take_screenshot("location_not_found")

            # Close location dialog if not found
            close_button = 'svg[aria-label="Close"], button[aria-label="Close"]'
            if await self.browser_service.is_element_visible(close_button, timeout=2000):
                await self.browser_service.click_like_human(close_button)

            return False  # Location not found

        except Exception as e:
            print(f"❌ Error adding location: {e}")
            await self.browser_service.take_screenshot("location_entry_error")
            return False

    async def configure_advanced_options(self, hide_likes: bool = False,
                                        disable_comments: bool = False) -> bool:
        """Configure advanced options for post.

        Args:
            hide_likes: Whether to hide like count
            disable_comments: Whether to disable comments

        Returns:
            bool: True if options configured successfully
        """
        if not hide_likes and not disable_comments:
            return True  # Nothing to configure

        print("⚙️  Configuring advanced options...")

        if not self.browser_service:
            raise MetadataError("BrowserService required for advanced options")

        try:
            # Find advanced settings button
            advanced_button_selectors = [
                'div:has-text("Advanced settings")',
                'button:has-text("Advanced")',
                'div[role="button"]:has-text("Settings")'
            ]

            advanced_button = None
            for selector in advanced_button_selectors:
                if await self.browser_service.wait_for_element(selector, timeout=5000):
                    advanced_button = selector
                    break

            if not advanced_button:
                print("⚠️  Advanced settings button not found (may not be available)")
                return True  # Advanced settings might not be available

            # Click advanced settings
            await self.browser_service.click_like_human(advanced_button)
            await asyncio.sleep(2)

            # Configure hide likes
            if hide_likes:
                hide_likes_selectors = [
                    'input[type="checkbox"]:has-text("Hide like count")',
                    'div[role="checkbox"]:has-text("Hide like and view counts")',
                    'label:has-text("Hide like") input[type="checkbox"]'
                ]

                for selector in hide_likes_selectors:
                    if await self.browser_service.is_element_visible(selector, timeout=3000):
                        await self.browser_service.click_like_human(selector)
                        print("✅ Hide like count enabled")
                        break

            # Configure disable comments
            if disable_comments:
                disable_comments_selectors = [
                    'input[type="checkbox"]:has-text("Turn off commenting")',
                    'div[role="checkbox"]:has-text("Turn off commenting")',
                    'label:has-text("Turn off commenting") input[type="checkbox"]'
                ]

                for selector in disable_comments_selectors:
                    if await self.browser_service.is_element_visible(selector, timeout=3000):
                        await self.browser_service.click_like_human(selector)
                        print("✅ Comments disabled")
                        break

            # Close advanced settings
            close_button = 'svg[aria-label="Close"], button[aria-label="Close"]'
            if await self.browser_service.is_element_visible(close_button, timeout=2000):
                await self.browser_service.click_like_human(close_button)
            else:
                # Press Escape as fallback
                await self.browser_service.page.keyboard.press('Escape')

            await asyncio.sleep(1)
            return True

        except Exception as e:
            print(f"❌ Error configuring advanced options: {e}")
            await self.browser_service.take_screenshot("advanced_options_error")
            return False

    async def enter_all_metadata(self, metadata: VideoMetadata) -> bool:
        """Enter all metadata for a video post.

        Args:
            metadata: Video metadata

        Returns:
            bool: True if all metadata entered successfully
        """
        print("\n📋 Entering video metadata...")
        print(f"   Caption: {metadata.caption[:50]}..." if len(metadata.caption) > 50 else f"   Caption: {metadata.caption}")
        print(f"   Hashtags: {len(metadata.hashtags)}")
        print(f"   Location: {metadata.location}")

        # Validate metadata first
        is_valid, errors = metadata.validate()
        if not is_valid:
            print(f"❌ Metadata validation failed: {', '.join(errors)}")
            return False

        # Enter caption
        if metadata.caption or metadata.hashtags:
            formatted_caption = metadata.format_caption_with_hashtags()
            if not await self.enter_caption(formatted_caption):
                print("⚠️  Could not enter caption, trying alternative method...")
                # Try entering caption and hashtags separately
                if metadata.caption and not await self.enter_caption(metadata.caption):
                    return False
                if metadata.hashtags and not await self.add_hashtags(metadata.hashtags):
                    return False

        # Add location
        if metadata.location:
            location_success = await self.add_location(metadata.location)
            if not location_success:
                print("⚠️  Could not add location (continuing anyway)")

        # Configure advanced options
        if metadata.hide_like_count or metadata.disable_comments:
            await self.configure_advanced_options(
                hide_likes=metadata.hide_like_count,
                disable_comments=metadata.disable_comments
            )

        print("✅ All metadata entered")
        return True

    async def click_next_to_share(self) -> bool:
        """Click next button to proceed to share screen.

        Returns:
            bool: True if successfully clicked next
        """
        print("➡️  Clicking Next to proceed to share...")

        if not self.browser_service:
            raise MetadataError("BrowserService required")

        try:
            # Find next button
            next_button_selectors = [
                'div[role="button"]:has-text("Next")',
                'button:has-text("Next")',
                'div:has-text("Next")'
            ]

            for selector in next_button_selectors:
                if await self.browser_service.wait_for_element(selector, timeout=10000):
                    await self.browser_service.click_like_human(selector)
                    await asyncio.sleep(2)

                    # Verify we moved to next screen (look for Share button)
                    share_selectors = [
                        'div[role="button"]:has-text("Share")',
                        'button:has-text("Share")'
                    ]

                    for share_selector in share_selectors:
                        if await self.browser_service.wait_for_element(share_selector, timeout=5000):
                            print("✅ Moved to share screen")
                            return True

            print("❌ Could not find or click Next button")
            await self.browser_service.take_screenshot("next_button_error")
            return False

        except Exception as e:
            print(f"❌ Error clicking Next: {e}")
            await self.browser_service.take_screenshot("next_button_exception")
            return False


# Example usage
async def example_usage():
    """Example usage of MetadataHandler."""
    print("MetadataHandler Example Usage")
    print("============================")

    # Create metadata
    metadata = VideoMetadata(
        caption="Beautiful sunset at the beach today! 🌅 The colors were absolutely amazing.",
        hashtags=["sunset", "beach", "nature", "photography", "goldenhour"],
        location="Santa Monica Pier",
        hide_like_count=False,
        disable_comments=False
    )

    print("\n1. Metadata Creation:")
    print(f"   Caption: {metadata.caption}")
    print(f"   Hashtags: {metadata.hashtags}")
    print(f"   Location: {metadata.location}")

    print("\n2. Validation:")
    is_valid, errors = metadata.validate()
    print(f"   Valid: {'✅' if is_valid else '❌'}")
    if errors:
        print(f"   Errors: {', '.join(errors)}")

    print("\n3. Formatted Caption:")
    formatted = metadata.format_caption_with_hashtags()
    print(f"   Length: {len(formatted)} characters")
    print(f"   Preview: {formatted[:100]}...")

    print("\n4. Default Hashtags from Environment:")
    handler = MetadataHandler()
    print(f"   Default hashtags: {handler._default_hashtags}")

    print("\n5. Enhanced Metadata:")
    enhanced = handler.enhance_metadata(metadata, auto_add_hashtags=True)
    print(f"   Hashtags after enhancement: {enhanced.hashtags}")

    print("\n🎉 Example completed (no browser automation in example)")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())