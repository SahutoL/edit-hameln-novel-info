from DrissionPage import ChromiumOptions, ChromiumPage
from time import sleep
import os

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
    try:
        page.get("https://syosetu.org/?mode=favo")
        page_num = (int(page.ele(".heading").text[3:-1]) // 10) + 1
        novels = []
        for i in range(int(page_num)):
            page.get(f'https://syosetu.org/?mode=favo&page={i+1}')
            links = page.eles("@name=multi_id")
            novels.extend([link.attr('value') for link in links])
            sleep(3)
        return novels
    except Exception as e:
        print(f"お気に入り取得エラー: {e}")
        page.quit()
        return []

def register_details(page, novels):
    try:
        for novel in novels:
            url = f'https://syosetu.org/?mode=favo_input&nid={novel}'
            page.get(url)
            author = page.ele(".section3").ele('tag:h3').text.split('）(')[0].split('（作者：')[1]
            title = page.ele(f'@href=https://syosetu.org/novel/{novel}/').text
            textfield = page.ele("#text")
            text_to_input = f'作品名：{title}\n作者名：{author}'
            existing_text = textfield.text

            if text_to_input not in existing_text:
                textfield.input(text_to_input)
            else:
                pass
            script = f"""
                var ul = document.querySelector('ul.tagit.ui-widget.ui-widget-content.ui-corner-all');
                var exists = Array.from(ul.children).some(li => li.querySelector('span.tagit-label').textContent === '{title}');
                if (!exists) {{
                    var li = document.createElement('li');
                    li.className = 'tagit-choice ui-widget-content ui-state-default ui-corner-all tagit-choice-editable';
                    var span = document.createElement('span');
                    span.className = 'tagit-label';
                    span.textContent = '{title}';
                    var a = document.createElement('a');
                    a.className = 'tagit-close';
                    var spanIcon = document.createElement('span');
                    spanIcon.className = 'text-icon';
                    spanIcon.textContent = '×';
                    var spanUiIcon = document.createElement('span');
                    spanUiIcon.className = 'ui-icon ui-icon-close';
                    a.appendChild(spanIcon);
                    a.appendChild(spanUiIcon);
                    li.appendChild(span);
                    li.appendChild(a);
                    ul.appendChild(li);
                }}
            """
            page.run_script(script)
            sleep(1)
            page.ele("@value=詳細内容登録").click()
            sleep(2)
    except Exception as e:
        print(f'詳細内容登録エラー: {e}')
        page.quit()

def main():
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
        register_details(page, novels)
    page.quit()

if __name__ == "__main__":
    main()