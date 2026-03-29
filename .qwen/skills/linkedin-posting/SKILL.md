---
name: linkedin-posting
description: |
  LinkedIn automation skill for creating and posting business content. Uses Playwright MCP
  to navigate LinkedIn, compose posts, and publish content for lead generation and business
  growth. Always requires human approval before posting.
---

# LinkedIn Posting Skill

Automate LinkedIn posts for business growth and lead generation.

## Prerequisites

### Playwright MCP

```bash
npm install -g @playwright/mcp
```

### LinkedIn Account

- Business account recommended
- Keep session authenticated
- Company page access (if posting to company)

## Posting Workflow

### 1. Content Creation

Qwen Code creates post content based on:
- Business updates
- Industry news
- Thought leadership
- Product announcements

### 2. Human Approval

Review and approve content before posting.

### 3. Scheduled Publishing

Post at optimal times for engagement.

## Implementation

```python
# linkedin_poster.py
from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime
import time

class LinkedInPoster:
    def __init__(self, session_path: str):
        self.session_path = Path(session_path)
        self.browser = None
        self.page = None
    
    def _init_browser(self):
        """Initialize browser with persistent session"""
        if self.browser is None:
            playwright = sync_playwright().start()
            self.browser = playwright.chromium.launch_persistent_context(
                self.session_path,
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            self.page = self.browser.pages[0]
    
    def create_post(self, content: str, images: list = None) -> dict:
        """Create a LinkedIn post"""
        self._init_browser()
        
        try:
            # Navigate to LinkedIn
            self.page.goto('https://www.linkedin.com', wait_until='networkidle')
            
            # Click on "Start a post"
            self.page.click('[aria-label="Start a post"]', timeout=5000)
            
            # Wait for post dialog
            self.page.wait_for_selector('[data-testid="post-create-editor"]', timeout=10000)
            
            # Type content
            editor = self.page.locator('[data-testid="post-create-editor"]')
            editor.fill(content)
            
            # Add images if provided
            if images:
                self._add_images(images)
            
            # Take screenshot for approval
            screenshot = self.page.screenshot(type='png')
            
            return {
                'success': True,
                'content': content,
                'images': images,
                'screenshot': screenshot,
                'ready_to_post': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def post(self, content: str, images: list = None) -> dict:
        """Publish a LinkedIn post"""
        self._init_browser()
        
        try:
            # Navigate to LinkedIn
            self.page.goto('https://www.linkedin.com', wait_until='networkidle')
            
            # Click on "Start a post"
            self.page.click('[aria-label="Start a post"]', timeout=5000)
            
            # Wait for post dialog
            self.page.wait_for_selector('[data-testid="post-create-editor"]', timeout=10000)
            
            # Type content
            editor = self.page.locator('[data-testid="post-create-editor"]')
            editor.fill(content)
            
            # Add images if provided
            if images:
                self._add_images(images)
            
            # Click Post button
            self.page.click('button:has-text("Post")', timeout=10000)
            
            # Wait for confirmation
            self.page.wait_for_selector('[data-testid="post-create-editor"]', 
                                        state='detached', timeout=10000)
            
            return {
                'success': True,
                'posted_at': datetime.now().isoformat(),
                'content': content
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _add_images(self, images: list):
        """Add images to post"""
        # Click on media button
        self.page.click('[aria-label="Add media"]', timeout=5000)
        
        # Upload images
        file_input = self.page.locator('input[type="file"]')
        for image in images:
            file_input.set_input_files(image)
            time.sleep(1)
    
    def close(self):
        """Close browser"""
        if self.browser:
            self.browser.close()
            self.browser = None
```

## Post Templates

### Business Update

```
🚀 Exciting News!

We're thrilled to announce [announcement].

This is a significant milestone for [company/team] because [reason].

What do you think? Share your thoughts in the comments!

#Business #Innovation #Growth
```

### Thought Leadership

```
💡 Here's what I've learned about [topic]...

[Key insight 1]
[Key insight 2]
[Key insight 3]

The biggest mistake people make is [common mistake].

Instead, try [better approach].

What's your experience with [topic]?

#Leadership #Tips #Professional
```

