# suep-core, A core for students at Shanghai University of Electric Power.
#
# Copyright (c) 2024 zhengxyz123
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from bs4 import BeautifulSoup
from requests import HTTPError

from core import auth
from core.util import AuthServiceError


@dataclass
class MeterState:
    """电表状态。"""

    recharges: int
    reskwh: float
    power: int
    voltage: int
    power_factor: float
    limit: int
    state: int


@dataclass
class RechargeInfo:
    """充值信息。"""

    oid: int
    type: str
    money: float
    quantity: int
    time: datetime


class ElectricityManagement:
    """能源管理。"""

    home_url = "http://10.50.2.206"
    meter_state_url = "http://10.50.2.206/api/charge/query"
    recharge_info_url = "http://10.50.2.206/api/charge/user_account"
    recharge_url = "http://10.50.2.206/api/charge/Submit"
    get_room_url = "http://10.50.2.206/api/charge/GetRoom"

    def __init__(self, session) -> None:
        self._session = session
        # if not test_network():
        #     raise VPNError(
        #         "you are not connected to the campus network, please turn on vpn"
        #     )
        response = self._session.get(self.home_url, allow_redirects=True)
        response.raise_for_status()
        dom = BeautifulSoup(response.text, features="html.parser")

        if len(dom.select("div[class=auth_page_wrapper]")) > 0:
            raise AuthServiceError("must login first")

    @property
    def meter_state(self) -> MeterState:
        """获取电表状态。"""
        response = self._session.get(
            self.meter_state_url, params={"_dc": int(time.time())}
        )
        response.raise_for_status()
        data = response.json()

        if not data["success"]:
            raise ValueError("api returned an error")
        recharges = int(data["info"][0]["recharges"])
        reskwh = float(data["info"][0]["reskwh"])
        power = int(data["info"][0]["P"])
        voltage = int(data["info"][0]["U"])
        power_factor = float(data["info"][0]["FP"])
        limit = int(data["info"][0]["limit"])
        state = int(data["info"][0]["state"])
        return MeterState(recharges, reskwh, power, voltage, power_factor, limit, state)

    @property
    def recharge_info(self) -> Iterable[RechargeInfo]:
        """获取历次的电表充值账单。"""
        response = self._session.get(
            self.recharge_info_url, params={"_dc": int(time.time())}
        )
        response.raise_for_status()
        data = response.json()

        if not data["success"]:
            raise ValueError("api returned an error")
        for info in data["info"]:
            oid = int(info["oid"])
            recharge_type = info["type"]
            money = float(info["money"])
            quantity = int(info["quantity"])
            recharge_time = datetime.fromisoformat(info["datetime"])
            yield RechargeInfo(oid, recharge_type, money, quantity, recharge_time)

    def recharge(self, building: str, room: str, kwh: int) -> None:
        """充值电费。"""
        response = self._session.post(
            self.recharge_url,
            params={"_dc": int(time.time())},
            data={"building": building, "room": room, "kwh": kwh},
        )
        response.raise_for_status()
        data = response.json()

        if not data["success"]:
            raise ValueError(data["info"])

    def recharge_my_room(self, kwh: int) -> None:
        """给自己的宿舍充值电费。"""
        response = self._session.get(
            self.get_room_url, params={"_dc": int(time.time())}
        )
        response.raise_for_status()
        data = response.json()

        if not data["success"]:
            raise ValueError("api returned an error")
        self.recharge(data["info"][0]["building"], data["info"][0]["room"], kwh)



def login_service(username, password, proxy_config=None, site = "http://10.50.2.206:80/"):

    """执行登陆，然后返回service对象"""

    # service 必须与下面一行所展示的精确相符，都为 22 个字符！
    service = auth.AuthService(username, password, proxy_config=proxy_config, service=site, renew="true")
    # 是否需要输入验证码？
    if service.need_captcha():
        # 获取并保存验证码:
        with open("captcha.jpg", "wb") as captcha_image:
            captcha_image.write(service.get_captcha_image())
        # 填写验证码:
        service.set_captcha_code("验证码")
    # 登陆:
    try:
        service.login()
    except HTTPError as e:
        print(e)
    return service

def pay_electricity(username, password, building_code, room, amount, proxy_config=None, delay = 3)->RechargeInfo:
    """根据房间号和金额充值电费以及用户，并返回充值信息"""
    service = login_service(username, password, proxy_config)
    time.sleep(delay)
    em = ElectricityManagement(service.session)
    # 充值电费
    em.recharge(building_code, room, amount)
    # 获取历次的电表充值账单：
    all_payments = list(em.recharge_info)
    service.logout()
    return all_payments[0]

__all__ = ("ElectricityManagement",)