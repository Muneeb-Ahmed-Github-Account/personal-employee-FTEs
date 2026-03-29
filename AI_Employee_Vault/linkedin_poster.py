#!/usr/bin/env python3
"""
LinkedIn Post Creator using Playwright MCP
Navigates to LinkedIn, creates a post, and publishes it.
"""

import asyncio
import json
import websockets
import sys
from datetime import datetime

PLAYWRIGHT_MCP_URL = "ws://localhost:3000"

async def call_mcp(method: str, params: dict = None):
    """Call Playwright MCP method"""
    try:
        async with websockets.connect(PLAYWRIGHT_MCP_URL) as ws:
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params or {}
            }
            await ws.send(json.dumps(request))
            response = await ws.recv()
            return json.loads(response)
    except Exception as e:
        return {"error": str(e)}

async def create_linkedin_post(content: str):
    """Create and publish a LinkedIn post"""
    
    print("=" * 60)
    print("LINKEDIN POST CREATOR")
    print("=" * 60)
    print(f"\nPost Content: \"{content}\"")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # For this implementation, we'll use a simpler approach with subprocess
    # calling npx playwright directly since MCP protocol may vary
    
    print("Note: Using direct Playwright automation...")
    print("\n" + "=" * 60)
    print("INSTRUCTIONS FOR USER")
    print("=" * 60)
    print("""
The LinkedIn post automation requires browser authentication.
Please follow these steps:

1. A browser window will open and navigate to LinkedIn
2. LOG IN to your LinkedIn account if not already logged in
3. Once logged in, the script will attempt to create the post
4. If any CAPTCHA or 2FA appears, please complete it manually
5. The script will wait for your authentication

Post content to be published:
  "{}"

Opening LinkedIn in the browser now...
    """.format(content))

    # Skip interactive prompt for non-interactive environments
    # input("\nPress ENTER to open LinkedIn in the browser...")
    
    # Use Playwright directly via command line
    import subprocess
    
    # Create a Node.js script for Playwright automation
    script_content = f'''
const {{ chromium }} = require('playwright');

(async () => {{
    console.log('Launching browser...');
    const browser = await chromium.launch({{ headless: false }});
    const context = await browser.newContext({{
        viewport: {{ width: 1280, height: 720 }}
    }});
    const page = await context.newPage();
    
    console.log('Navigating to LinkedIn...');
    await page.goto('https://www.linkedin.com/feed', {{ waitUntil: 'networkidle' }});
    
    console.log('Waiting for user authentication...');
    console.log('Please log in to LinkedIn if not already logged in.');
    
    // Wait for user to be logged in - check for post creation box
    await page.waitForSelector('[data-placeholder-text*="Start a post"]', {{ timeout: 300000 }})
        .catch(() => console.log('Timeout waiting for post box'));
    
    console.log('LinkedIn loaded. Looking for post creation area...');
    
    // Try to find and click the post creation button
    const postButton = await page.$('[data-placeholder-text*="Start a post"]');
    if (postButton) {{
        console.log('Found post button, clicking...');
        await postButton.click();
        await page.waitForTimeout(2000);
        
        // Find the textarea and type the content
        const textarea = await page.$('div[contenteditable="true"][role="textbox"]');
        if (textarea) {{
            console.log('Found textarea, typing content...');
            await textarea.fill(`{content}`);
            await page.waitForTimeout(1000);
            
            // Take a screenshot before posting
            await page.screenshot({{ path: 'linkedin_pre_post.png' }});
            console.log('Screenshot saved: linkedin_pre_post.png');
            
            // Find and click the Post button
            const postSubmitButton = await page.$('button:has-text("Post")');
            if (postSubmitButton) {{
                console.log('Found Post button, clicking to publish...');
                await postSubmitButton.click();
                await page.waitForTimeout(3000);
                
                // Take screenshot after posting
                await page.screenshot({{ path: 'linkedin_post_result.png' }});
                console.log('Screenshot saved: linkedin_post_result.png');
                console.log('SUCCESS: Post should be published!');
            }} else {{
                console.log('ERROR: Could not find Post button');
            }}
        }} else {{
            console.log('ERROR: Could not find textarea for post content');
        }}
    }} else {{
        console.log('ERROR: Could not find post creation button');
        console.log('Please ensure you are logged in to LinkedIn');
    }}
    
    console.log('\\nKeeping browser open for 30 seconds for verification...');
    await page.waitForTimeout(30000);
    
    await browser.close();
    console.log('Browser closed.');
}})();
'''
    
    # Write the script to a temp file
    script_path = "C:\\Users\\computer lab\\Documents\\GitHub\\personal-employee-FTEs\\AI_Employee_Vault\\temp_linkedin_script.js"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"\nRunning Playwright automation script...")
    print(f"Script location: {script_path}\n")
    
    # Run the script
    try:
        result = subprocess.run(
            ['node', script_path],
            capture_output=True,
            text=True,
            timeout=360  # 6 minutes timeout
        )
        
        print("\n" + "=" * 60)
        print("AUTOMATION OUTPUT")
        print("=" * 60)
        print(result.stdout)
        
        if result.stderr:
            print("\nErrors/Warnings:")
            print(result.stderr)
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        if "SUCCESS" in result.stdout:
            print("\n[SUCCESS] LinkedIn post was SUCCESSFULLY created!")
            print("\nScreenshots saved:")
            print("  - linkedin_pre_post.png")
            print("  - linkedin_post_result.png")
            return True
        else:
            print("\n[ERROR] LinkedIn post creation encountered issues.")
            print("\nPossible reasons:")
            print("  - Not logged in to LinkedIn")
            print("  - CAPTCHA or 2FA required manual completion")
            print("  - LinkedIn UI changed (selectors may need updating)")
            print("\nPlease check the screenshots and try again if needed.")
            return False

    except subprocess.TimeoutExpired:
        print("\n[ERROR] Automation timed out after 6 minutes")
        print("The script may still be running - check the browser window")
        return False
    except Exception as e:
        print(f"\n[ERROR] Error running automation: {e}")
        return False

if __name__ == "__main__":
    # Read post content from test.md in Needs_Action folder
    import pathlib
    vault_path = pathlib.Path(__file__).parent
    test_file = vault_path / "Needs_Action" / "test.md"

    if test_file.exists():
        post_content = test_file.read_text().strip()
        print(f"Reading post content from: {test_file}")
    else:
        post_content = "Test post from AI Employee"
        print("test.md not found, using default content")
    
    success = asyncio.run(create_linkedin_post(post_content))
    sys.exit(0 if success else 1)
