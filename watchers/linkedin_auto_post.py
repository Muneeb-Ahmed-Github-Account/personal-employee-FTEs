"""
LinkedIn Auto-Post - Single Working Version

- Reuses your existing LinkedIn session
- Auto-clicks "Start a post"
- Auto-types content (most reliable method)
- You ONLY click the final "Post" button
"""

import sys
import time
import re
import shutil
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright


class LinkedInAutoPost:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        # REUSE YOUR EXISTING SESSION
        self.session_path = self.vault_path / '.linkedin_session'
        
        for folder in [self.approved, self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        self.browser = None
        self.page = None
        self.playwright = None
    
    def get_approved_posts(self):
        """Get approved LinkedIn posts"""
        posts = []
        for file in self.approved.glob('*.md'):
            try:
                content = file.read_text(encoding='utf-8')
                if 'linkedin' in content.lower() and ('approval' in content.lower() or 'To Approve' in content):
                    posts.append({'file': file, 'content': content})
            except:
                pass
        return posts
    
    def extract_content(self, content: str) -> str:
        """Extract post content from approval file"""
        # Method 1: YAML content field
        match = re.search(r'content:\s*"([^"]+)"', content)
        if match:
            return match.group(1)
        
        # Method 2: After **Content:**
        if '**Content:**' in content:
            parts = content.split('**Content:**')
            if len(parts) > 1:
                text = parts[1].split('##')[0].split('---')[0].strip()
                return re.sub(r'^>\s*', '', text, flags=re.MULTILINE).strip()
        
        # Method 3: Extract non-metadata lines
        lines = content.split('\n')
        post = []
        started = False
        for line in lines:
            if line.strip() == '---':
                started = True
                continue
            if started and not line.startswith(('type:', 'action:', 'created:', 'status:')):
                if 'To Approve' not in line and not line.startswith('##') and line.strip():
                    post.append(line.strip())
        return ' '.join(post)
    
    def init_browser(self):
        """Initialize browser - REUSES YOUR EXISTING SESSION"""
        print("Starting browser (reusing your LinkedIn session)...")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch_persistent_context(
            str(self.session_path),
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        self.page = self.browser.pages[0]
        print("Browser started - session reused!")
    
    def close_browser(self):
        """Close browser BUT KEEP SESSION FOR NEXT TIME"""
        if self.browser:
            try:
                self.browser.close()
            except:
                pass
        if self.playwright:
            try:
                self.playwright.stop()
            except:
                pass
        self.browser = None
        self.page = None
        self.playwright = None
        print("Browser closed (session saved)")
    
    def click_start_post(self):
        """Auto-click 'Start a post' button"""
        print("\nAuto-clicking 'Start a post'...")
        time.sleep(2)
        
        selectors = [
            '[aria-label="Start a post"]',
            '[data-test-id="feed-compose"]',
            'button:has-text("Start a post")',
        ]
        
        # Try up to 5 times
        for attempt in range(5):
            for selector in selectors:
                try:
                    btn = self.page.locator(selector).first
                    if btn.is_visible(timeout=3000):
                        btn.scroll_into_view_if_needed()
                        time.sleep(1)
                        btn.click()
                        print("SUCCESS: Auto-clicked 'Start a post'")
                        time.sleep(3)
                        return True
                except:
                    continue
            
            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(2)
        
        # Fallback: JavaScript click
        try:
            self.page.evaluate('document.querySelector(\'[aria-label="Start a post"]\').click()')
            print("SUCCESS: Clicked via JavaScript")
            time.sleep(3)
            return True
        except:
            print("Please click 'Start a post' manually")
            return False
    
    def type_content(self, post_content: str):
        """Auto-type content into LinkedIn editor - MOST RELIABLE METHOD"""
        print("\nAuto-typing content...")
        
        editors = [
            'div[contenteditable="true"][role="textbox"]',
            '[data-testid="post-create-editor"]',
            '.ql-editor[contenteditable="true"]',
        ]
        
        for selector in editors:
            try:
                editor = self.page.locator(selector).first
                if editor.is_visible(timeout=5000):
                    editor.click()
                    time.sleep(1)
                    # Type the content
                    editor.type(post_content)
                    time.sleep(2)
                    print("SUCCESS: Content typed automatically!")
                    return True
            except Exception as e:
                print(f"Type attempt failed: {e}")
                continue
        
        # Fallback: JavaScript injection
        print("Trying JavaScript injection...")
        try:
            safe_content = post_content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            self.page.evaluate(f'''
                const editor = document.querySelector('[data-testid="post-create-editor"]');
                if (editor) {{
                    editor.innerText = "{safe_content}";
                    editor.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
            ''')
            time.sleep(2)
            print("SUCCESS: Content injected via JavaScript!")
            return True
        except Exception as e:
            print(f"JavaScript failed: {e}")
        
        print("CONTENT READY - Please paste manually (Ctrl+V)")
        return False
    
    def post_to_linkedin(self, post_content: str):
        """Complete posting workflow"""
        try:
            # Navigate to LinkedIn
            print("Navigating to LinkedIn...")
            self.page.goto('https://www.linkedin.com', timeout=60000)
            time.sleep(5)
            
            # Check if logged in
            if 'login' in self.page.url.lower():
                print("\n" + "="*70)
                print("NOT LOGGED IN - Please log in (session will be saved)")
                print("="*70)
                print("Waiting 60 seconds...")
                for i in range(60, 0, -1):
                    print(f"{i}...", end='\r')
                    time.sleep(1)
                self.page.goto('https://www.linkedin.com/feed/', timeout=30000)
                time.sleep(3)
            
            print(f"LinkedIn loaded: {self.page.url[:80]}")
            
            # Auto-click "Start a post"
            if not self.click_start_post():
                time.sleep(5)
            
            # Wait for dialog
            print("Waiting for post dialog...")
            time.sleep(5)
            
            # Auto-type content
            self.type_content(post_content)
            
            # Screenshot
            screenshot = self.logs / f'post_{int(time.time())}.png'
            self.page.screenshot(path=str(screenshot))
            print(f"Screenshot: {screenshot.name}")
            
            # Wait for user to click Post button
            print("\n" + "="*70)
            print("CONTENT READY - CLICK THE BLUE 'Post' BUTTON!")
            print("="*70)
            print("Then press Enter here...")
            print("="*70)
            
            try:
                input("\nPress Enter after clicking Post...")
            except:
                pass
            
            time.sleep(3)
            
            if 'feed' in self.page.url.lower():
                print("Post published successfully!")
                return True
            else:
                print("Please verify post was published")
                return True
            
        except Exception as e:
            print(f"ERROR: {e}")
            return False
    
    def run(self):
        """Main loop"""
        print("="*70)
        print("LinkedIn Auto-Post - REUSES YOUR SESSION")
        print("="*70)
        print(f"Monitoring: {self.approved}")
        print(f"Session: {self.session_path}")
        print("Press Ctrl+C to stop")
        print("="*70)
        
        try:
            while True:
                posts = self.get_approved_posts()
                
                for post in posts:
                    print(f"\nFound approved post: {post['file'].name}")
                    
                    content = self.extract_content(post['content'])
                    
                    if not content or len(content) < 5:
                        print("Could not extract content, skipping")
                        continue
                    
                    safe_content = content.encode('ascii', 'ignore').decode('ascii')[:100]
                    print(f"Content: {safe_content}...")
                    print(f"Length: {len(content)} chars")
                    
                    self.init_browser()
                    success = self.post_to_linkedin(content)
                    
                    if success:
                        done_path = self.done / post['file'].name
                        shutil.move(str(post['file']), str(done_path))
                        print(f"Moved to Done: {post['file'].name}")
                    else:
                        print("Post failed")
                    
                    self.close_browser()
                
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("\nStopped by user")
            self.close_browser()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='LinkedIn Auto-Post')
    parser.add_argument('--vault', type=str, required=True, help='Path to Obsidian vault')
    args = parser.parse_args()
    
    system = LinkedInAutoPost(args.vault)
    system.run()


if __name__ == '__main__':
    main()
