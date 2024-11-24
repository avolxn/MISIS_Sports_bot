from frontend.bot import main
import asyncio
import logging
import sys

# Этот корневой .py файл и нужно запускать, чтобы стартануть бота

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, stream=sys.stdout)
    asyncio.run(main())