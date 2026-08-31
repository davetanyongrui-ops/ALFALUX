import asyncio
import os
import json
import base64
from pathlib import Path
from playwright.async_api import async_playwright

# Locations we need better images for (specific real Batam places)
LOCATIONS = [
    {
        "filename": "nuvasa_bay.jpg",
        "prompt": "Generate an aerial view photograph of Nuvasa Bay Batam Indonesia at golden hour, luxury waterfront mega-development with marina, resort villas, white sandy beaches, turquoise water, manicured tropical landscaping, premium residential towers, modern architecture, Singapore skyline visible in distant background, cinematic lighting, professional aerial photography, 16:9 aspect ratio, photorealistic, 8k quality"
    },
    {
        "filename": "nongsa_digital_park.jpg", 
        "prompt": "Generate an aerial view photograph of Nongsa Digital Park Batam Indonesia, modern tech campus with sleek glass data center buildings, fiber optic infrastructure visible, submarine cable landing station, green landscaping, tropical setting, Southeast Asian modern architecture, professional aerial photography, 16:9 aspect ratio, photorealistic, 8k quality"
    },
    {
        "filename": "batam_ferry_terminal.jpg",
        "prompt": "Generate a photograph of Batam Center Ferry Terminal exterior at daytime, sleek white contemporary architecture with glass facades, passenger walkways, ferry boats docked at multiple berths, Singapore-HarbourFront connection, tropical blue sky, professional architectural photography, 16:9 aspect ratio, photorealistic, 8k quality"
    },
    {
        "filename": "batu_ampar_port.jpg",
        "prompt": "Generate an aerial view photograph of Batu Ampar Deep Water Port Batam, massive container cranes, automated terminal operations, bonded warehouses, cargo ships at berth, Strait of Malacca shipping lane visible, industrial maritime infrastructure, professional aerial photography, 16:9 aspect ratio, photorealistic, 8k quality"
    },
    {
        "filename": "kabil_industrial_estate.jpg",
        "prompt": "Generate an aerial view photograph of Kabil Integrated Industrial Estate Batam, large-scale manufacturing campus with factory buildings, internal roads, green buffer zones, port access, heavy industry infrastructure, tropical setting, professional industrial photography, 16:9 aspect ratio, photorealistic, 8k quality"
    },
    {
        "filename": "batamindo_industrial_park.jpg",
        "prompt": "Generate an aerial view photograph of Batamindo Industrial Park Batam, 300+ multinational tenant campus, modern factory buildings, logistics warehouses, internal road network, green spaces, professional industrial aerial photography, 16:9 aspect ratio, photorealistic, 8k quality"
    },
    {
        "filename": "sekupang_medical_sez.jpg",
        "prompt": "Generate a photograph of Sekupang International Health Zone Batam, modern hospital campus with helipad, medical research buildings, wellness resort integration, tropical landscaping, premium healthcare architecture, international medical tourism destination, professional architectural photography, 16:9 aspect ratio, photorealistic, 8k quality"
    },
    {
        "filename": "harbour_bay_waterfront.jpg",
        "prompt": "Generate a photograph of Harbour Bay Downtown Waterfront Batam at sunset, premium mixed-use development with waterfront promenade, luxury residential towers, commercial podiums, marina, restaurants, tropical evening lighting, modern Southeast Asian architecture, 16:9 aspect ratio, photorealistic, 8k quality"
    },
    {
        "filename": "grand_batam_commercial.jpg",
        "prompt": "Generate an aerial view photograph of Grand Batam Commercial District, modern CBD with office towers, retail complexes, wide boulevards, green corridors, premium commercial real estate, Batam city center, professional aerial photography, 16:9 aspect ratio, photorealistic, 8k quality"
    },
    {
        "filename": "batam_center_business_district.jpg",
        "prompt": "Generate an aerial view photograph of Batam Center Business District, government buildings, BP Batam headquarters, financial district, modern architecture, organized urban planning, tropical cityscape, professional aerial photography, 16:9 aspect ratio, photorealistic, 8k quality"
    },
]

