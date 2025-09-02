import requests
import asyncio

url = "https://www.hngbwlxy.gov.cn/api/Page/CourseList"

headers = {
    'Connection': 'close',
    'sec-ch-ua': '";Not A Brand";v="99", "Chromium";v="88"',
    'Accept': 'application/json, text/plain, */*',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Origin': 'https://www.hngbwlxy.gov.cn',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.hngbwlxy.gov.cn/',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cookie': ''
}

data = {
    'page': '1',
    'rows': '9',
    'sort': 'Sort',
    'order': 'desc',
    'courseType': '',
    'channelId': '975',
    'title': '',
    'titleNav': '课程中心',
    'wordLimt': '35',
    'teacher': '',
    'flag': 'all',
    'isSearch': '0',
    'channelCode': '',
    'isImportant': ''
}


async def Get_course_id(cookie: str, channel_id: str, rowlength: str, page_num: int):
    headers['Cookie'] = cookie
    data['channelId'] = channel_id
    data['rows'] = rowlength
    data['page'] = str(page_num)
    response = requests.post(url, headers=headers, data=data)
    ListData = response.json()['Data']['ListData']
    course_messages = []
    for course in ListData:
        course_message = {}
        id = course["Id"]
        name = course["Name"].strip()
        course_message[id] = name
        course_messages.append(course_message)
    return course_messages
