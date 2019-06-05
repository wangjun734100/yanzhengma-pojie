import os
import time
import random,json
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains




# 匹配到原图，对原图进行操作
def match_source(image, source_path='./sources'):
    #image是验证码图片
    # 遍历文件夹下面的所有图片
    for source in sorted(os.listdir(source_path)):
        source_img = Image.open(os.path.join(source_path, source))
        # 根据自己电脑的实际情况调整
        pixel1 = image.getpixel((846, 429))
        pixel2 = source_img.getpixel((846, 429))
        if abs(pixel1[0]-pixel2[0]) < 5:
            print('当前匹配的地图是',source)
            return source_img
    return None

# 截取当前验证码图片
def capture_captcha(browser, savename='captcha.png'):
    '''
    captcha = WebDriverWait(browser, 60).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_img')))
    # location = captcha.location
    # size = captcha.size
    # top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size['width']
    # print('[INFO]: Captcha location - (top, bottom, left, right) -> ({}, {}, {}, {})'.format(top, bottom, left, right))
    time.sleep(1)
    left, top, right, bottom = 790, 280, 1100, 480
    screenshot = browser.get_screenshot_as_png()
    screenshot = Image.open(BytesIO(screenshot))
    screenshot.save('sd.png')
    captcha_img = screenshot.crop((left, top, right, bottom))
    captcha_img.save(savename)
    return savename
    '''
    WebDriverWait(browser, 60).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_img')))
    slider = browser.find_element_by_class_name('geetest_slider_button')
    x = slider.location['x']
    ActionChains(browser).click_and_hold(slider).perform()
    ActionChains(browser).move_by_offset(xoffset=230, yoffset=0).perform()
    time.sleep(0.3)
    browser.save_screenshot(savename)
    ActionChains(browser).release(slider).perform()
    return savename, x

# 获得滑块对象
def get_slider(browser):
    slider = browser.find_element_by_xpath('//*[@class="geetest_slider_button"]')
    return slider

# 获得缺口偏移量
def get_gap_offset(image, source_img, x):
    # print("我是x",x)
    # 根据自己电脑的实际情况调整
    for i in range(827, 1075):#遍历的是验证码的横坐标
        for j in range(420, 567):#遍历的是验证码的纵坐标
            pixel1 = image.getpixel((i, j))
            pixel2 = source_img.getpixel((i, j))
            if abs(pixel1[0]-pixel2[0]) >= 33 and abs(pixel1[1]-pixel2[1]) >= 33 and abs(pixel1[2]-pixel2[2]) >= 33:
                print("这是横坐标", i)
                print("这是纵坐标", j)
                print("这是pixel1", pixel1)
                print("这是pixel2", pixel2)
                # 获取到缺口偏移量
                print("这是缺口的左侧横坐标",i)       # 打印查看缺口x轴的偏移量
                print(i - 600 - x  - 13)
                return int(i - 600 - x  - 13)

# 将滑块移动到特定位置
def move_to_gap(browser, slider, tracks, data):
    ActionChains(browser).click_and_hold(slider).perform()
    for track in tracks:
        ActionChains(browser).move_by_offset(xoffset=track, yoffset=0).perform()
        # 模拟人工滑动超过缺口位置返回至缺口的情况，数据来源于人工滑动轨迹，同时还加入了随机数，都是为了更贴近人工滑动轨迹
    imitate = ActionChains(browser).move_by_offset(xoffset=-1, yoffset=0)
    time.sleep(0.015)
    imitate.perform()
    time.sleep(random.randint(6, 10) / 10)
    imitate.perform()
    time.sleep(0.04)
    imitate.perform()
    time.sleep(0.012)
    imitate.perform()
    time.sleep(0.019)
    imitate.perform()
    time.sleep(0.033)
    ActionChains(browser).move_by_offset(xoffset=1, yoffset=0).perform()
    # 放开圆球
    ActionChains(browser).pause(random.randint(6, 14) / 10).release(slider).perform()
    time.sleep(2)
    time.sleep(2)
    return browser

# 破解滑块验证码
def crack_captcha(browser, data, t_len=12, func_kind=3):
    savename,x = capture_captcha(browser, savename='captcha.png')
    image = Image.open(savename)
    time.sleep(1)
    source_img = match_source(image, source_path='./sources')
    # print('测试，我是否执行了')
    if source_img is None:
        print('[Error]: Fail to match sources...')
        exit(-1)
    # 计算出滑块应该移动的距离
    distance = get_gap_offset(image, source_img, x)
    if distance is None:
        print('[Error]: Fail to match sources...')
        exit(-1)
    time.sleep(2)
    # 找到滑块
    slider = get_slider(browser)
    tracks = get_track(distance)
    time.sleep(0.5)
    # 移动滑块至特定的位置
    return move_to_gap(browser, slider, tracks, data)

