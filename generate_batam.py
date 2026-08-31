#!/usr/bin/env python3
"""Generate 10 Batam-specific images via Gemini web using Playwright CDP."""
import asyncio, json, pathlib
from playwright.async_api import async_playwright

CDP_URL = "http://127.0.0.1:9222"
GEMINI_URL = "https://gemini.google.com/app?hl=en"
ASSETS_DIR = pathlib.Path("assets")
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_JSON = "batam-images.json"

PROMPTS = [
    "Generate an image: Aerial drone view of Batam Riau Islands, Indonesia — modern industrial parks, shipyards along the coastline, turquoise sea, Singapore visible in the distant background, bright sunny day.",
    "Generate an image: Interior of BP Batam investment office, modern glass building, Indonesian officials in business attire meeting with international investors, presentation screen showing SEZ map, professional atmosphere.",
    "Generate an image: Batu Ampar Deep Water Port, Batam — large container ships, cranes, logistics operations, clear blue sky, busy commercial harbor activity.",
    "Generate an image: Nongsa Digital Park, Batam — ultra-modern tech campus, glass buildings, lush tropical greenery, coworking spaces, digital infrastructure.",
    "Generate an image: Private ferry terminal, Batam Centre — premium executive lounge, fast ferry departing to Singapore, waterway with modern skyline, bright daylight.",
    "Generate an image: Batamindo Industrial Park — factory floor, advanced manufacturing equipment, technicians in clean-room gear, precision engineering.",
    "Generate an image: Nuvasa Bay luxury resort, Batam — infinity pool overlooking the sea, tropical landscaping, premium hospitality, golden hour lighting.",
    "Generate an image: SIJORI Growth Triangle map infographic — Singapore, Batam, Johor connected by transport routes, modern clean design, corporate blue and gold color scheme.",
    "Generate an image: Executive yacht charter crossing Singapore Strait from Singapore to Batam — luxury vessel, clear blue waters, dramatic sky, premium travel.",
    "Generate an image: Batam waterfront dining and networking reception — executives in business casual, premium outdoor venue, string lights, harbor view, evening ambiance.",
]

async def get_editor(page):
    for sel in ['div.ql-editor.ql-blank','div.ql-editor','div[role="textbox"][contenteditable="true"]']:
        try:
            ed = page.locator(sel).first
            await ed.wait_for(state='visible', timeout=10000)
            return ed
        except Exception:
            continue
    return None

async def submit_and_download(page, prompt, save_path, idx):
    editor = await get_editor(page)
    if not editor:
        print(f"[{idx}] Prompt box not found")
        return False
    await editor.click(click_count=3)
    await page.keyboard.press('Backspace')
    await editor.type(prompt, delay=15)
    await page.keyboard.press('Enter')
    print(f"[{idx}] Prompt submitted, waiting for image...")
    ready = False
    for i in range(30):  # up to 150s
        await asyncio.sleep(5)
        try:
            ready = await page.evaluate('''() => {
                const imgs = Array.from(document.querySelectorAll('message-content img'));
                return imgs.some(img=>img.naturalWidth>250);
            }''')
        except Exception:
            pass
        if ready:
            print(f"[{idx}] Image ready after {(i+1)*5}s")
            break
    if not ready:
        print(f"[{idx}] Timeout waiting for image")
        return False
    await asyncio.sleep(3)
    try:
        target = await page.evaluate('''() => {
            const imgs = Array.from(document.querySelectorAll('message-content img'));
            const valid = imgs.filter(i=>i.naturalWidth>250);
            if(valid.length){valid[valid.length-1].setAttribute('id','temp_target');return '#temp_target';}
            return null;
        }''')
        if target:
            img = page.locator(target).first
            await img.scroll_into_view_if_needed()
            dl_btn = page.locator('button[aria-label*="Download" i]').last
            if await dl_btn.is_visible():
                async with page.expect_download(timeout=30000) as dl:
                    await dl_btn.click()
                download = await dl.value
                await download.save_as(str(save_path))
                print(f"[{idx}] Downloaded → {save_path}")
                return True
            else:
                await img.screenshot(path=str(save_path))
                print(f"[{idx}] Screenshot saved → {save_path}")
                return True
    except Exception as e:
        print(f"[{idx}] Download error: {e}")
    return False

async def main():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(CDP_URL)
        except Exception as e:
            print(f"Failed to connect to CDP at {CDP_URL}: {e}")
            return
        if not browser.contexts:
            print("No browser contexts – is Chrome running with remote debugging?")
            return
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto(GEMINI_URL, wait_until='domcontentloaded')
        await asyncio.sleep(8)
        saved = []
        for i, prompt in enumerate(PROMPTS, 1):
            path = ASSETS_DIR / f"batam-{i:02d}.jpg"
            ok = await submit_and_download(page, prompt, path, i)
            if ok:
                saved.append(str(path))
            await page.goto(GEMINI_URL, wait_until='domcontentloaded')
            await asyncio.sleep(12)
        with open(OUTPUT_JSON, 'w') as f:
            json.dump(saved, f, indent=2)
        print(f"Saved {len(saved)} images to {OUTPUT_JSON}")

if __name__ == '__main__':
    asyncio.run(main())
