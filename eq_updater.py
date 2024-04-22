import json
import yandex_session
from preset import presets
import asyncio
import os
import json
from aiohttp import ClientSession

CFG_PATH = f"{os.environ.get('HOME')}/.yadata"

class YandexStationEqUpdater():
    def __init__(self, session: yandex_session.YandexSession):
        self.yasess = session

    def set_device(self, dev):
        self.device = dev

    async def pick_device(self):
        r = await self.get_devices_list()
        if not r:
            print("Failed to get devices list")
            return None
        
        if len(self.devices) == 0:
            print("Нет доступных поддерживаемых устройств!")
            return None
        
        if len(self.devices) == 1:
            dev = self.devices[0]
            print(f"Выбрана {dev['name']}")
            self.device = dev
            return dev

        print("Выберите устройство:")
        for device in self.devices:
            print(f"{self.devices.index(device)} - {device['name']}")
        
        picked_str = input('Число> ')
        picked = int(picked_str)
        self.device = self.devices[picked]
        return self.devices[picked]
    
    async def pick_cfg(self):
        prsts = []
        for pr in presets:
            if pr['device'] != self.device['platform']:
                continue
            prsts.append(pr)

        if len(prsts) == 1:
            preset = prsts[0]
            print(f"Выбран пресет {preset['author']} - {preset['description']}")
            self.preset = preset
            return True
        
        print("Выберите пресет:")
        for preset in prsts:
            print(f"{prsts.index(preset)}: {preset['author']} - {preset['description']}")

        picked_str = input('Число> ')
        picked = int(picked_str)
        self.preset = prsts[picked]
        return True

    async def send_cfg(self):
        r = await self.yasess.post(f"https://iot.quasar.yandex.ru/m/v3/user/devices/{self.device['did']}/configuration/quasar", data=json.dumps({
            "config": self.cfg,
            "version": self.cfg_ver,
        }), headers={"Content-Type": "application/json; charset=utf-8"})
        if r.status != 200:
            print(f"{r.status}: {await r.text()}")
            return False

        return True
    

    async def get_devices_list(self):
        r = await self.yasess.get(f"https://iot.quasar.yandex.ru/m/user/devices")
        if r.status != 200:
            print(f"{r.status}: {await r.text()}")
            return False
        
        self.devices = []
        j = await r.json()

        devs = []
        for room in j['rooms']:
            for device in room['devices']:
                devs.append({**device, "room_name": room['name']})
        for device in j['speakers']:
            devs.append(device)

        plats = list(map(lambda x: x['device'], presets))

        for device in devs:
            if not str(device['type']).startswith('devices.types.smart_speaker.yandex'):
                continue

            platform = device['quasar_info']['platform']
            if platform not in plats:
                continue

            self.devices.append({
                "name": str(device['name']) + str(" (неизвестная комната)" if "room_name" not in device else f" ({device['room_name']})"),
                "did": device['id'],
                "platform": platform,
            })

        return True
        

    async def get_cfg(self):
        r = await self.yasess.get(f"https://iot.quasar.yandex.ru/m/v2/user/devices/{self.device['did']}/configuration", headers={
            "Content-Type": "application/json; charset=utf-8",
        })
        if r.status != 200:
            print(f"{r.status}: {await r.text()}")
            return False
        
        j = await r.json()
        self.cfg_ver = j["quasar_config_version"] if "quasar_config_version" in j else 3
        self.cfg = j["quasar_config"] if "quasar_config" in j else {}
        return True


    async def update_cfg(self):
        r = await self.get_cfg()
        if not r:
            print("Failed to get cfg")
            return
        self.cfg['equalizer'] = {
            "bands": self.preset['bands'],
            "active_preset_id": "custom",
            "smartEnabled": self.preset['use_room_correction'] if 'use_room_correction' in self.preset else False,
            "enabled": True
        }
        r = await self.send_cfg()
        if not r:
            print("Failed to send cfg")
            return
        print("Успешно.")

def getcfg():
    if not os.access(CFG_PATH, os.F_OK):
        return None

    with open(CFG_PATH, "r") as cfg:
        return json.loads(cfg.read())
    
def putcfg(cfgj):
    with open(CFG_PATH, "w") as cfg:
        cfg.write(json.dumps(cfgj, indent=2))

async def main():
    async with ClientSession() as http:
        sess = None
        device = None
        updater = None

        # TODO: Rewrite, this is insecure!
        saved_cfg = getcfg()
        if saved_cfg is None:
            sess = yandex_session.YandexSession(session=http)
            qr_link = await sess.get_qr()
            print(f"Отсканируйте QR по этой ссылке для входа в аккаунт: {qr_link}")
            while True:
                await asyncio.sleep(2.5)
                result = await sess.login_qr()
                if result.ok:
                    print("Вход успешен!")
                    saved_cfg = {
                        "cookie": sess.cookie,
                        "x_token": sess.x_token,
                        "music_token": sess.music_token,
                    }
                    putcfg(saved_cfg)
                    break
        else:
            sess = yandex_session.YandexSession(session=http,
                                                cookie=saved_cfg['cookie'],
                                                x_token=saved_cfg['x_token'],
                                                music_token=saved_cfg['music_token'])
            device = saved_cfg['device'] if 'device' in saved_cfg else None
            print(f"[!] Для смены аккаунта, удалите {CFG_PATH}\n")

        updater = YandexStationEqUpdater(session=sess)
        device = await updater.pick_device()
        if device == None:
            print("Не удалось выбрать устройство")
            exit(1)

        r = await updater.pick_cfg()
        if not r:
            print("Не удалось выбрать пресет")
            exit(1)

        await updater.update_cfg()
    

if __name__ == "__main__":
    asyncio.run(main())

