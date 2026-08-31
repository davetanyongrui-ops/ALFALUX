#!/usr/bin/env python3
"""Generate a Gemini hero image for AlfaLux Travel via browser automation.
Requires Chrome running with remote debugging on port 9222 and signed in.
"""
import asyncio, pathlib, json
from playwright.async_api import async_playwright

CDP_URL = "http://127.0.0.1:9222"
GEMINI_URL = "https://gemini.google.com/app?hl=en"
ASSETS_DIR = pathlib.Path("assets")
ASSETS_DIR.mkdir(exist_ok=True)
SAVE_PATH = ASSETS_DIR / "hero.jpg"
PROMPT = "Generate an image: a sun‑lit, ultra‑modern conference hall with floor‑to‑ceiling glass windows showing the Singapore skyline, sleek white marble flooring, and subtle gold accents – bright, airy, premium corporate feel."

async def get_editor(page):
    for sel in ["div.ql-editor.ql-blank", "div.ql-editor", "div[role='textbox'][contenteditable='true']"]:
        try:
            el = page.locator(sel).first
            await el.wait_for(state="visible", timeout=5000)
            return el
        except Exception:
            continue
    return None

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto(GEMINI_URL, wait_until="domcontentloaded")
        await asyncio.sleep(5)
        editor = await get_editor(page)
        if not editor:
            print("❌ Prompt box not found – ensure Gemini is loaded and you are signed in.")
            return

        await editor.click()
        await editor.fill(PROMPT)
        await page.keyboard.press("Enter")
        # wait for image
        for _ in range(60):  # extend wait up to 5 minutes
            await asyncio.sleep(5)
            ready = await page.evaluate("""() => {
                const imgs = document.querySelectorAll('message-content img');
                return Array.from(imgs).some(i => i.naturalWidth > 250);
            }""")
            if ready:
                break
        # Capture screenshot of the generated image as fallback
        selector = await page.evaluate("""() => {
            const imgs = document.querySelectorAll('message-content img');
            const good = Array.from(imgs).filter(i => i.naturalWidth > 250);
            if (good.length) {
                good[good.length - 1].setAttribute('id', 'tmpImg');
                return '#tmpImg';
            }
            return null;
        }""")
        if selector:
            await page.locator(selector).first.screenshot(path=str(SAVE_PATH))
            print(f"Screenshot saved to {SAVE_PATH}")
        else:
            print('❌ No image element found to capture')

if __name__ == '__main__':
    asyncio.run(main())
