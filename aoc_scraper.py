import requests

from aoc_cache import Cache
from bs4 import BeautifulSoup


class Scraper:

    def __init__(self, year):
        self.url = "https://adventofcode.com/"
        self.year = str(year)
        self.cache = Cache(f'{self.year}')

    def get_day(self, day) -> list:
        if day not in self.cache.data:
            self.cache.set(day, self._scrape(day))
            self.cache.save_data()

        parser = BeautifulSoup(self.cache.get(day), "html.parser")

        for x in parser.find_all():
            if len(x.get_text(strip=True)) == 0:
                x.extract()

        return self._process(parser.article)

    def _scrape(self, day) -> str:
        print("Scraping Advent of Code...")

        url = f'{self.url}{self.year}/day/{day}'
        response = requests.get(url)

        print("Done! Returning results.")
        return response.text

    def _process(self, element) -> list:
        res = []
        msg = ""
        tmp = ""
        for child in element.children:
            match child.name:
                case "h2":
                    tmp += f'**{child.text}**\n\n'
                case "pre":
                    tmp += f'```\n{child.text}```\n'
                case "p":
                    tmp += f'{self._format_text(child)}\n\n'
                case "ul":
                    for grandchild in child.find_all("li"):
                        tmp += f'- {self._format_text(grandchild)}'
                        tmp += "\n"
                    tmp += "\n"

            if len(tmp) + len(msg) > 2000:
                res.append(msg)
                msg = "...\n\n"

            msg += tmp
            tmp = ""

        res.append(msg)
        return res

    def _format_text(self, element):
        res = ""
        for child in element.children:
            match child.name:
                case "a":
                    res += self._link_embed(child)
                case "em":
                    res += f'**{child.text}**'
                case "code":
                    res += f'`{child.text}`'
                case _:
                    res += child.text

        return res

    def _link_embed(self, element) -> str:
        if element.name != "a" or not element.has_attr("href"):
            return

        text = element.text
        link = element.get("href")

        if link[0] == "/":
            link = f'{self.url}{link[1:]}'
        elif link.isdecimal():
            link = f'{self.url}{self.year}/day/{link}'

        return f'[{text}](<{link}>)'
