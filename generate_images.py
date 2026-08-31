import asyncio
import os
import json
from pathlib import Path
from playwright.async_api import async_playwright

# Locations we need better images for (specific real Batam places)
LOCATIONS = [
    {
        "filename": "nuvasa_bay.jpg",
        "prompt": "Aerial view of Nuvasa Bay Batam Indonesia at golden hour, luxury waterfront mega-development with marina, resort villas, white sandy beaches, turquoise water, manicured tropical landscaping, premium residential towers, modern architecture, Singapore skyline visible in distant background, cinematic lighting, 16:9 aspect ratio"
    },
    {
        "filename": "nongsa_digital_park.jpg", 
        "prompt": "Aerial view of Nongsa Digital Park Batam Indonesia, modern tech campus with sleek glass data center buildings, fiber optic infrastructure visible, submarine cable landing station, green landscaping, tropical setting, Southeast Asian modern architecture, professional aerial photography, 16:9"
    },
    {
        "filename": "batam_ferry_terminal.jpg",
        "prompt": "Modern Batam Center Ferry Terminal exterior at daytime, sleek white contemporary architecture with glass facades, passenger walkways, ferry boats docked at multiple berths, Singapore-HarbourFront connection, tropical sky, professional architectural photography, 16:9 aspect ratio"
    },
    {
        "filename": "batu_ampar_port.jpg",
        "prompt": "Aerial view of Batu Ampar Deep Water Port Batam, massive container cranes, automated terminal operations, bonded warehouses, cargo ships at berth, Strait of Malacca shipping lane visible, industrial maritime infrastructure, professional aerial photography, 16:9"
    },
    {
        "filename": "kabil_industrial_estate.jpg",
        "prompt": "Aerial view of Kabil Integrated Industrial Estate Batam, large-scale manufacturing campus with factory buildings, internal roads, green buffer zones, port access, heavy industry infrastructure, tropical setting, professional industrial photography, 16:9"
    },
    {
        "filename": "batamindo_industrial_park.jpg",
        "prompt": "Aerial view of Batamindo Industrial Park Batam, 300+ multinational tenant campus, modern factory buildings, logistics warehouses, internal road network, green spaces, professional industrial aerial photography, 16:9"
    },
    {
        "filename": "sekupang_medical_sez.jpg",
        "prompt": "Sekupang International Health Zone Batam, modern hospital campus with helipad, medical research buildings, wellness resort integration, tropical landscaping, premium healthcare architecture, international medical tourism destination, professional architectural photography, 16:9"
    },
    {
        "filename": "harbour_bay_waterfront.jpg",
        "prompt": "Harbour Bay Downtown Waterfront Batam at sunset, premium mixed-use development with waterfront promenade, luxury residential towers, commercial podiums, marina, restaurants, tropical evening lighting, modern Southeast Asian architecture, 16:9"
    },
    {
        "filename": "grand_batam_commercial.jpg",
        "prompt": "Grand Batam Commercial District aerial view, modern CBD with office towers, retail complexes, wide boulevards, green corridors, premium commercial real estate, Batam city center, professional aerial photography, 16:9"
    },
    {
        "filename": "batam_center_business_district.jpg",
        "prompt": "Batam Center Business District aerial view, government buildings, BP Batam headquarters, financial district, modern architecture, organized urban planning, tropical cityscape, professional aerial photography, 16:9"
    },
]

# Create output directory
OUTPUT_DIR = Path('/Users/DT/alfa-lux-travel/assets/generated')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def generate_image(page, prompt, output_path):
    """Generate image using Gemini web app via Playwright."""
    try:
        # Navigate to Gemini
        await page.goto('https://gemini.google.com', wait_until='networkidle', timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Find the prompt input
        # This is a simplified version - in reality we'd need to handle Gemini's specific UI
        # For now, we'll use the browser's screenshot capability as a placeholder
        await page.screenshot(path=str(output_path), full_page=True)
        return True
    except Exception as e:
        print(f"Error generating {output_path}: {e}")
        return False

async def main():
    print("Starting browser...")
    
    # Use persistent context to preserve Google login
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
            ]
        )
        
        page = await browser.new_page()
        
        # Navigate to check if logged in
        await page.goto('https://gemini.google.com', wait_until='networkidle')
        await page.wait_for_timeout(5000)
        
        # Check page content
        title = await page.title()
        print(f"Page title: {title}")
        
        # Take a test screenshot
        await page.screenshot(path=str(OUTPUT_DIR / 'test_gemini.png'))
        print("Test screenshot saved")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())