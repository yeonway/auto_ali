# 필요한 모듈 설치:
# pip install selenium requests beautifulsoup4

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import requests
from bs4 import BeautifulSoup

# 1️⃣ 브라우저 설정
driver = webdriver.Chrome()  # 크롬드라이버 실행

# 2️⃣ 알리 제휴 로그인
driver.get("https://")
time.sleep(3)
# 직접 로그인 수동 또는 자동 로그인 코드 삽입
input("로그인 완료 후 엔터 키를 눌러주세요...")

# 3️⃣ 실시간 주문 페이지 이동
driver.get("https://")
time.sleep(3)

# 4️⃣ 필터 조건 설정 (수동 또는 자동화)
# 자동 클릭 방식이 너무 복잡하면, 수동으로 입력하고 엔터하는 것도 좋습니다.
# 예: 가격 > 10, 커미션 > 7%

input("필터 설정 후 엔터 키를 눌러주세요...")

# 5️⃣ 상품 링크 추출
links = driver.find_elements(By.CSS_SELECTOR, "a.product-link")  # 실제 셀렉터로 바꾸세요
raw_urls = [a.get_attribute("href") for a in links]
print("발견된 링크:", raw_urls)

# 6️⃣ 링크 변환기 자동화 (간편하게 requests 사용)
affiliate_urls = []
for url in raw_urls:
    # 변환기 페이지가 API를 제공한다면 POST 요청 사용
    resp = requests.post("https://affiliate-tool-url/convert", data={"url": url})
    soup = BeautifulSoup(resp.text, "html.parser")
    aff_link = soup.select_one("input#affiliate-link").get("value")
    affiliate_urls.append(aff_link)
print("변환된 제휴 링크:", affiliate_urls)

# 7️⃣ 티스토리에 자동 글쓰기 (Selenium 사용)
driver.get("https://www.tistory.com")
time.sleep(2)
driver.find_element(By.LINK_TEXT, "카카오계정으로 시작하기").click()
time.sleep(3)
# 이미 로그인 세션 유지 중이라면, 바로 글쓰기 페이지 이동 가능
driver.get("https://www.tistory.com/manage/post/write")
time.sleep(3)

# 8️⃣ 글 제목 + 본문 입력
title = "알리익스프레스 제휴 상품 모음"
driver.find_element(By.NAME, "title").send_keys(title)

# 본문 작성
body_element = driver.find_element(By.CSS_SELECTOR, "textarea#content")
content_text = ""
for aff in affiliate_urls:
    content_text += f"- 제휴 링크: {aff}\n"
content_text += "\n**disclaimer**\nAliexpress 제휴 프로그램 설정으로...\n#알리익스프레스 #할인\n"
body_element.send_keys(content_text)

# 이미지 첨부는 파일 업로드 버튼을 통한 자동화가 필요
# driver.find_element(By.CSS_SELECTOR, "input[type=file]").send_keys("/path/to/image.jpg")

# 9️⃣ 게시 버튼 클릭
# driver.find_element(By.XPATH, "//button[text()='발행']").click()
print("게시 완료! (출력 없이 작동하도록 활성화 가능)")

# 10️⃣ 브라우저 종료
time.sleep(5)
driver.quit()
