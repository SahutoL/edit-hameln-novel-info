from DrissionPage import ChromiumOptions, ChromiumPage
from dotenv import load_dotenv
from time import sleep
import os
import argparse

load_dotenv()

def login(page, userId, password):
    try:
        page.get("https://syosetu.org/")
        page.ele("@value=ログインページへ").click()
        sleep(2)
        page.ele("@name=id").input(userId)
        page.ele("@name=pass").input(password)
        page.ele("@value=ログイン").click()
        sleep(2)
    except Exception as e:
        print(f"ログインエラー: {e}")
        page.quit()
        return

def get_favorites(page):
    novels = list()
    try:
        page.get("https://syosetu.org/?mode=favo")
        page_num = (int(page.ele(".heading").text[3:-1]) // 10) + 1
        for i in range(int(page_num)):
            page.get(f'https://syosetu.org/?mode=favo&page={i+1}')
            links = page.eles("@name=multi_id")
            novels.extend([link.attr('value') for link in links])
            sleep(3)
        return novels
    except Exception as e:
        print(f"お気に入り小説取得エラー: {e}")
        return novels

def register_details(page, novels, no_note, no_tag):
    for novel in novels:
        try:
            url = f'https://syosetu.org/?mode=favo_input&nid={novel}'
            page.get(url)
            author = page.ele(".section3").ele('tag:h3').text.split('）(')[0].split('（作者：')[1]
            title = page.ele(f'@href=https://syosetu.org/novel/{novel}/').text
            
            if not no_note:
                textfield = page.ele("#text")
                text_to_input = f'作品名：{title}\n作者名：{author}'
                existing_text = textfield.text
                if text_to_input.split('\n')[0] not in existing_text.split(' ') or text_to_input.split('\n')[1] not in existing_text.split(' '):
                    textfield.input(text_to_input)

            if not no_tag:
                script = f"""
                    var ul = document.querySelector('ul.tagit.ui-widget.ui-widget-content.ui-corner-all');
                    var exists = Array.from(ul.children).some(li => li.childNodes[0].textContent === '{title}');
                    if (!exists) {{
                        document.getElementById('singleFieldTags2').value += ',{title}'
                    }}
                """
                page.run_js(script)

            sleep(1)
            page.ele("@value=詳細内容登録").click()
            sleep(2)
        except Exception as e:
            print(f'対象の小説は削除されているか或は非公開に設定されています。\n https://www.google.com/search?q=site:syosetu.org%20nid={novel} にて該当作品の情報が見つかるかもしれません')

def main():
    parser = argparse.ArgumentParser(description='ハーメルンにおけるお気に入り小説情報の自動編集ツール')
    parser.add_argument('--no-note', action='store_true', help='メモ欄への作品名及び作者名の記入処理を無効化します')
    parser.add_argument('--no-tag', action='store_true', help='作品名のタグへの追加処理を無効化します')
    args = parser.parse_args()

    userId = os.getenv('USER_ID')
    password = os.getenv('USER_PASSWORD')

    co = ChromiumOptions()
    co.incognito()
    co.headless()
    co.set_argument('--no-sandbox')
    co.set_argument('--guest')

    page = ChromiumPage()

    login(page, userId, password)
    novels = get_favorites(page)
    if novels:
        register_details(page, novels, args.no_note, args.no_tag)
    page.quit()

if __name__ == "__main__":
    main()