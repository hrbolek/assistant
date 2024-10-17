import asyncio
import re
from datasource import CachedDownloader, Crawler
import bs4

async def Run():
    alltext = []
    async with CachedDownloader(cachelocation="./pagecache") as downloader:
        async with Crawler(pattern=r'https://unob.cz/univerzita/co-muzu-studovat/([^\"]+)') as crawler:
            toget = ["https://www.unob.cz/univerzita/co-muzu-studovat/"]
            while len(toget) > 0:
                [url, *toget] = toget
                page = await downloader(url=url)
                scan = crawler(pagecontent=page)
                if scan:
                    for m in scan:
                        toget.append(m[0])

                    bsanalyzer: bs4.BeautifulSoup = bs4.BeautifulSoup(page, features="html.parser")
                    text = bsanalyzer.find_all("div", {"class": "elementor-widget-container"})
                    for item in text:
                        itemtexts = item.stripped_strings
                        wholetext = ' '.join(itemtexts)
                        alltext.append(wholetext)
                        


    reduced = []
    for line in alltext:
        line = line.strip()
        if len(line) > 1:
            if line not in reduced:
                reduced.append(line)
    for index, line in enumerate(reduced):
        reduced[index] = line + "\n"

    with open("./alltext.txt", "w", encoding="utf-8") as f:
        f.writelines(reduced)


asyncio.run(Run())