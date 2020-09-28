import requests
import threading
import os
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import urllib.parse

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
}

proxy = {
    "https": "127.0.0.1:1087",
    "http": "127.0.0.1:1087",
}

domain = "https://cn.pornhub.com"
download_failed_list = []


def key_word_search(key_word):
    data = {
        "search": key_word
    }
    query_string = urllib.parse.urlencode(data)
    album_search_url = f"https://cn.pornhub.com/albums/female-straight-uncategorized?{query_string}"
    print(album_search_url)

    html = requests.get(album_search_url, headers=headers, timeout=180, proxies=proxy)
    soup = BeautifulSoup(html.text, "html.parser")
    # print(soup)

    li_list = soup.find_all("li", class_="photoAlbumListContainer")

    album_list = [li.a.get("href") for li in li_list]
    print(f"========================== 当前相册个数: {len(album_list)} ==========================")

    title_list = [title_tag.get_text() for title_tag in soup.find_all("div", class_="title-album")][4:-1]
    print(f"========================== 相册列表: {title_list} ==========================")

    count = int(input("需要下载的相册个数："))
    if count <= len(album_list):
        albums = album_list[0:count]
        return pornhub_get_page_list(albums)
    else:
        print("输入个数有误")
        return []

    # get page number
    # page_list = [page.get_text() for page in soup.find_all("li", class_="page_number")]
    # print(page_list)

def pornhub_get_page_list(album_list):
    if isinstance(album_list, list):
        image_page_url = []
        for album in album_list:
            main_url = domain + album
            image_page_url.extend(get_list(main_url))
        print(image_page_url)
        return image_page_url
    elif isinstance(album_list, int):
        main_url = domain + f"/album/{album_list}"
        return get_list(main_url)


def get_list(url):
    url_list = []
    try:
        url_list.append(url)
        html = requests.get(url, headers=headers, timeout=180, proxies=proxy)
        soup = BeautifulSoup(html.text, "html.parser")
        div_pagination = soup.find_all("div", class_="pagination3")

        page_list = div_pagination[0].find_all("a", class_="greyButton")
        url_list.extend([domain + page.get("href") for page in page_list])
        print(url_list)
        return url_list
    except Exception as e:
        print("get page list error: ", e)
        return []

def get_all_image_url(page_list):
    url_list = []
    for page_url in page_list:
        try:
            html = requests.get(page_url, headers=headers, timeout=180, proxies=proxy)
            soup = BeautifulSoup(html.text, "html.parser")
            div_list = soup.find_all("div", attrs={"class": "js_lazy_bkg photoAlbumListBlock"})
            url_list = url_list + [domain + div.a.get("href") for div in div_list]

        except Exception as e:
            print("get image url error: ", e)

    print(f"总张数：{len(url_list)}")
    # print(url_list)
    return url_list


def image_download(info):
    url = info[0]
    index = info[1]

    html = requests.get(url, headers=headers, proxies=proxy)
    soup = BeautifulSoup(html.text, "html.parser")
    div_list = soup.find_all("div", class_="centerImage")

    section = soup.find_all("section", attrs={"id": "photoInfoSection"})
    title = section[0].find("h1").get_text().replace(" ", "")
    # print(title)

    if not os.path.exists(title):
        os.mkdir(title)

    file_name = title + "_" + str(index)

    if len(div_list) > 0:
        img_url = div_list[0].img.get("src")
        try:
            with open(f"./{title}/{file_name}.jpg", "wb") as f:
                resp = requests.get(img_url, timeout=180, proxies=proxy)
                f.write(resp.content)
                print("%s" % (threading.current_thread().name), f"下载完成： {url}", index)
        except Exception as e:
            print("download error: ", e, url)
            download_failed_list.append(url)


def video_analytics():
    domain = "https://cv.phncdn.com/"
    url = "https://cn.pornhub.com/view_video.php?viewkey=ph5d24f5b77c6f6"

    resp = requests.get(url, headers=headers, proxies=proxy)
    print(resp.text)

    html_file = open("./mini.html", 'r', encoding='utf-8').read()
    soup = BeautifulSoup(html_file, "html.parser")
    videos = soup.find_all("source", attrs={"type": "video/mp4"})
    # scripts = soup.find_all("script", attrs={"type": "text/javascript"})
    print(videos)

    for video in videos:
        print(video.get("src"))
        print("-" * 50)


if __name__ == '__main__':

    select = 0
    page_list = []

    while select != 1 and select != 2:
        select = int(input("请输入下载方式，1为搜索下载，2为相册编号下载："))
    if select == 1:
        key_word = str(input("请输入关键字："))
        page_list = key_word_search(key_word)
    elif select == 2:
        num = int(input("请输入相册编号："))
        page_list = pornhub_get_page_list(num)

    if len(page_list) > 0:
        image_list = get_all_image_url(page_list)
        n = 0
        with ThreadPoolExecutor(max_workers=30, thread_name_prefix="当前线程_") as pool:
            for image_url in image_list:
                n += 1
                pool.map(image_download, [(image_url, n)])
        print("========================== 下载完成 ==========================")
    else:
        print("abort by page list not complete")

    if len(download_failed_list) > 0:
        print(f"download failed list: {download_failed_list}")

    # video_analytics()
    # key_word_search("过期米线")