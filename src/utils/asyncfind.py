import asyncio

async def FindAsync(string: str, keywords: list[str]) -> float:
    keywordMap = {} 

    async with asyncio.TaskGroup() as tg: 
        for keyword in keywords:
            async def find(k):
                keywordMap[k] = string.find(k)

            tg.create_task(find(keyword))

    return (sum(1 for m in keywordMap.values() if m >= 0) / len(keywords)) * 100