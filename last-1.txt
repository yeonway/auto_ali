from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import os

# 크롬 옵션 설정 (프로필 경로)
options = Options()
options.add_argument("user-data-dir=C:\\Users\\hsh\\AppData\\Local\\Google\\Chrome\\User Data")  # ← 너의 경로로 바꿔
options.add_argument("profile-directory=Default")  # 혹은 'Profile 1', 'Profile 2' 등

# 크롬 드라이버 실행 (자동 로그인 됨)
driver = webdriver.Chrome(options=options)

# 원하는 사이트 접속 (알리 실시간 주문 정보)
driver.get("https://portals.aliexpress.com/affiportals/web/link_generator.htm")  

# 알리 링크 변환기
driver.execute_script("window.open('https://portals.aliexpress.com/affiportals/web/link_generator.htm')")

# T 스토리
driver.execute_script("window.open('https://eman.tistory.com/manage/newpost')")

# 유튜브 커뮤니티
driver.execute_script("window.open('https://www.youtube.com/@%EC%9D%B4%EB%A7%A8/posts')")

# 페이지 로딩 대기
wait = WebDriverWait(driver, 10)  # 최대 10초 대기


# 첫 번째 창으로 이동
driver.switch_to.window(driver.window_handles[0])

filename = 'num.csv'

# CSV에서 이미 저장된 값 읽기 (첫번째 컬럼 기준)
existing_values = set()
if os.path.exists(filename):
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                existing_values.add(row[0])

row_index = 1

new_page_url = None  # 여기에 new_page_url 초기화

while True:
    try:
        # 특정 XPath (예: 상품명이나 고유값 위치)
        value_xpath = f'/html/body/div/div/div[3]/div/div/div[2]/div/div/div[2]/table/tbody/tr[{row_index}]/td[2]/div/span'
        value_element = wait.until(EC.presence_of_element_located((By.XPATH, value_xpath)))
        value_text = value_element.text.strip()

        if value_text not in existing_values:
            # 가격 추출
            price_xpath = f'/html/body/div/div/div[3]/div/div/div[2]/div/div/div[2]/table/tbody/tr[{row_index}]/td[10]/div/span'
            price_element = driver.find_element(By.XPATH, price_xpath)
            price_text = price_element.text.strip()
            price = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_text)))

            # 주문 ID 추출
            order_id_xpath = f'/html/body/div/div/div[3]/div/div/div[2]/div/div/div[2]/table/tbody/tr[{row_index}]/td[4]/div'
            order_id_element = driver.find_element(By.XPATH, order_id_xpath)
            order_id_text = order_id_element.text.strip()

            # 제품명 추출
            product_xpath = f'/html/body/div/div/div[3]/div/div/div[2]/div/div/div[2]/table/tbody/tr[{row_index}]/td[6]/div/a'
            product_element = driver.find_element(By.XPATH, product_xpath)
            product_text = product_element.text.strip()

            if price >= 10:
                with open(filename, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([value_text, price, order_id_text, product_text])  # ← 여기만 수정
                existing_values.add(value_text)
                print(f"저장됨: {value_text} 가격: {price}, 주문ID: {order_id_text}, 제품명: {product_text}")

                # 버튼 클릭
                click_xpath = f'/html/body/div/div/div[3]/div/div/div[2]/div/div/div[2]/table/tbody/tr[{row_index}]/td[5]/button'
                button = wait.until(EC.element_to_be_clickable((By.XPATH, click_xpath)))
                button.click()
                print(f"{row_index}번 행 버튼 클릭 완료")

                # 새 창 핸들
                current_handle = driver.current_window_handle
                handles = driver.window_handles

                new_handle = None

                for handle in handles:
                    if handle != current_handle:
                        new_handle = handle
                        break


                if new_handle:
                    driver.switch_to.window(new_handle)
                    new_page_url = driver.current_url
                    print("새 창 URL:", new_page_url)

                #name 추출
                name_Xpath = '/html/body/div[3]/div/div[1]/div/div[1]/div[1]/div[2]/div[5]/h1'
                try:
                    name_element = wait.until(EC.presence_of_element_located((By.XPATH, name_Xpath)))
                    name = name_element.text.strip()
                    print("상품 이름", name)
                except:
                    name = ""
                    print("상품 이름 추출 실패")

                    driver.close()
                    driver.switch_to.window(current_handle)
                else:
                    print("새 창을 찾을 수 없습니다.")
                    new_page_url = None

        else:
            print(f"중복된 값 발견, 건너뜀: {value_text}")

        row_index += 1

    except Exception as e:
        print(f"탐색 종료 또는 오류 발생: {e}")
        break



# 두 번째 창(탭)으로 이동
driver.switch_to.window(driver.window_handles[1])

if new_page_url is not None:
    # 알리 링크 입력(변환 전)
    input_xpath = '/html/body/div/div/div[3]/div/div/div[3]/div[2]/div/div/div/div/form[1]/div/div[3]/div[2]/span/textarea'
    input_element = wait.until(EC.element_to_be_clickable((By.XPATH, input_xpath)))
    input_element.click()
    input_element.clear()
    input_element.send_keys(new_page_url)

    # 옆 박스 클릭
    box_xpath = '/html/body/div/div/div[3]/div/div/div[3]/div[2]/div/div/div/div/form[2]/div/div[2]/span/textarea'
    box_element = wait.until(EC.element_to_be_clickable((By.XPATH, box_xpath)))
    box_element.click()

    # 변환 버튼 클릭
    convert_button_xpath = '/html/body/div/div/div[3]/div/div/div[3]/div[2]/div/div/div/div/form[1]/button'
    convert_element = wait.until(EC.element_to_be_clickable((By.XPATH, convert_button_xpath)))
    convert_element.click()
else:
    print("변환할 URL이 없습니다.")

# T 스토리로 가기(세 번째 창)
driver.switch_to.window(driver.window_handles[2])

# 페이지 로딩 대기
wait = WebDriverWait(driver, 10)  # 최대 10초 대기
print("페이지 로그인 하기")



# 드롭다운 버튼 클릭해서 메뉴 열기
dropdown_xpath = '/html/body/div[1]/div/main/div/div[1]/div[1]/button/i[1]'
dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpath)))
dropdown.click()

