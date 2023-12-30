from selenium import webdriver as driver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from PIL import Image
from io import BytesIO
from env.config import USER_NUMBER, USER_PASSWD, COURSER_LINK, PAGE_NUM
import random
import time
import cv2
import re


class Shuake:
    def setup(self, chrome_path):
        # 代码执行完毕后chrome不会关闭
        # 使用指定的chrome浏览器
        service = ChromeService(executable_path=chrome_path)
        options = driver.ChromeOptions()
        options.add_argument("--mute-audio")
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--headless')
        self.driver = driver.Chrome(options=options, service=service)
        # self.driver.maximize_window()
        self.driver.implicitly_wait(5)

    # 获取屏幕截图
    def get_screenshot(self, wait):
        """
            获取屏幕截图，截图结果使用Image打开，打开之后的对象可以用来从中截取出验证码图片
        """
        # 截屏
        screenshot = self.driver.get_screenshot_as_png()

        # 打开图片
        screenshot = Image.open(BytesIO(screenshot))

        return screenshot

    # 获取图片验证码在屏幕截图上的位置
    def get_position(self, wait):
        """
            获取图片验证码在屏幕截图上的位置
        """
        # 获取图片验证码元素
        img = self.driver.find_element(By.XPATH, '//*[@id="drag"]/canvas[1]')

        # 获取验证码在屏幕截图上的坐标
        location = img.location

        # 获取验证码图片的的尺寸
        size = img.size

        # 使用图片坐标和图片尺寸计算出整个图片的区域
        left, top, right, down = location['x'], location['y'], (location['x'] + size['width']), (
                location['y'] + size['height'])

        return left, top, right, down

    # 下载图像
    def get_image(self, wait):

        # 获取截图用的坐标元组
        position = self.get_position(wait)

        # 屏幕截图
        screenshot1 = self.get_screenshot(wait)
        # 将不带阴影的验证码图片抠出
        captcha = screenshot1.crop(position)
        captcha_path = './images/captcha.png'
        with open(captcha_path, 'wb') as f:
            captcha.save(f)
        f.close()
        return captcha_path

    # 获取移动距离
    def get_pos(self, wait):
        # 读取图像文件并返回一个image数组表示的图像对象
        status = False
        while status is False:
            imageSrc = self.get_image(wait)
            image = cv2.imread(imageSrc)
            # GaussianBlur方法进行图像模糊化/降噪操作。
            # 它基于高斯函数（也称为正态分布）创建一个卷积核（或称为滤波器），该卷积核应用于图像上的每个像素点。
            blurred = cv2.GaussianBlur(image, (5, 5), 0, 0)
            # Canny方法进行图像边缘检测
            # image: 输入的单通道灰度图像。
            # threshold1: 第一个阈值，用于边缘链接。一般设置为较小的值。
            # threshold2: 第二个阈值，用于边缘链接和强边缘的筛选。一般设置为较大的值
            canny = cv2.Canny(blurred, 200, 400)  # 轮廓
            # findContours方法用于检测图像中的轮廓,并返回一个包含所有检测到轮廓的列表。
            # contours(可选): 输出的轮廓列表。每个轮廓都表示为一个点集。
            # hierarchy(可选): 输出的轮廓层次结构信息。它描述了轮廓之间的关系，例如父子关系等。
            contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # 遍历检测到的所有轮廓的列表
            for contour in contours:
                # contourArea方法用于计算轮廓的面积
                area = cv2.contourArea(contour)
                # arcLength方法用于计算轮廓的周长或弧长
                length = cv2.arcLength(contour, True)
                # 如果检测区域面积在
                # 计算轮廓的边界矩形，得到坐标和宽高
                if 2000 < area < 2300 and 250 < length < 260:
                    # 计算轮廓的边界矩形，得到坐标和宽高
                    # x, y: 边界矩形左上角点的坐标。
                    # w, h: 边界矩形的宽度和高度。
                    x, y, w, h = cv2.boundingRect(contour)
                    # 在目标区域上画一个红框看看效果
                    # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    # cv2.imwrite("images/111.jpg", image)
                    status = True
                    return x

            self.driver.refresh()
            time.sleep(0.5)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(0.2)
            tan_box = self.driver.find_element(By.XPATH, '//*[@id="msBox"]/div[3]/span')
            tan_box.click()

    # 移动滑块
    def move_slider(self, wait):
        x_distance = self.get_pos(wait)
        # 获取滑块
        slider = self.driver.find_element(By.XPATH, '//*[@id="drag"]/div[2]/div/div/span')
        # 按下鼠标左键
        ActionChains(self.driver).click_and_hold(slider).perform()
        time.sleep(0.2)
        # 移动鼠标
        all_distance = x_distance + 14
        move = 0
        while move < all_distance:
            x = random.randint(6, 10)
            move += x
            ActionChains(self.driver).move_by_offset(x, 2).perform()
        time.sleep(0.5)
        # 释放鼠标
        ActionChains(self.driver).release().perform()
        try:
            time.sleep(0.5)
            check = self.driver.find_element(By.XPATH, '//*[@id="myplayer_display"]/div[1]')
            if check:
                return True
            else:
                return False
        except:
            return False

    # 查询课程
    def check_status(self, wait, page):
        # 查询全部课程
        page = page
        # 记录未选课程
        course = {}

        # 获取最大页数
        pagemax_element = wait.until(
            EC.visibility_of_element_located((By.XPATH,
                                              '/html/body/div/div[3]/div[3]/div/div/div[2]/div[3]/div/div/div[1]/span/strong')))
        pagemax = int(int(pagemax_element.text) / 9 + 0.5)
        while page <= pagemax + 1:

            put_box = self.driver.find_element(By.XPATH,
                                               '/html/body/div/div[3]/div[3]/div/div/div[2]/div[3]/div/div/div[1]/input')
            put_box.clear()
            put_number = self.driver.find_element(By.XPATH,
                                                  '/html/body/div/div[3]/div[3]/div/div/div[2]/div[3]/div/div/div[1]/input')
            put_number.send_keys(page)
            go_page = self.driver.find_element(By.XPATH,
                                               '/html/body/div/div[3]/div[3]/div/div/div[2]/div[3]/div/div/div[1]/button')
            go_page.click()

            time.sleep(0.5)
            ul_element = self.driver.find_element(By.XPATH, '/html/body/div/div[3]/div[3]/div/div/div[2]/ul')
            li_elements = ul_element.find_elements(By.XPATH, './li')
            for li_element in li_elements:
                course_name = str(li_element.find_element(By.XPATH, './p[1]/a').text)
                course_core = float(
                    re.search(r'\d+(\.\d+)?', li_element.find_element(By.XPATH, './p[2]/span[2]').text).group())

                course_status = str(li_element.find_element(By.XPATH, './div/p[1]/span/span').text)
                course_link = str(li_element.find_element(By.XPATH, './p[1]/a').get_attribute('href'))
                course[course_name] = [course_core, course_status, course_link]

            page += 1

        return course

    # 学习课程
    def study_video(self, wait, course_name, course_message, course_link, course_schedule):
        course_time_element = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "/html/body/div/div[3]/div[1]/div/div/div[2]/div[1]/div/div[2]/span[2]")))
        course_time = int(re.search(r'\d+(\.\d+)?', course_time_element.text).group())
        print(
            "当前选择课程：\"{}\"，课程时长{}，课程当前已学习进度{}".format(course_name, course_time, course_schedule))
        play_button = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, '/html/body/div/div[3]/div[1]/div/div/div[2]/div[1]/div/div[4]/a')))
        if play_button.text == "播放":
            play_button.click()
        else:
            self.driver.execute_script("window.open('');")
            all_handles = self.driver.window_handles
            new_window_handle = all_handles[-1]
            self.driver.switch_to.window(new_window_handle)
            self.driver.get(course_link)
            play_button = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, '/html/body/div/div[3]/div[1]/div/div/div[2]/div[1]/div/div[4]/a')))
            play_button.click()

        # 等待新窗口打开
        # self.driver.switch_to.alert.accept()
        try:
            time.sleep(1)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            study_status = self.driver.find_element(By.ID, 'ban-study')
            if study_status:
                return True
        except NoSuchElementException:
            print("{}->开始学习".format(course_name))
            time.sleep(0.5)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            tan_box = self.driver.find_element(By.XPATH, '//*[@id="msBox"]/div[3]/span')
            tan_box.click()
            # 获取移动距离

            # 判断滑块是否成功
            check = self.move_slider(wait)
            while check is False:
                self.get_pos(wait)
                check = self.move_slider(wait)

            pass_schedule = course_time * (float(course_schedule.replace('%', '')) / 100.0)
            not_pass_schedule = course_time - pass_schedule
            wait_time = int(not_pass_schedule + 1)
            print("{}需要学习时长{}".format(course_name, wait_time))
            wait_time_miao = wait_time * 60
            # 等待课程结束
            # self.driver.find_element(By.XPATH,'//*[@id="myplayer_display_button_replay"]')
            time.sleep(wait_time_miao)
            print("{}观看完毕！".format(course_name))

            # 关闭当前标签页 并等待15秒钟 防止打开下一个视频出现弹窗10秒内不能打开新的课程
            current_window_handle = self.driver.current_window_handle
            self.driver.close()
            for handle in self.driver.window_handles:
                if handle != current_window_handle:
                    self.driver.switch_to.window(handle)
            time.sleep(15)
            return False

    # 执行刷课
    def run_shuake(self):
        self.driver.get('https://www.hngbwlxy.gov.cn/#/')
        # time.sleep(0.5)
        wait = WebDriverWait(self.driver, 10)
        # 点击登录
        login_button = wait.until(
            EC.visibility_of_element_located((By.XPATH, '/html/body/div/div[1]/div[1]/div/div/ul/div[1]/a')))
        login_button.click()
        # 输入账号
        user_number = wait.until(
            EC.visibility_of_element_located((By.XPATH,
                                              '//*[@id="loginModal"]/div/div/div[2]/div/div/div/form/div[2]/div[1]/input')))
        user_number.send_keys(USER_NUMBER)
        # 输入密码
        user_passwd = wait.until(
            EC.visibility_of_element_located((By.XPATH,
                                              '//*[@id="loginModal"]/div/div/div[2]/div/div/div/form/div[2]/div[2]/input')))
        user_passwd.send_keys(USER_PASSWD)
        # 点击登录
        user_login_button = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="loginModal"]/div/div/div[2]/div/div/div/form/div[2]/button')))
        user_login_button.click()

        # 查询个人积分
        # time.sleep(0.8)
        core_number = wait.until(
            EC.visibility_of_element_located((By.XPATH,
                                              '/html/body/div/div[1]/div[1]/div/div/ul/div[2]/div[2]/div/p')))
        core_number = re.search(r'\d+(\.\d+)?', core_number.text).group()
        print("当前个人积分：{}".format(core_number))

        # you_want_to_study_url = input("请输入你想要学习的课程URL：")
        you_want_to_study_url = COURSER_LINK
        # 前往所需要学习的课程页面
        self.driver.get(you_want_to_study_url)
        time.sleep(0.5)

        # 获取全部课程
        course = self.check_status(wait, page=PAGE_NUM)
        # 获取URL链接
        for course_name, course_message in course.items():
            course_link = course_message[2]
            self.driver.get(course_link)
            time.sleep(0.5)
            course_schedule_element = self.driver.find_element(By.XPATH,
                                                               "/html/body/div/div[3]/div[1]/div/div/div[2]/div[1]/div/div[3]/span[2]")
            course_schedule = course_schedule_element.text
            if course_schedule != "100.0%":
                study_status = self.study_video(wait, course_name, course_message, course_link, course_schedule)
                if study_status is True:
                    print("今日学习的学分已经够5分，不需要再学习了！")
                    break
                else:
                    print("今日学习的学分未够5分，将为您自动选择下一门课程！")
                    continue

        print("今日学分已够5分或当前URL下的课程已经全部学习完毕！")

