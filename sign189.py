# -*- coding: utf8 -*-

import requests
import lxml
import codecs
import time
from PIL import Image


class Auto189Sign(object):
    PHONE_USER = 2000004
    BROAD_BAND_USER = 1
    LOGON_POST_URL = r'http://js.189.cn/self_service/validateLogin.action'
    CHECK_CODE_URL = r'http://js.189.cn/rand.action'
    LOGON_URL = r'http://js.189.cn/self_service/validateLoginNew.action?favurl=http://js.189.cn/index'

    headers = {
        'Host': 'js.189.cn',
        'Origin': 'http://js.189.cn',
        'Referer': 'http://js.189.cn/self_service/validateLogin.action',
        'Upgrade-Insecure-Requests': 1,
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    }

    def __init__(self, user, password, user_type):
        self.user = user
        self.password = password
        self.user_type = user_type
        if user_type not in [self.PHONE_USER, self.BROAD_BAND_USER]:
            print('Invalid user type !!!')
        self.__init_http_session()
        self.__get_session_cookie_from_server()

    def __init_http_session(self):
        self.session = requests.Session()
        self.session.headers['User-Agent'] = self.headers['User-Agent']
        res = self.session.get(self.LOGON_URL)
        self.__print_cookie(res.cookies)
        if not res.ok:
            print('Request failed, ' + res.reason)
        # print res.text

    def __get_session_cookie_from_server(self):
        url = r'http://js.189.cn/user_getSessionInfoforCookie.action'
        res = self.session.post(url, headers={'Content-Type':'application/json;charset=UTF-8'})
        print res.content

    def __get_check_code_manually(self):
        print("Tell me what is current check code ?")
        res = self.session.get(self.CHECK_CODE_URL)
        self.__print_cookie(res.cookies)

        if not res.ok:
            print('get check code image failed, ' + res.reason)
            return None

        image_name = 'checkcode.jpg'
        with open(image_name, 'wb') as f:
            f.write(res.content)

        image = Image.open(image_name)
        image.show()
        image.close()

        while 1:
            code = raw_input("Check code: ").strip()
            if code and len(code) == 4:
                print("Your input is: " + code)
                return code
            else:
                print('Invalid check code !')

    def logon(self):
        post_data = {
            'logonPattern': '1',
            'areaCode':'025',
            'userType':'2000004',
            'validateCode': 'gfwu',
            'qqNum': '',
            'newTargetUrl': 'http://js.189.cn/service',
            'newUamType': '-1',
            'productId': '18021541225',
            'userPwd': '841130',
            'bandValidateCode': 'gfwu'
        }

        check_code = self.__get_check_code_manually()
        if not check_code:
            return False
        post_data['validateCode'] = check_code
        post_data['validate'] =check_code

        res = self.session.post(self.LOGON_POST_URL, data=post_data)
        print('Logon result: {}, {}'.format(res.ok, res.reason))
        self.__print_cookie(res.cookies)
        self.__save_response(res, 'logon_result.html')

        if u'验证码错误，请重新输入' in res.text:
            print(u'!!!! 验证码错误, logon failed !!!!!')
            return False
        else:
            print('----- Logon success -----')

    @staticmethod
    def __save_response(res, name):
        with codecs.open(name, encoding='utf8', mode='w') as f:
            f.write(res.text)

    @staticmethod
    def __print_cookie(cookies):
        print('current cookies is:')
        for k, v in cookies.iteritems():
            print(' * {}:{}'.format(k, v))

    def sign(self):
        # url = r'http://js.189.cn/service/credit?in_cmpid=home-rfc-jfqd'
        # res = self.session.get(url)

        # query_url = r'http://js.189.cn/service/infoQuery_canGetIntegral.action'
        sign_url = r'http://js.189.cn/service/infoQuery_integralSign.action'
        referer = r'http://js.189.cn/service/credit?in_cmpid=home-rfc-jfqd'
        res = self.session.post(sign_url, headers={'Referer':referer})
        self.__print_cookie(res.cookies)
        self.__save_response(res, 'sign_result.html')


if __name__ == '__main__':
    user = raw_input('Input user name:')
    password = raw_input('Input password:')
    sign_proxy = Auto189Sign(user, password, Auto189Sign.BROAD_BAND_USER)
    sign_proxy.logon()
    while 1:
        sign_proxy.sign()
        time.sleep(300)
