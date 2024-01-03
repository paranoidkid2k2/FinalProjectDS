import scrapy
import re
from time import sleep
class collect_animes_info(scrapy.Spider):
    name = 'animes_info'
    def __init__(self):
        self.result = []
        self.parsed_count = 0
    def start_requests(self):
        url_format = "https://myanimelist.net/topanime.php?limit={}"
        amount = 10000
        step = 50
        self.result = [None] * (amount)

        for i in range(0,amount,step):
            yield scrapy.Request(url = url_format.format(i), 
                                callback = self.parse,
                                cb_kwargs = dict(page = i))
    def parse(self, response, page):
        films = response.xpath('//tr[@class="ranking-list"]')
        for i in range(0,len(films)):
            film = films[i]
            url = film.xpath('td[contains(@class,"title")]/a').attrib['href']
            yield response.follow(url = url,callback=self.film_parse,cb_kwargs = dict(id = page+i))
    def film_parse(self,response,id):
        film={}
        film['Name']= response.xpath('//h1[contains(@class,"title-name")]/strong/text()').get()
        film['Score']=response.xpath('//div[contains(@class,"score-label")]/text()').get()
        film['Rank']= response.xpath('//span[contains(@class,"ranked")]/strong/text()').get()[1:]
        self.parse_sidebar_info(response,film)


        self.result[id]=film
        self.parsed_count+=1
        if len(self.result) == self.parsed_count:
            for item in self.result:
                yield item
    def parse_sidebar_info(self,response,film):
        info_list = ['Type', "Episodes", "Aired", "Premiered", "Producers", "Studios", "Genres",
                     "Genre","Popularity", "Members", "Favorites"]
        xpath_prototype='//span[text()="{}:"]/parent::div[@class="spaceit_pad"]//text()'
        for title in info_list:
            temp=response.xpath(xpath_prototype.format(title)).getall()
            if len(temp) == 0:
                # if title != 'Genre' : print(film['Name'],'-',title,"skip")
                continue
            temp.remove(title+":")
            temp=listProcess(temp)

            if title == "Genre":
                title = "Genres"
                film[title]=temp
            elif title in ['Type', "Episodes", "Aired", "Premiered","Popularity", "Members", "Favorites"]:
                film[title]=temp[0]
            else:
                film[title]=temp
def listProcess(plist):
    result=plist
    result=removeDuplicate(result)
    result=deleteNnS(result)
    result=deleteEmpty(result)
    # if len(result) == 1:
    #     result=result[0]
    return result
def removeDuplicate(plist):
    result=list(set(plist))
    return result
def deleteNnS(plist):
    result=[]
    for item in plist:
        result.append(re.sub('\n\s*|\s\s+|^,\s*',"",item))
    # print(result)
    return result
def deleteEmpty(plist):
    result=[]
    for item in plist:
        if item != "":
            result.append(item)
    return result