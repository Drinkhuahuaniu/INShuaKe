import asyncio
from Shuake import Shuake


async def main():
    shuake = Shuake()  # 创建 Shuake 实例
    await shuake.start()  # 运行 shuake.start() 方法

if __name__ == '__main__':
    asyncio.run(main())
