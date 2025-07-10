import asyncio
from ADB import ADB
from lives import Live

async def main_loop(live, adb):
    contLivesScroll = 0
    while True:
        if not live.hasCoin():
            live.nextLive()
            live.loadButtoms()
            contLivesScroll += 1
            if contLivesScroll > 10:
                live.clickLiveHome()
                contLivesScroll = 0
        else:
            live.waitToReceiveCoins()
            live.claimCoin()
            live.validateClaimCoin()
        await asyncio.sleep(0.1)  # Evita travar o loop

async def timeout_action():
    await asyncio.sleep(3)
    print("⏰ 3 segundos se passaram! Executando ação...")
    # Aqui coloque o comando que quer executar
    # Exemplo:
    # live.someMethod()
    # adb.someOtherCommand()
    # Ou qualquer coisa:
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
