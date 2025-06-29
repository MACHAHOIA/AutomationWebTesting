from selenium import webdriver
from selenium.webdriver.common.by import By


options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver=webdriver.Chrome(options=options)
driver.get("https://bstackdemo.com/")

#__next > div > div > main > div.shelf-container
inputs_container = driver.find_element(By.CSS_SELECTOR, "#__next > div > div > main > div.shelf-container")

# 查找所有 input 元素
inputs = inputs_container.find_elements(By.CLASS_NAME, "shelf-item")

# 输出每个 input 的 CSS Selector
for i, input_elem in enumerate(inputs):
    # 尝试用 id、name、class 生成 selector
    selector = ""
    elem_id = input_elem.get_attribute("id")
    elem_name = input_elem.get_attribute("name")
    elem_class = input_elem.get_attribute("class")
    elem_value = input_elem.get_attribute("value")
    if elem_id:
        selector = f"input#{elem_id}"
    elif elem_name:
        selector = f'input[name="{elem_name}"]'
    elif elem_class:
        # 处理多个 class
        classes = ".".join(elem_class.split())
        selector = f"input.{classes}"
    elif elem_value:
        selector = f'input[value="{elem_value}"]'
    else:
        # 退而求其次，使用 nth-of-type
        selector = f"input:nth-of-type({i+1})"
    print(selector)