#滑块移动轨迹
def get_track(distance):
    track = []
    current = 0
    mid = distance * 3/4
    t = random.uniform(0.2, 0.4)
    v = 0
    while current < distance:
          if current < mid:
             a = 2
          else:
             a = -3
          v0 = v
          v = v0+a*t
          move = v0*t+1/2*a*t*t
          current += move
          track.append(round(move))
    return track
# 主函数
def main(para):
    # para = json.loads(para)
    dep_code = para["dep_code"].lower()
    arr_code = para["arr_code"].lower()
    dep_time = para["dep_time"][2:]
    flightnumber = para["flightnumber"]
    url = "http://www.ceair.com/booking/{}-{}-{}_JF.html".format(dep_code,arr_code,dep_time)
    print(url)
    # url = "http://www.ceair.com/booking/pek-kmg-190607_JF.html"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--start-maximized')
    browser = webdriver.Chrome(options=chrome_options)
    browser.get(url)
    time.sleep(3)
    try:
        browser.switch_to.frame("centerWindow")
        username = browser.find_element_by_xpath('//*[@id="username"]')
        password  = browser.find_element_by_xpath('//*[@type="password"]')
    except Exception as e:
        print(e)
        browser.refresh()
        browser.switch_to.frame("centerWindow")
        username = browser.find_element_by_xpath('//*[@id="username"]')
        password = browser.find_element_by_xpath('//*[@type="password"]')

    username.send_keys('15074709134')
    password.send_keys('73410012')
    btn  = browser.find_element_by_xpath('//*[@type="button"]')
    btn.click()
    time.sleep(2)
    driver = crack_captcha(browser,"ALLALLA")
    time.sleep(5)
    select_flight(driver,flightnumber)

def select_flight(driver,flightnumber):

    fight = driver.find_element_by_xpath(
        "//div[contains(text(),'{}')]/../following-sibling::section[1]/dl/dd[@data-type='economy']".format(flightnumber))  # 根据航班号获取点击的航班   dd[@data-type='economy'] 根据这个选择经济舱还是头等舱
    # input()
    fight.click()
    time.sleep(1)
    ticket = driver.find_element_by_xpath(
        "//div[contains(text(),'{}')]/../following-sibling::*[2]/div[2]/dl[1]/dd[5]/button".format(flightnumber))  # dl[1] 第一个是便宜 第二个是贵   根据dl 来判断选择什么价位
    ticket.click()
    time.sleep(5)

    #另外添加乘机人   点击添加乘机人按钮
    # add_passenger_btn = driver.find_element_by_xpath('//input[@name="add"]')
    # add_passenger_btn.click()

    #乘机人   选中当前账号的默认乘机人
    passenger = driver.find_element_by_xpath('//*[@name="commonPaxs"]/ul/li')
    passenger.click()
    time.sleep(1)



    # 联系人   当选择账号联系人的时候   联系人选框是默认选中的
    # contact_passenger = driver.find_element_by_xpath('//*[@name="commonContacts"]/ul/li')
    # contact_passenger.click()
    # time.sleep(1)

    #下一步
    btn_passenger = driver.find_element_by_xpath('//*[@id="btn_passenger"]')  # 点击下一步
    btn_passenger.click()
    time.sleep(5)  # 可以设置隐性等待

    discounts = driver.find_element_by_xpath('//*[@id="sylvanas_0"]/hgroup/p/input')  # 取消使用优惠
    discounts.click()
    time.sleep(1)

    read = driver.find_element_by_xpath('//*[@id="pax_confirm"]')  # 点击我已阅读
    read.click()
    time.sleep(1)

    # 获取当前机票的详情
    # build_price = driver.find_element_by_xpath('//*[@class="orange"]/text()[2]')

    # pay = driver.find_element_by_xpath('//*[@id="bookDomesNext"]')  # 点击 下一步支付
    # pay.click()

if __name__ == '__main__':
        i = 1
        print("这是第{}次执行".format(i))
        para = {
            "dep_code":"PEK",
            "arr_code": "KMG",
            "dep_time": "20190607",
            "flightnumber" : "MU2569"
        }
        main(para)
