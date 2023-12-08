import requests, random, time
from enum import Enum
from bs4 import BeautifulSoup
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")
options.add_argument("--deisable-blink-features=AutomationControlled")
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options._binary_location = "D:\PROJECTS\DempingParser\webdriver\driver\win32\chromedriver.exe"

driver = webdriver.Chrome(options=options)

def guess_parse_method(url: str):
    if "market.yandex.ru" in url:
        return ParserMethods.YANDEX_MARKET
    elif "ozon.ru" in url:
        return ParserMethods.OZON
    elif "wildberries.ru" in url:
        return ParserMethods.WILDBERRIES
    elif "megamarket.ru" in url:
        return ParserMethods.SBER_MARKET
    elif "aliexpress.ru" in url:
        return ParserMethods.ALIEXPRESS
    else:
        return None

def get_free_proxies():
    url = "https://free-proxy-list.net/"
    # получаем ответ HTTP и создаем объект soup
    c = requests.get(url).content
    with open("tableoutput.htm", "w", -1, "utf-8") as f:
        f.write(c.decode("utf-8"))

    soup = BeautifulSoup(c, "html.parser")
    proxies = []
    for row in soup.find("table").find_all("tr")[1:]:
        tds = row.find_all("td")
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            host = f"{ip}:{port}"
            proxies.append(host)
        except IndexError:
            continue
    return proxies

def create_session():
    # создать HTTP‑сеанс
    session = requests.Session()
    # выбираем один случайный прокси
    proxy = random.choice(get_free_proxies())
    session.proxies = {"http": proxy, "https": proxy}
    return session

class ParserMethods(Enum):
    YANDEX_MARKET = 1
    OZON = 2
    WILDBERRIES = 3
    SBER_MARKET = 4
    ALIEXPRESS = 5

def find_integers(string):
    r = ""
    for i in string:
        try:
            int(i)
            r += i
        except:
            pass
    
    return int(r)

def find_raw_model(string):
    string = string.lower()

    stop_word = [
        "многофункциональное", 
        "реле", 
        "двухмодульное", 
        "напряжения", 
        "с", 
        "контролем", 
        "тока", 
        "гарантия", 
        "контроля", 
        "и",
    ]

    for i in stop_word:
        string = string.replace(i, "")
    return " ".join(string.split(",")[0].split())

def parse(url, parse_method):
    session = create_session()

    try:
        content = session.get(url, headers={
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
        }).text
        with open("output.html", "w", -1, "utf-8") as f:
            f.write(content)
            f.close()

        soup = BeautifulSoup(content, "html.parser")

        find(soup, parse_method)
    except Exception as e:
        print(e)

def find(soup, parse_method):
    cost_new = 0
    cost_type = "none"
    title = "none"

    match parse_method:
                case ParserMethods.YANDEX_MARKET:
                    with_yapay = soup.find("h3", attrs={"class": "_1He5n _36SPc _2kgEE _1KE2k fhbmm"})
                    if with_yapay:
                        cost_new = find_integers(with_yapay.find("span", attrs={"data-auto": "price-value"}).text)
                        cost_type = "red"
                    else:
                        with_yapay = soup.find("h3", attrs={"class": "_1He5n _36SPc _2kgEE fhbmm"})

                        if with_yapay:
                            cost_new = find_integers(with_yapay.find_all("span")[1].text)
                            cost_type = "common"
                        else:
                            with_yapay = soup.find("h3", attrs={"class": "_1stjo"})

                            if with_yapay:
                                cost_new = find_integers(with_yapay.text)
                                cost_type = "green"
                            else:
                                print("Error")
                    
                    title = soup.find("h1", attrs={"data-auto": "productCardTitle", "class": "_1a3VS D7c4V _3ORV- _2pkLA"})
                    if not title:
                        title = soup.find("h1", attrs={"class": "_1a3VS D7c4V ZsaCc _2pkLA", "data-auto": "productCardTitle"})

                    title = " ".join(find_raw_model(title.text).split())
                case ParserMethods.OZON:
                    cost_new = soup.find("span", attrs={"class": "m5l lm6 nl"})
                    if cost_new:
                         cost_new = find_integers(cost_new.text)
                    else:
                        print("Error")
                    
                    costtype = soup.find("span", attrs={"class": "l5m l6m l4m ml5"})

                    if costtype:
                        cost_type = "discount"
                    else:
                        cost_type = "common"

                    title = find_raw_model(soup.find("h1", attrs={"class": "nl0"}).text)
                case ParserMethods.WILDBERRIES:
                    pass
                case ParserMethods.SBER_MARKET:
                    pass

    print("Cost:", cost_new)
    print("Title:", title)
    print("Cost type:", cost_type)

def test_finder():
    test_path = "./test/"
    tests_names = [
        # yandexmarket block
        ["yandexmarket/common", ParserMethods.YANDEX_MARKET], 
        ["yandexmarket/green", ParserMethods.YANDEX_MARKET], 
        ["yandexmarket/red", ParserMethods.YANDEX_MARKET],
        
        # ozon block
        ["ozon/common", ParserMethods.OZON],
        ["ozon/discount", ParserMethods.OZON],
        ]

    counter = 1
    for i in tests_names:
        print("test {}. {}".format(counter, i))

        with open(test_path+i[0]+".html", "r", -1, "utf-8") as f:
            content = f.read()
            f.close()

            soup = BeautifulSoup(content, "html.parser")

        find(soup, i[1])
    
        print("--------------------------")

        counter += 1

def parse_by_urls():
    with open("url_list", "r", -1, "utf-8") as f:
        l = f.readlines()

        for line in l:
            parse(line, guess_parse_method(l))

# if __name__ == "__main__":
#     parse_by_urls()