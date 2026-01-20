import abc

from core.util import save_info, get_info


class Information(abc.ABC):
    @abc.abstractmethod
    def load_info(self):
        pass

    @abc.abstractmethod
    def write_info(self):
        pass
    @abc.abstractmethod
    def modify_info(self, arg1, arg2, arg3=None, arg4=None):
        pass
    @abc.abstractmethod
    def check_info_empty(self):
        pass
    @abc.abstractmethod
    def show_info(self)->str:
        pass


payer_info_path = "data/payer_info.json"
vpn_info_path = "data/vpn_info.json"
charge_info_path = "data/charge_info.json"


class Payer(Information):
    username: str
    password: str

    def __init__(self):
        """read and load info from file"""
        self.username = ""
        self.password = ""
        self.load_info()

    def write_info(self):
        user_data = {
            "username": self.username,
            "password": self.password,
        }
        save_info(payer_info_path, user_data)
        print(f"单个用户 {self.username} 已保存！")


    def load_info(self):
        user_data = get_info(payer_info_path)
        if user_data is None:
            return
        self.username = user_data["username"] or ""
        self.password = user_data["password"] or ""

    def modify_info(self, arg1, arg2, arg3=None, arg4=None):
        self.username = arg1
        self.password = arg2

    def check_info_empty(self):
        return self.username == "" or self.password == ""
    def show_info(self)->str:
        return f"付费账户为{self.username}"




class VpnUser(Information):


    username: str
    password: str

    def __init__(self):
        """read and load info from file"""
        self.username = ""
        self.password = ""
        self.load_info()

    def load_info(self):
        user_data = get_info(vpn_info_path)
        if user_data is None:
            return
        self.username = user_data["username"] or ""
        self.password = user_data["password"] or ""

    def write_info(self):
        user_data = {
            "username": self.username,
            "password": self.password,
        }
        save_info(vpn_info_path, user_data)

    def modify_info(self, arg1, arg2, arg3=None, arg4=None):
        self.username = arg1
        self.password = arg2

    def check_info_empty(self):
        return self.username == "" or self.password == ""
    def show_info(self)->str:
        return f"当前VPN默认登陆账户: {self.username}"



class ChargeInfo(Information):
    building_name:str
    building_code: str
    room: str
    amount: int
    charge_data:dict

    def __init__(self):
        """read and load info from file"""
        self.building_name = ""
        self.building_code = ""
        self.room = ""
        self.amount = 0
        self.load_info()

    def load_info(self):
        charge_data = get_info(charge_info_path)
        if charge_data is None:
            return
        self.building_name = charge_data["building_name"]
        self.building_code = charge_data["building_code"]
        self.room = charge_data["room"]
        self.amount = charge_data["amount"]
    def write_info(self):
        charge_data = {
            "building_name": self.building_name,
            "building_code": self.building_code,
            "room": self.room,
            "amount": self.amount,
        }
        save_info(charge_info_path, charge_data)

    def modify_info(self, arg1, arg2, arg3=None, arg4=None):
        self.building_name = arg1
        self.building_code = arg2
        self.room = arg3
        self.amount = arg4

    def check_info_empty(self):
        return self.building_code == "" or self.room == "" or self.amount == 0
    def show_info(self)->str:
        return f"充值房间:{self.building_name},{self.room},默认充值度数:{self.amount}"


class InfoManger:

    def __init__(self):
        self.charge_info = ChargeInfo()
        self.vpn_info = VpnUser()
        self.payer_info = Payer()

    def check_info_empty(self):
        return self.charge_info.check_info_empty() or self.vpn_info.check_info_empty() or self.payer_info.check_info_empty()

    def modify_info(self, choice, str1, str2, str3 = None, str4=None):
        if choice == 1:
            self.charge_info.modify_info(str1, str2, str3, str4)
            self.charge_info.write_info()
        elif choice == 2:
            self.vpn_info.modify_info(str1, str2, str3, str4)
            self.vpn_info.write_info()
        else:
            self.payer_info.modify_info(str1, str2, str3, str4)
            self.payer_info.write_info()
    def query_info(self,choice)->str:
        if choice == 1:
            return self.vpn_info.show_info() + '\n\n'
        elif choice == 2:
            return self.payer_info.show_info() + '\n\n'
        else:
            return self.charge_info.show_info() + '\n\n'


