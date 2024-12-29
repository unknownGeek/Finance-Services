import asyncio

from Crypto.scalping_15mins_rsi_golden_crossover_indicator_app import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")