### Product Announcement

```
🎉 Introducing [Product Name]!

After [time period] of development, we're excited to share:

✨ [Feature 1]
✨ [Feature 2]
✨ [Feature 3]

Early users are saying:
"[Testimonial]"

Ready to try it? [Link]

#Product #Launch #Innovation
```

### Industry Commentary

```
📰 My take on [industry news]...

This development is significant because:

1️⃣ [Point 1]
2️⃣ [Point 2]
3️⃣ [Point 3]

What does this mean for [industry/professionals]?

[Analysis]

Your thoughts?

#Industry #News #Analysis
```

## Approval Workflow

### 1. Qwen Creates Post Draft

```markdown
---
type: approval_request
action: linkedin_post
content_type: business_update
created: 2026-03-02T10:00:00Z
scheduled_for: 2026-03-02T14:00:00Z  # Optimal posting time
---

## LinkedIn Post

**Content:**
🚀 Exciting News!

We're thrilled to announce our new AI Employee Bronze Tier!

This is a significant milestone because it enables businesses to:
✅ Automate file processing
✅ Integrate with Qwen Code
✅ Get real-time updates

What do you think? Share your thoughts in the comments!

#AI #Automation #Business #Innovation

**Image:** /Vault/Media/bronze_tier_announcement.png

## Preview
[Screenshot of post preview]

## To Approve
Move to /Approved folder.

## To Reject
Move to /Rejected folder.
```

### 2. Human Reviews

Check:
- Content accuracy
- Tone and style
- Hashtags
- Images
- Posting time

### 3. Approve and Post

Move file to `Approved/` → Post is published at scheduled time.

## Optimal Posting Times

| Day | Best Times |
|-----|------------|
| Monday | 8-10 AM, 12 PM, 5-6 PM |
| Tuesday | 8-10 AM, 2-4 PM |
| Wednesday | 8-10 AM, 12 PM, 5-6 PM |
| Thursday | 8-10 AM, 12 PM |
| Friday | 8-10 AM, 12-2 PM |
| Saturday | 10 AM-12 PM |
| Sunday | 10 AM-1 PM |

## Content Calendar

```markdown
# Weekly Content Plan

| Day | Type | Topic | Status |
|-----|------|-------|--------|
| Mon | Thought Leadership | Industry trends | Scheduled |
| Tue | Business Update | Project milestone | Draft |
| Wed | Engagement | Question for audience | Posted |
| Thu | Product | Feature highlight | Draft |
| Fri | Culture | Team spotlight | Scheduled |
```

## Usage with Qwen Code

### Create Post Content

```bash
qwen "Create a LinkedIn post about our new Bronze Tier AI Employee. Include relevant hashtags and emojis."
```

### Review and Approve

```bash
qwen "Review the LinkedIn post draft in Pending_Approval. Check for tone, clarity, and engagement."
```

### Post to LinkedIn

```bash
python linkedin_poster.py --session "./linkedin_session" --post "Approved/linkedin_post_*.md"
```

## Best Practices

1. **Post consistently** - 3-5 times per week
2. **Use visuals** - Images get 2x engagement
3. **Ask questions** - Encourage comments
4. **Use hashtags** - 3-5 relevant tags
5. **Engage with comments** - Reply within 24 hours
6. **Optimal length** - 100-200 characters
7. **Post at peak times** - See table above

## Analytics to Track

| Metric | Goal |
|--------|------|
| Impressions | 1,000+ per post |
| Engagement rate | 3%+ |
| Comments | 5+ per post |
| Connection requests | 10+ per week |
| Profile views | 50+ per week |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't login | Re-authenticate LinkedIn session |
| Post fails | Check content length, remove special chars |
| Images not uploading | Verify file format (PNG, JPG) |
| Rate limited | Wait 24 hours before posting |

## Security Notes

- Keep session secure
- Never automate connection requests
- Don't spam or over-post
- Follow LinkedIn Terms of Service

---

*LinkedIn Posting Skill v0.1*
*For Silver Tier AI Employee*
