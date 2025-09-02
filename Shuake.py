from progressbar import ProgressBar, Percentage, Bar
from playwright.async_api import async_playwright
from config.config import USER_NUMBER, USER_PASSWD, COURSER_LINK
from getcourseid import Get_course_id
from PIL import Image
from io import BytesIO
import asyncio as asynioc
import cv2
import re


class Shuake:
    async def start(self):
        async with async_playwright() as playwright:
            # playwright = await async_playwright().start()
            # chromium = playwright.chromium
            # self.browser = await chromium.launch(headless=False)
            self.browser = await playwright.chromium.launch(channel='chrome', headless=True, args=['--mute-audio'])
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            await self.page.goto(
                "https://www.hngbwlxy.gov.cn/#/")
            await self.login()
            await self.check_user_core()
            try:
                status = await self.start_shuake()
                if status:
                    await self.browser.close()
            except:
                print("网络异常！请再次运行！")

    async def login(self):
        login_button = await self.page.wait_for_selector(
            'body > div > div.main-bg-top.ng-scope > div:nth-child(1) > div > div > ul > div.grid_9.searchInput > a')
        await login_button.click()
        username_input = await self.page.wait_for_selector(
            '//*[@id="loginModal"]/div/div/div[2]/div/div/div/form/div[2]/div[1]/input')
        await username_input.fill(USER_NUMBER)
        password_input = await self.page.wait_for_selector(
            '//*[@id="loginModal"]/div/div/div[2]/div/div/div/form/div[2]/div[2]/input')
        await password_input.fill(USER_PASSWD)
        login_button = await self.page.wait_for_selector(
            '//*[@id="loginModal"]/div/div/div[2]/div/div/div/form/div[2]/button')
        await login_button.click()

    async def check_user_core(self):
        core_number = await self.page.wait_for_selector(
            'body > div > div.main-bg-top.ng-scope > div:nth-child(1) > div > div > ul > div.grid_12.searchInput > div.search_user_wrap > div > p')
        core_number = await core_number.inner_text()
        core_number = re.search(r'\d+(\.\d+)?', core_number).group()
        print(f"当前个人积分为：{core_number}")

    async def get_course_link(self):
        await self.page.goto(COURSER_LINK)
        cookies = await self.context.cookies()
        cookies = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        channelId = COURSER_LINK.split('=')[-1]
        rowlength = await self.page.wait_for_selector(
            'body > div > div.container_24.clear-fix.ng-scope > div.grid_18.pad_left_20 > div > div > div.allCourse.mar_top_20 > div:nth-child(5) > div > div > div.page-total > span > strong')
        rowlength = await rowlength.inner_text()
        course_messages = await Get_course_id(cookies, channelId, rowlength, 1)
        return course_messages

    async def get_captcha_image(self):
        img = await self.page.wait_for_selector('#drag > canvas.undefined')
        bounding_box = await img.bounding_box()
        left = round(bounding_box['x'])
        top = round(bounding_box['y'])
        right = round(left + bounding_box['width'])
        down = round(top + bounding_box['height'])

        screenshot = await self.page.screenshot()
        screenshot = Image.open(BytesIO(screenshot))
        captcha = screenshot.crop((left, top, right, down))
        captcha_path = './images/captcha.png'
        with open(captcha_path, 'wb') as f:
            captcha.save(f, format='png')
        f.close()
        return captcha_path

    async def get_captcha_position(self):
        status = False
        while status is False:
            captcha_path = await self.get_captcha_image()
            imageSrc = captcha_path
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
                if 20 < area < 30 and 230 < length < 300:
                    # 计算轮廓的边界矩形，得到坐标和宽高
                    # x, y: 边界矩形左上角点的坐标。
                    # w, h: 边界矩形的宽度和高度。

                    x, y, w, h = cv2.boundingRect(contour)
                    # 在目标区域上画一个红框看看效果
                    # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    # cv2.imwrite("images/111.jpg", image)
                    status = True
                    return x

            refresh_pic_button = await self.page.wait_for_selector('#drag > div.refreshIcon')
            await refresh_pic_button.click()

    async def move_to_slider(self):
        x_move_position = await self.get_captcha_position()
        slider = await self.page.wait_for_selector('#drag > div.sliderContainer > div > div')
        slider_position = await slider.bounding_box()
        await slider.hover()
        await self.page.mouse.down()
        await self.page.mouse.move(slider_position['x'] + x_move_position + 30, slider_position['y'] + 2, steps=5)
        await self.page.mouse.up()

        await asynioc.sleep(1)
        class_attribute = await self.page.locator('//*[@id="drag"]/div[2]').get_attribute('class')
        if class_attribute == 'sliderContainer sliderContainer_success':
            return True
        else:
            return False

    async def wait_for_jwplayer(self, selector):
        while True:
            try:
                player = await self.page.wait_for_selector(
                    "body > div > div > div > div.sigle-video.ng-scope > div.sigle-video-bg > div")
                await player.hover()
                jwplayer = await self.page.wait_for_selector(selector)
                if jwplayer:
                    break
                else:
                    await asynioc.sleep(1)
            except Exception as e:
                await asynioc.sleep(1)

        return jwplayer

    async def start_shuake(self):
        course_messages = await self.get_course_link()
        for course_message in course_messages:
            for course_id, course_name in course_message.items():
                course_url = f"https://www.hngbwlxy.gov.cn/#/courseCenter/courseDetails?Id={str(course_id)}&courseType=video"
                await self.page.goto(course_url)
                await asynioc.sleep(2)
                course_status = await self.page.wait_for_selector(
                    'body > div > div:nth-child(3) > div.container_24 > div > div > div.cpurseDetail.grid_24 > div.c-d-course.clearfix > div > div.course-progress > span.progress-con.ng-binding')
                course_status = await course_status.inner_text()
                if course_status == "100.0%":
                    print(f" {course_name} 课程已学完将为您选择下一个课程！")
                    continue
                else:
                    course_play_url = f"https://www.hngbwlxy.gov.cn/#/play/play?Id={str(course_id)}"
                    await self.page.goto(course_play_url)
                    try:
                        study_status = await self.page.wait_for_selector('#ban-study', timeout=4000)
                        if study_status:
                            print("今日学习的学分已经够5分，不需要再学习了！")
                            return True
                    except:
                        print("正在自动选择下一门课程！")
                    tan_box = await self.page.wait_for_selector('#msBox > div.msBtn > span')
                    await tan_box.click()
                    check = await self.move_to_slider()
                    while check is False:
                        await self.get_captcha_position()
                        check = await self.move_to_slider()
                    print(f"{course_name} 课程开始学习！")
                    course_progress = await self.wait_for_jwplayer(
                        "#myplayer_controlbar > span.jwgroup.jwcenter > span.jwslider.jwtime > span.jwrail.jwsmooth > span.jwprogressOverflow")
                    pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=100).start()
                    while True:
                        style1 = await course_progress.get_attribute("style")
                        width1 = next(
                            (s.split(":")[1].strip() for s in style1.split(";") if
                             s.split(":")[0].strip() == "width"),
                            None)
                        await asynioc.sleep(1.5)
                        style2 = await course_progress.get_attribute("style")
                        width2 = next(
                            (s.split(":")[1].strip() for s in style2.split(";") if
                             s.split(":")[0].strip() == "width"),
                            None)
                        width_num = float(width2.strip('%'))
                        pbar.update(width_num)
                        # 0.0
                        if (width1 == width2) and width_num == 0.0:
                            pbar.finish()
                            break
                # 十秒钟不能打开另一个课程需要等待
                await self.page.goto(COURSER_LINK)
                await self.page.reload()
                await asynioc.sleep(12)

        print("当前URL下的课程已经全部学习完毕！")
        return True
