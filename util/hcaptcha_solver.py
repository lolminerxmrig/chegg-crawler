import sys
import os
from twocaptcha import TwoCaptcha


def solver(sitekey, url):
    api_key = os.getenv('APIKEY_2CAPTCHA', '6c454182b70bdb7d4129eadee5e7e6ca')

    solver = TwoCaptcha(api_key)

    try:
        result = solver.hcaptcha(
            sitekey='4593ff08-59a2-4c32-b0d6-04d69deb3895',
            url='https://homeworkify.net/',
        )

    except Exception as e:
        sys.exit(e)

    else:
        # print(str(list(result.values())[1]))

        return str(list(result.values())[1])


if __name__ == '__main__':
    solver("4593ff08-59a2-4c32-b0d6-04d69deb3895", "https://homeworkify.net/")
