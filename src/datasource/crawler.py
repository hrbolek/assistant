import hashlib
import re

def cacheIt(Crawler):
    contextcache = {}
    def result(*, pattern):
        func = contextcache.get("cache", None)
        if func is None:
            func = Crawler(pattern)
            contextcache["cache"] = func
        return func
    return result

@cacheIt
def Crawler(pattern):
    class Result:
        def __init__(self, pattern):
            self.done = set()
            self.pattern = pattern

        async def __aenter__(self):
            return self
        
        def __call__(self, *, pagecontent: str):
            str_bytes = pagecontent.encode(encoding="utf-8")
            hash_object = hashlib.sha256(str_bytes)
            hash_hex = hash_object.hexdigest()
            if hash_hex in self.done:
                return
            self.done.add(hash_hex)
            return re.finditer(pattern=self.pattern, string=pagecontent)
        
        async def __aexit__(self, exc_type, exc, tb):
            pass
        
    return Result(pattern)
