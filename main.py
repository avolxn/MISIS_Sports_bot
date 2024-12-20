from frontend.bot import main
import asyncio
import logging
import sys

# Корневой файл, которые запускает бота

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, stream=sys.stdout)
    asyncio.run(main())