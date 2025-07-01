import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import pandas as pd
import re
import cv2
import numpy as np
from datetime import datetime

# 1. 启动Selenium，访问目标网页
chrome_options = Options()
chrome_options.add_argument('--headless')  # 无头模式
chrome_options.add_argument('--disable-gpu')

# 你可以根据实际情况选择webdriver路径
# driver = webdriver.Chrome(executable_path='chromedriver', options=chrome_options)
driver = webdriver.Chrome(options=chrome_options)

url = 'https://www.crazybirdhk.com/'
driver.get(url)

# 2. 等待页面加载，定位图片元素
selector = '#todaysrate > div.gdlr-core-pbf-wrapper-content.gdlr-core-js > div > div:nth-child(2) > div > div > div > div > div > a > img'

# 等待图片加载
for _ in range(10):
    try:
        img_elem = driver.find_element(By.CSS_SELECTOR, selector)
        if img_elem.is_displayed():
            break
    except Exception:
        time.sleep(1)
else:
    driver.quit()
    raise Exception('未找到目标图片元素')

img_url = img_elem.get_attribute('src')
print(f'图片URL: {img_url}')

# 3. 下载图片到image文件夹
img_dir = 'src/Currency/image'
if not os.path.exists(img_dir):
    os.makedirs(img_dir)
img_path = os.path.join(img_dir, 'crazybird_rate.jpg')
resp = requests.get(img_url)
with open(img_path, 'wb') as f:
    f.write(resp.content)

# 4. OCR识别图片前，先裁剪表格区域
from PIL import Image

# 打开原图
image = Image.open(img_path)
width, height = image.size

# 你可以根据实际图片像素手动调整以下crop参数
# 假设表格1在左侧，表格2在右侧，去除顶部约120px，底部约80px
# 左表格区域
left_table = image.crop((95, 110, 630, height-53))
left_table_path = os.path.join(img_dir, 'crazybird_rate_left.jpg')
left_table.save(left_table_path)
# 右表格区域
right_table = image.crop((720 , 110, 1260, height-53))
right_table_path = os.path.join(img_dir, 'crazybird_rate_right.jpg')
right_table.save(right_table_path)

def preprocess_image(img):
    # PIL转OpenCV格式
    img_cv = np.array(img)
    if img_cv.ndim == 3:
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
    # 先放大2倍
    #img_cv = cv2.resize(img_cv, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    # 自适应阈值
    img_cv = cv2.adaptiveThreshold(img_cv, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 35, 15)
    # 形态学开运算去除小噪点
    kernel = np.ones((2,2), np.uint8)
    img_cv = cv2.morphologyEx(img_cv, cv2.MORPH_OPEN, kernel)
    # OpenCV转PIL格式
    img_pil = Image.fromarray(img_cv)
    return img_pil

# 预处理后再OCR
left_table = preprocess_image(left_table)
right_table = preprocess_image(right_table)
left_table.save(os.path.join(img_dir, 'left_table.jpg'))
right_table.save(os.path.join(img_dir, 'right_table.jpg'))

ocr_text_left = pytesseract.image_to_string(left_table, lang='eng+chi_tra')
ocr_text_right = pytesseract.image_to_string(right_table, lang='eng+chi_tra')
print('左表OCR结果:')
print(ocr_text_left)
print('右表OCR结果:')
print(ocr_text_right)

# 币种英文白名单
CURRENCY_WHITELIST = {
    'CNY', 'USD', 'JPY', 'KRW', 'TWD', 'THB', 'SGD', 'MYR', 'VND', 'IDR', 'PHP',
    'EUR', 'GBP', 'CHF', 'AUD', 'NZD', 'CAD', 'AED', 'MOP', 'INR', 'RUB', 'ZAR'
}

def parse_table_lines(ocr_text):
    lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
    table = []
    last_currency_en = ''
    for line in lines:
        # 提取所有数字
        nums = re.findall(r'[\d\.]+', line)
        if len(nums) >= 2:
            # 找到买入、卖出
            buy, sell = nums[:2]
            # 英文币种名为第一个数字前的最后一个大写字母串
            currency_part = line.split(nums[0])[0].strip()
            m = re.findall(r'([A-Z]{2,4})', currency_part)
            currency_en = m[-1] if m else last_currency_en
            last_currency_en = currency_en
            # 备注为卖出数字后的内容
            note_part = line.split(nums[1], 1)[-1].strip() if len(nums) > 1 else ''
            # 只保留白名单币种
            if currency_en in CURRENCY_WHITELIST:
                table.append([currency_en, buy, sell, note_part])
    return table

table_left = parse_table_lines(ocr_text_left)
table_right = parse_table_lines(ocr_text_right)
table = table_left + table_right

header = ["币种(英文)", "本店买入/We Buy", "本店卖出/We Sell", "备注/Notes"]
df = pd.DataFrame(table, columns=header)
print(df)

# 导出为Excel和CSV，文件名带当前日期，采用追加模式
now_str = datetime.now().strftime('%Y%m%d')
excel_path = os.path.join(img_dir, f'crazybird_rate_{now_str}.xlsx')
csv_path = os.path.join(img_dir, f'crazybird_rate_{now_str}.csv')
df.to_excel(excel_path, index=False)
df.to_csv(csv_path, index=False)
print(f'已导出: {excel_path}\n已导出: {csv_path}')

# 7. 清理
os.remove(img_path)
driver.quit()
