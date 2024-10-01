from utils.zapi import Zapi
import aiohttp
import asyncio

async def main():
    
    async with aiohttp.ClientSession() as session:
        buttons = ["Com certeza", "Claro!"]
        zapi = Zapi("3C66B22560C4B086AC4B2242B4E23AC7", "C5D643E2AA4151C1B8572F97", "Fe0e74500268e4524be2bdc1a96e1db3cS")
        print(await zapi.send_button_text(session, "553587112380", "Ola, voce gostaria de saber mais sobre o pix de 15?", buttons))



asyncio.run(main())