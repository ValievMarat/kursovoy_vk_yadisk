import requests
from datetime import datetime
from pprint import pprint
import json

class VkApi:
    def __init__(self):
        with open('token_vk.txt') as file:
            self.token = file.read()
        self.params = {'access_token': self.token,
                       'v': '5.131'}

    def get_photos_profile(self, id, max_count=5):
        dict_photos = {}

        params = {'owner_id': id,
                  'album_id': 'profile',
                  'extended': True,
                  'photo_sizes': True,
                  'count': max_count}

        params.update(self.params)
        response = requests.get('https://api.vk.com/method/photos.get', params=params)
        if response.status_code != 200:
            return f'Error: status: {response.status_code}'

        dict_response = response.json()
        for dict_images in dict_response['response']['items']:
            max_size = 0
            max_image_index = None
            for index, dict_size in enumerate(dict_images['sizes']):
                size = dict_size['height'] * dict_size['width']
                if size > max_size:
                    max_size = size
                    max_image_index = index

            file_name = str(dict_images['likes']['count'])
            if dict_photos.get(file_name) is not None:
                date = datetime.utcfromtimestamp(dict_images['date'])
                file_name += '_' + date.strftime('%Y_%m_%d')

            dict_info = {'url': dict_images['sizes'][max_image_index]['url'],
                         'size': dict_images['sizes'][max_image_index]['type'],
                         'file_name': f'{file_name}.jpg'}

            dict_photos[file_name] = dict_info

        return list(dict_photos.values())


class YaDisk:
    def __init__(self):
        with open('token_yadisk.txt') as file:
            self.token = file.read()

    def __load_public_file(self, file_info: dict, folder_name: str):
        url = 'https://cloud-api.yandex.net:443/v1/disk/resources/upload'

        headers = {'Authorization': f'OAuth {self.token}', 'Content-Type': 'Application/json'}
        # params = {'path': folder_name + '/' + file_info['file_name'],
        #           'overwrite': True}
        # resp = requests.get(url, params=params, headers=headers)
        # if resp.status_code != 200:
        #     return f'Ошибка получения ссылки: статус {resp.status_code}: {resp.json()["message"]}'
        # href = resp.json()['href']

        params = {'path': folder_name + '/' + file_info['file_name'],
                  'url': file_info['url'],
                  'overwrite': True}
        resp = requests.post(url, params=params, headers=headers)
        if resp.status_code != 202 and resp.status_code != 200:
            return f'Ошибка загрузки: статус {resp.status_code}: {resp.json()["message"]}'

        return 'Ok'

    def load_public_files(self, list_files: list, folder_name: str = 'Загрузки'):
        list_json = []

        # создадим папку, в случае её отсутствия
        url = 'https://cloud-api.yandex.net:443/v1/disk/resources'

        headers = {'Authorization': f'OAuth {self.token}',
                   'Content-Type': 'Application/json',
                   'Accept': 'application/json'}
        params = {'path': folder_name}
        resp = requests.put(url, params=params, headers=headers)
        if resp.status_code != 201 and resp.status_code != 409:
            print(f'Ошибка создания папки: статус {resp.status_code}: {resp.json()["message"]}')
            return

        count_files = len(list_files)
        for index, file_info in enumerate(list_files):
            print(f'Загрузка файла {index + 1} из {count_files}')
            result = self.__load_public_file(file_info, folder_name)
            if result != 'Ok':
                print(result)
                return
            dict_info = {'file_name': file_info['file_name'],
                         'size': file_info['size']}
            list_json.append(dict_info)

        with open('result.json', 'w', encoding='utf-8') as file:
            json.dump(list_json, file, ensure_ascii=False, indent=2)

        print('Загрузка успешно завершена')


def load_pictures_from_vk(vk_id: str, folder_name: str = 'Загрузки', max_count: int = 5):
    vk = VkApi()
    list_photos = vk.get_photos_profile(vk_id, max_count)
    if isinstance(list_photos, str):
        print(list_photos)
        return
    ya_disk = YaDisk()
    ya_disk.load_public_files(list_photos, folder_name)


if __name__ == '__main__':
    test_id = '59671091'
    load_pictures_from_vk(test_id, 'Фото тест ВК', 10)
