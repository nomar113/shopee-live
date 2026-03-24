import asyncio
from ADB import ADB
from lives import Live

async def main_loop(live, adb):
    cont_lives_scroll = 0
    while True:
        live.claimCoin()
        if not live.hasCoin():
            live.nextLive()
            live.loadButtoms()
            cont_lives_scroll += 1
            if cont_lives_scroll > 10:
                live.clickLiveHome()
                cont_lives_scroll = 0
        else:
            live.waitToReceiveCoins()
            live.claimCoin()
        await asyncio.sleep(0.1)

async def timeout_action():
    await asyncio.sleep(3)
    print("⏰ 3 segundos se passaram! Executando ação...")
    print("Comando executado!")

async def main():
    live = Live()
    adb = ADB()
    await asyncio.gather(
        main_loop(live, adb),
        timeout_action()
    )

if __name__ == "__main__":
    asyncio.run(main())