# 메뉴 항목 클릭 (전동 자전거 DIY)
menu_item_xpath = '/html/body/div[1]/div/main/div/div[1]/div[2]/div/div[3]/span'
menu_item = wait.until(EC.element_to_be_clickable((By.XPATH, menu_item_xpath)))
menu_item.click()


# 제목 입력란
title_input_xpath = '/html/body/div[1]/div/main/div/div[2]/textarea'
title_input = wait.until(EC.element_to_be_clickable((By.XPATH, title_input_xpath)))
title_input.click()
title_input.clear()
title_input.send_keys(name) # 아까 복사한 상품명


# 완료라고 치기 전까지 대기
print("=" * 50)
print("T스토리 글 작성을 진행하세요.")
print("글 작성이 완료되면 터미널에 '완료'를 입력하고 Enter를 눌러주세요.")
print("=" * 50)

def wait_for_completion():
    """사용자가 '완료'를 입력할 때까지 대기"""
    while True:
        user_input = input("글 작성 상태 (완료 입력 시 다음 단계로): ").strip()
        if user_input.lower() in ['완료', '완료!', 'done', 'finish']:
            print("글 작성 완료 확인! 다음 단계를 진행합니다...")
            break
        else:
            print("글 작성을 계속하세요. 완료되면 '완료'를 입력해주세요.")

# 완료 대기 실행
wait_for_completion()

# 네 번째 창으로 이동(유튜브 게시물)
driver.switch_to.window(driver.window_handles[3])

# 유튜브 게시물 창 클릭 후 글자 넣기
youtube_input_xpath = (
    '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/'
    'div[1]/ytd-section-list-renderer/div[2]/ytd-backstage-items/ytd-item-section-renderer/div[1]/'
    'ytd-comments-header-renderer/div[7]/ytd-backstage-post-dialog-renderer/div[2]/ytd-commentbox/'
    'div[2]/div/div[2]/tp-yt-paper-input-container/div[2]/div/div[1]/ytd-emoji-input/'
    'yt-user-mention-autosuggest-input/yt-formatted-string/div'
)

youtube_input_element = wait.until(EC.element_to_be_clickable((By.XPATH, youtube_input_xpath)))
youtube_input_element.click()
youtube_input_element.clear() # 없어도 됨(원래 있던 글자 지우는 거여서)
youtube_input_element.send_keys(new_page_url)


# 완료라고 치기 전까지 대기
print("=" * 50)
print("T스토리 글 작성을 진행하세요.")
print("글 작성이 완료되면 터미널에 '완료'를 입력하고 Enter를 눌러주세요.")
print("=" * 50)

def wait_for_completion():
    """사용자가 '완료'를 입력할 때까지 대기"""
    while True:
        user_input = input("글 작성 상태 (완료 입력 시 다음 단계로): ").strip()
        if user_input.lower() in ['완료', '완료!', 'done', 'finish']:
            print("글 작성 완료 확인! 다음 단계를 진행합니다...")
            break
        else:
            print("글 작성을 계속하세요. 완료되면 '완료'를 입력해주세요.")

# 완료 대기 실행
wait_for_completion()

# 유튜브 게시물 게시 버튼 클릭
youtube_post_button_xpath = (
    '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/'
    'div[1]/ytd-section-list-renderer/div[2]/ytd-backstage-items/ytd-item-section-renderer/div[1]/'
    'ytd-comments-header-renderer/div[7]/ytd-backstage-post-dialog-renderer/div[2]/ytd-commentbox/'
    'div[2]/div/div[5]/div[5]/ytd-button-renderer[2]/yt-button-shape/button/yt-touch-feedback-shape/'
    'div/div[2]'
)

youtube_post_button_element = wait.until(EC.element_to_be_clickable((By.XPATH, youtube_post_button_xpath)))
youtube_post_button_element.click()


# 드라이버 종료
driver.quit()

# 테스트용 대기
#wait.until(lambda d: False)  # 무한 대기 대신 필요한 대기 조건 넣기 or 삭제
#코드 전체 멈추기

# XPath로 버튼 클릭
# xpath = '//*[@id="example-button"]'  # ← 클릭할 요소의 XPath로 바꿔
# element = driver.find_element(By.XPATH, xpath)
# element.click()

# 한 번 클릭 할때는 이거 쓰기



# 실시간 주문 정보로 들어갈 수 있도록 클릭(바로 들어가져서 없앰)
#btn1 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn1"]')))
#btn1.click() 

#btn2 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn2"]')))
#btn2.click()