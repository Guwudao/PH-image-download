import requests
import os
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
}

domain = "https://cn.pornhub.com"
download_failed_list = []

def pornhub_get_page_list():
    image_page_url = []
    try:
        main_url = domain + "/album/53926892"
        image_page_url.append(main_url)
        html = requests.get(main_url, headers=headers, timeout=180)
        soup = BeautifulSoup(html.text, "html.parser")
        div_pagination = soup.find_all("div", class_="pagination3")

        page_list = div_pagination[0].find_all("a", class_="greyButton")
        for page in page_list:
            image_page_url.append(domain + page.get("href"))

    except Exception as e:
        print("get page list error: ", e)

    print(image_page_url)
    get_all_image_url(image_page_url)


def get_all_image_url(pageList):
    url_list = []

    for page_url in pageList:
        try:
            html = requests.get(page_url, headers=headers, timeout=180)
            # print(html.text)
            soup = BeautifulSoup(html.text, "html.parser")
            div_list = soup.find_all("div", attrs={"class": "js_lazy_bkg photoAlbumListBlock"})
            url_list = url_list + [domain + div.a.get("href") for div in div_list]

        except Exception as e:
            print("get image url error: ", e)

    print(f"总张数：{len(url_list)}")

    n = 0
    for url in url_list:
        # print(url)
        n += 1
        image_download(url, n)


def image_download(url, index):
# def image_download():
#     url = "https://cn.pornhub.com/photo/647114252"

    html = requests.get(url, headers=headers)
    soup = BeautifulSoup(html.text, "html.parser")
    div_list = soup.find_all("div", class_="centerImage")

    section = soup.find_all("section", attrs={"id": "photoInfoSection"})
    title = section[0].find("h1").get_text().replace(" ", "")
    # print(title)

    if not os.path.exists(title):
        os.mkdir(title)

    fileName = title + "_" + str(index)

    if len(div_list) > 0:
        img_url = div_list[0].img.get("src")
        try:
            with open(f"./{title}/{fileName}.jpg", "wb") as f:
                resp = requests.get(img_url, timeout=180)
                f.write(resp.content)
                print(f"下载完成： {url}", index)
        except Exception as e:
            print("download error: ", e, url)
            download_failed_list.append(url)


pornhub_get_page_list()
print(f"download failed list: {download_failed_list}")
# image_download()