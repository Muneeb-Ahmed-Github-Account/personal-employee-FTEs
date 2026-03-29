
const { chromium } = require('playwright');

(async () => {
    console.log('Launching browser...');
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext({
        viewport: { width: 1280, height: 720 }
    });
    const page = await context.newPage();
    
    console.log('Navigating to LinkedIn...');
    await page.goto('https://www.linkedin.com/feed', { waitUntil: 'networkidle' });
    
    console.log('Waiting for user authentication...');
    console.log('Please log in to LinkedIn if not already logged in.');
    
    // Wait for user to be logged in - check for post creation box
    await page.waitForSelector('[data-placeholder-text*="Start a post"]', { timeout: 300000 })
        .catch(() => console.log('Timeout waiting for post box'));
    
    console.log('LinkedIn loaded. Looking for post creation area...');
    
    // Try to find and click the post creation button
    const postButton = await page.$('[data-placeholder-text*="Start a post"]');
    if (postButton) {
        console.log('Found post button, clicking...');
        await postButton.click();
        await page.waitForTimeout(2000);
        
        // Find the textarea and type the content
        const textarea = await page.$('div[contenteditable="true"][role="textbox"]');
        if (textarea) {
            console.log('Found textarea, typing content...');
            await textarea.fill(`Test! #AI`);
            await page.waitForTimeout(1000);
            
            // Take a screenshot before posting
            await page.screenshot({ path: 'linkedin_pre_post.png' });
            console.log('Screenshot saved: linkedin_pre_post.png');
            
            // Find and click the Post button
            const postSubmitButton = await page.$('button:has-text("Post")');
            if (postSubmitButton) {
                console.log('Found Post button, clicking to publish...');
                await postSubmitButton.click();
                await page.waitForTimeout(3000);
                
                // Take screenshot after posting
                await page.screenshot({ path: 'linkedin_post_result.png' });
                console.log('Screenshot saved: linkedin_post_result.png');
                console.log('SUCCESS: Post should be published!');
            } else {
                console.log('ERROR: Could not find Post button');
            }
        } else {
            console.log('ERROR: Could not find textarea for post content');
        }
    } else {
        console.log('ERROR: Could not find post creation button');
        console.log('Please ensure you are logged in to LinkedIn');
    }
    
    console.log('\nKeeping browser open for 30 seconds for verification...');
    await page.waitForTimeout(30000);
    
    await browser.close();
    console.log('Browser closed.');
})();
