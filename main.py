from DrissionPage import ChromiumOptions, ChromiumPage
from time import sleep

def main(userId: str, password: str):
    co = ChromiumOptions()
    co.incognito()
    co.headless()
    co.set_argument('--no-sandbox')
    co.set_argument('--guest')

    page = ChromiumPage()
    page.get("https://syosetu.org/")
    page.ele("@value=ログインページへ").click()
    sleep(2)
    page.ele("@name=id").input(userId)
    page.ele("@name=pass").input(password)
    page.ele("@value=ログイン").click()

    sleep(2)
    page.get("https://syosetu.org/?mode=favo")
    page_num = (int(page.ele(".heading").text[3:-1]) // 10) + 1

    novels = list()
    for i in range(int(page_num)):
        page.get(f'https://syosetu.org/?mode=favo&page={i+1}')
        links = page.eles("@name=multi_id")
        for link in links:
          novels.append(link.attr('value'))
        sleep(3)

    for novel in novels:
        url = f'https://syosetu.org/?mode=favo_input&nid={novel}'
        page.get(url)
        page.ele("#text").input('')
        author = page.ele(".section3").ele('tag:h3').text.split('）(')[0].split('（作者：')[1]
        title = page.ele(f'@href=https://syosetu.org/novel/{novel}/').text
        page.ele("#text").input(f'作品名：{title}\n作者名：{author}')
        page.ele("@value=詳細内容登録").click()
        sleep(2)
    page.quit()

main(input('userId: '), input('password: '))