OUTPUT_DIR = Path('/Users/DT/alfa-lux-travel/assets/generated')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def generate_with_gemini(page, prompt, output_path, index):
    """Generate image using Gemini web app."""
    try:
        # Navigate to Gemini if not already there
        await page.goto('https://gemini.google.com', wait_until='networkidle', timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Find the text input area
        # Gemini uses a textarea or contenteditable div for input
        input_selector = 'textarea[aria-label*="message"], textarea[placeholder*="message"], div[contenteditable="true"][data-placeholder*="message"], rich-textarea'
        
        # Wait for input to be available
        await page.wait_for_selector('textarea, div[contenteditable="true"]', timeout=15000)
        
        # Try different selectors for the input
        input_element = None
        for sel in ['textarea', 'div[contenteditable="true"]', 'rich-textarea']:
            elements = await page.query_selector_all(sel)
            for el in elements:
                if await el.is_visible():
                    input_element = el
                    break
            if input_element:
                break
        
        if not input_element:
            print(f"  Could not find input element")
            return False
            
        # Clear and type the prompt
        await input_element.click()
        await page.keyboard.press('Control+A')
        await page.keyboard.press('Delete')
        await input_element.type(prompt, delay=10)
        await page.wait_for_timeout(1000)
        
        # Submit - press Enter
        await page.keyboard.press('Enter')
        
        # Wait for response - look for image generation
        print(f"  Waiting for generation...")
        await page.wait_for_timeout(30000)  # Wait for generation
        
        # Check for generated images in the response
        # Images might be in img tags or in a specific gallery
        images = await page.query_selector_all('img[src*="generated"], img[src*="gstatic"], img[src*="lh3.googleusercontent"]')
        
        # Also check for image containers
        image_containers = await page.query_selector_all('[data-testid*="image"], .image-container, [role="img"]')
        
        print(f"  Found {len(images)} direct images, {len(image_containers)} containers")
        
        # Try to get the latest response area
        response_elements = await page.query_selector_all('[data-message-author="model"], .model-response, [data-response-index]')
        if response_elements:
            latest_response = response_elements[-1]
            # Look for images in the latest response
            response_images = await latest_response.query_selector_all('img')
            print(f"  Images in latest response: {len(response_images)}")
            
            for i, img in enumerate(response_images):
                src = await img.get_attribute('src')
                if src and ('generated' in src or 'gstatic' in src or 'lh3.googleusercontent' in src):
                    print(f"  Found generated image: {src[:100]}")
                    # Try to download it
                    try:
                        # Use page.evaluate to fetch the image
                        img_data = await page.evaluate(f'''async () => {{
                            const response = await fetch("{src}");
                            const blob = await response.blob();
                            return await new Promise(resolve => {{
                                const reader = new FileReader();
                                reader.onloadend = () => resolve(reader.result);
                                reader.readAsDataURL(blob);
                            }});
                        }}''')
                        if img_data and img_data.startswith('data:image'):
                            # Save the image
                            header, data = img_data.split(',', 1)
                            ext = 'png' if 'png' in header else 'jpg'
                            with open(output_path, 'wb') as f:
                                f.write(base64.b64decode(data))
                            print(f"  Saved: {output_path}")
                            return True
                    except Exception as e:
                        print(f"  Error downloading: {e}")
        
        # Fallback: take a screenshot of the response area
        print(f"  Taking screenshot fallback...")
        await page.screenshot(path=str(output_path), full_page=True)
        return True
        
    except Exception as e:
        print(f"  Error generating {output_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("Starting browser with persistent context...")
    
    user_data_dir = os.path.expanduser('~/Library/Application Support/Google/Chrome/Default')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--window-size=1920,1080',
            ],
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await browser.new_page()
        
        # Initial navigation to establish session
        await page.goto('https://gemini.google.com', wait_until='networkidle')
        await page.wait_for_timeout(5000)
        
        print("Session established. Starting image generation...")
        
        for i, loc in enumerate(LOCATIONS):
            output_path = OUTPUT_DIR / loc['filename']
            print(f"\n[{i+1}/{len(LOCATIONS)}] Generating: {loc['filename']}")
            
            success = await generate_with_gemini(page, loc['prompt'], output_path, i)
            
            if success:
                print(f"  ✓ Completed")
            else:
                print(f"  ✗ Failed")
            
            # Wait between generations
            await page.wait_for_timeout(5000)
        
        print("\nAll generations complete!")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())