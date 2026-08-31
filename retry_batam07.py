#!/usr/bin/env python3
"""Retry single Batam image #7."""
import asyncio, pathlib
from playwright.async_api import async_playwright

CDP_URL = "http://127.0.0.1:9222"
GEMINI_URL = "https://gemini.google.com/app?hl=en"
SAVE_PATH = pathlib.Path("assets/batam-07.jpg")

PROMPT = "Generate an image: Nuvasa Bay luxury resort, Batam — infinity pool overlooking the sea, tropical landscaping, premium hospitality, golden hour lighting."

async def get_editor(page):
    for sel in ['div.ql-editor.ql-blank','div.ql-editor','div[role="textbox"][contenteditable="true"]']:
        try:
            ed = page.locator(sel).first
            await ed.wait_for(state='visible', timeout=10000)
            return ed
        except Exception:
            continue
    return None

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto(GEMINI_URL, wait_until='domcontentloaded')
        await asyncio.sleep(8)
        editor = await get_editor(page)
        if not editor:
            print("Prompt box not found")
            return
        await editor.click(click_count=3)
        await page.keyboard.press('Backspace')
        await editor.type(PROMPT, delay=15)
        await page.keyboard.press('Enter')
        print("Prompt submitted, waiting...")
        for i in range(36):  # 180s max
            await asyncio.sleep(5)
            try:
                ready = await page.evaluate('''() => {
                    const imgs = Array.from(document.querySelectorAll('message-content img'));
                    return imgs.some(img=>img.naturalWidth>250);
                }''')
            except Exception:
                ready = False
            if ready:
                print(f"Image ready after {(i+1)*5}s")
                break
        else:
            print("Timeout")
            return
        await asyncio.sleep(3)
        target = await page.evaluate('''() => {
            const imgs = Array.from(document.querySelectorAll('message-content img'));
            const valid = imgs.filter(i=>i.naturalWidth>250);
            if(valid.length){valid[valid.length-1].setAttribute('id','temp_target');return '#temp_target';}
            return null;
        }''')
        if target:
            img = page.locator(target).first
            dl_btn = page.locator('button[aria-label*="Download" i]').last
            if await dl_btn.is_visible():
                async with page.expect_download(timeout=30000) as dl:
                    await dl_btn.click()
                await (await dl.value).save_as(str(SAVE_PATH))
                print(f"Downloaded → {SAVE_PATH}")
            else:
                await img.screenshot(path=str(SAVE_PATH))
                print(f"Screenshot saved → {SAVE_PATH}")

asyncio.run(main())
