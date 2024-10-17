import uuid
import json
import aiohttp

async def simpledownloader(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            # print(resp.status)
            return await resp.text()

def cacheIt(CachedDownloader):
    contextcache = {}
    def result(*, cachelocation, asyncdownloader=simpledownloader):
        func = contextcache.get(cachelocation, None)
        if func is None:
            func = CachedDownloader(cachelocation=cachelocation, asyncdownloader=asyncdownloader)
            contextcache[cachelocation] = func
        return func
    return result

@cacheIt
def CachedDownloader(*, cachelocation: str, asyncdownloader=simpledownloader):
    print(f"CachedDownloader{cachelocation}")
    class Result:
        def __init__(self, cachelocation, asyncdownloader):
            self.cachelocation = cachelocation
            self.asyncdownloader = asyncdownloader
            self.cacheindexfilename = f'{self.cachelocation}/index.json'
            try:
                with open(self.cacheindexfilename, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
            except FileNotFoundError as e:
                self.cache = {}

        async def __aenter__(self):
            return self
        
        async def __call__(self, url):
            cachedid = self.cache.get(url, None)
            if cachedid is None:
                cachedid = f"{uuid.uuid4()}"
                self.cache[url] = cachedid
                cachefilename = f"{self.cachelocation}/{cachedid}.html"

                cachedcontent = await asyncdownloader(url)

                with open(cachefilename, "w", encoding="utf-8") as f:
                    f.write(cachedcontent)
            else:
                cachefilename = f"{self.cachelocation}/{cachedid}.html"
                with open(cachefilename, "r", encoding="utf-8") as f:
                    cachedcontent = f.read()

            return cachedcontent
        
        async def __aexit__(self, exc_type, exc, tb):
            with open(self.cacheindexfilename, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=4)
            pass
        
    return Result(cachelocation=cachelocation, asyncdownloader=asyncdownloader)
