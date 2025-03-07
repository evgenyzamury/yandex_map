import pprint
import sys
import os
import math
import requests
from PyQt6.QtGui import QPixmap, QMouseEvent
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QCheckBox
from PyQt6.QtCore import Qt

SCREEN_SIZE = [600, 450]

step = {
    21: 0.0001,
    20: 0.0002,
    19: 0.0003,
    18: 0.0005,
    17: 0.0008,
    16: 0.001,
    15: 0.002,
    14: 0.005,
    13: 0.008,
    12: 0.01,
    11: 0.02,
    10: 0.04,
    9: 0.08,
    8: 0.16,
    7: 0.32,
    6: 0.64,
    5: 1.28,
    4: 2,
    3: 4,
    2: 8,
    1: 16,
}


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("yandex map")
        self.ll_one = 39.563117  # Долгота
        self.ll_two = 50.198775  # Широта
        self.z = 19
        self.address_text = ''
        self.postal_code = ''
        self.map_theme = 'light'
        self.map_file = 'map.png'
        self.pt = list()
        self.getImage()
        self.initUI()
        self.setFocus()

    def getImage(self):
        server_address = 'https://static-maps.yandex.ru/v1?'
        api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'

        map_params = {
            'll': ','.join(map(str, (self.ll_one, self.ll_two))),
            'z': self.z,
            'apikey': api_key,
            'theme': self.map_theme,
            'pt': '~'.join(map(str, self.pt)),
        }
        # Готовим запрос.

        response = requests.get(server_address, map_params)

        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            print(self.z, self.ll_one, self.ll_two)
            print(map_params)
            sys.exit(1)

        # Запишем полученное изображение в файл.
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')
        self.update_image()

        self.theme_button = QPushButton(self)
        self.theme_button.resize(40, 40)
        self.theme_button.move(540, 20)
        self.theme_button.setStyleSheet("""
                   QPushButton {
                       border-radius: 20px; 
                       background-color: #e6e6e6;
                       border-width: 1px;
                       border-style: solid;
                       border-color: black;
                   }
                   QPushButton:hover {
                       background-color: #00FFFF;
                   }
               """)
        self.theme_button.clicked.connect(self.change_theme)

        self.search_edit = QLineEdit(self)
        self.search_edit.move(10, 10)
        self.search_edit.clearFocus()

        self.search_remove_button = QPushButton(self)
        self.search_remove_button.resize(30, 30)
        self.search_remove_button.move(150, 5)
        self.search_remove_button.setStyleSheet("""
                   QPushButton {
                       border-radius: 15px; 
                       background-color: lightgrey;
                       background-image: url(cansel.png);
                   }
                   QPushButton:hover {
                       background-color: grey;
                   }
               """)
        self.search_remove_button.clicked.connect(self.clear_search)

        self.label = QLabel(self)
        self.label.setStyleSheet("""QLabel{
            font-size: 14px;
            color: black;
            background-color: white;
            padding: 10px;
            border-radius: 15px; 
            border-width: 1px;
            border-style: solid;
            border-color: grey;
        }""")
        self.label.move(5, 60)
        self.label.hide()

        self.index_checkbox = QCheckBox(self)
        self.index_checkbox.move(10, 40)
        self.index_checkbox.stateChanged.connect(self.index_state)
        self.index_checkbox.hide()

    def update_image(self):
        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def mousePressEvent(self, event: QMouseEvent):
        # найдём границы дельты изменении координат с помощью геометрической прогрессии
        cords_diff = ((2 ** (22 - self.z) * 0.0001) * 2, ((85 * 2 ** (21 - self.z)) * 0.000001) * 2)

        # найдем как сильно поменяются координаты если переместиться на 1 пиксель
        x_cords_diff = cords_diff[0] / 600
        y_cords_diff = cords_diff[1] / 450

        # найдём - где произошло нажатие
        x, y = event.position().x(), event.position().y()

        # найдём центр нашего экрана
        x_center, y_center = map(lambda a: a // 2, SCREEN_SIZE)

        # разница между центром и точки касания
        diff_x = x - x_center
        diff_y = y - y_center

        # найдем координаты долготу и широту, где нажали ЛКМ
        if diff_x:
            ll_one = self.ll_one + diff_x * x_cords_diff
        else:
            ll_one = self.ll_one

        if diff_y:
            ll_two = self.ll_two - diff_y * y_cords_diff
        else:
            ll_two = self.ll_two

        if event.button() == Qt.MouseButton.LeftButton:
            self.geocoder_query(f'{ll_one},{ll_two}')
            self.getImage()
            self.image.setPixmap(QPixmap(self.map_file))
        elif event.button() == Qt.MouseButton.RightButton:
            server = 'https://search-maps.yandex.ru/v1/'
            params = {
                'apikey': 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3',  # Ваш API-ключ
                'text': 'организация',  # Ищем организации
                'lang': 'ru_RU',
                'll': f'{ll_one},{ll_two}',
                'type': 'biz',  # Тип объекта (организация)
                'results': 1,  # Количество результатов
            }
            response = requests.get(server, params=params)
            if not response:
                print(response.status_code)
                print('Ошибка поиска организации')
                return

            json = response.json()
            if not json.get('features'):
                print('Организации не найдены.')
                return

            # Получаем первую найденную организацию
            feature = json['features'][0]
            org_name = feature['properties']['name']
            org_address = feature['properties']['description']
            org_lon, org_lat = map(float, feature['geometry']['coordinates'])

            # Проверяем, что организация находится в пределах 50 метров
            if self.haversine(ll_one, ll_two, org_lon, org_lat) <= 50:
                self.geocoder_query(f'{org_lon},{org_lat}')
                self.getImage()
                self.image.setPixmap(QPixmap(self.map_file))
                self.label.setText(f'{org_name}\n{org_address}')
                self.label.show()
                self.label.adjustSize()
            else:
                self.clear_search()
                print('Организация находится за пределами 50 метров.')

    def haversine(self, lon1, lat1, lon2, lat2):
        # Радиус Земли в метрах
        R = 6371000
        # Перевод градусов в радианы
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        # Формула гаверсинуса
        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Расстояние в метрах
        return R * c

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_PageUp:
            # нажата PgUP
            self.z += 1
            if self.z > 21:
                self.z = 21
            self.getImage()
            self.image.setPixmap(QPixmap(self.map_file))

        elif event.key() == Qt.Key.Key_PageDown:
            # нажата PgDOWN
            self.z -= 1
            if self.z == 0:
                self.z = 1
            self.getImage()
            self.image.setPixmap(QPixmap(self.map_file))

        elif event.key() == Qt.Key.Key_Down:
            self.ll_two -= step[self.z]
            if self.ll_two < -90:
                self.ll_two += 180
            self.getImage()
            self.image.setPixmap(QPixmap(self.map_file))

        elif event.key() == Qt.Key.Key_Up:
            self.ll_two += step[self.z]
            if self.ll_two > 90:
                self.ll_two -= 180
            self.getImage()
            self.image.setPixmap(QPixmap(self.map_file))

        elif event.key() == Qt.Key.Key_Right:
            self.ll_one += step[self.z]
            if self.ll_one > 180:
                self.ll_one -= 360
            self.getImage()
            self.image.setPixmap(QPixmap(self.map_file))

        elif event.key() == Qt.Key.Key_Left:
            self.ll_one -= step[self.z]
            if self.ll_one < -180:
                self.ll_one += 360
            self.getImage()
            self.image.setPixmap(QPixmap(self.map_file))

        elif event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Enter - 1:  # enter = 16777221
            search = self.search_edit.text()
            if search:
                cords = self.geocoder_query(search)
                self.ll_one, self.ll_two = map(float, cords.split())
                self.getImage()
                self.image.setPixmap(QPixmap(self.map_file))
            self.search_edit.clearFocus()
            self.setFocus()

    def change_theme(self):
        if self.map_theme == 'light':
            self.map_theme = 'dark'
            self.theme_button.setStyleSheet("""
                                   QPushButton {
                                       border-radius: 20px; 
                                       background-color: black;
                                   }
                                   QPushButton:hover {
                                       background-color: lightgrey;
                                   }
                               """)
            self.label.setStyleSheet("""QLabel{
                        font-size: 14px;
                        color: white;
                        background-color: grey;
                        padding: 10px;
                        border-radius: 15px; 
                        border-width: 1px;
                        border-style: solid;
                        border-color: lightgrey;
                    }""")
        elif self.map_theme == 'dark':
            self.map_theme = 'light'
            self.label.setStyleSheet("""QLabel{
                        font-size: 14px;
                        color: black;
                        background-color: white;
                        padding: 10px;
                        border-radius: 15px; 
                        border-width: 1px;
                        border-style: solid;
                        border-color: grey;
                    }""")
            self.theme_button.setStyleSheet("""
                               QPushButton {
                                   border-radius: 20px; 
                                   background-color: #e6e6e6;
                                   border-width: 1px;
                                   border-style: solid;
                                   border-color: black;
                               }
                               QPushButton:hover {
                                   background-color: #00FFFF;
                               }
                           """)
        self.setFocus()
        self.getImage()
        self.image.setPixmap(QPixmap(self.map_file))

    def geocoder_query(self, search: str):
        search_server = 'https://geocode-maps.yandex.ru/1.x/?'
        search_params = {
            'apikey': '8013b162-6b42-4997-9691-77b7074026e0',
            'geocode': search,
            'lang': 'ru_RU',
            'format': 'json'
        }
        response = requests.get(search_server, params=search_params)
        if not response:
            print(response.status_code)
            print(search_params)
            exit(-1)
        response_json = response.json()
        # если есть результаты по нашему запросу
        if int(response_json['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData'][
                   'found']):
            toponym = response_json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            cords = toponym['Point']['pos']
            self.address_text: str = toponym['metaDataProperty']['GeocoderMetaData']['Address']['formatted']

            # расставим '/n' в полученном адресе, чтобы вместить больше текста на экране
            self.address_text = list(self.address_text)
            for i in range(50, len(self.address_text), 50):
                self.address_text.insert(i, '\n')
            self.address_text = ''.join(self.address_text)

            # если есть данные про почтовый индекс
            if "postal_code" in toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]:
                self.postal_code = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
                self.index_checkbox.show()

                if self.index_checkbox.isChecked():  # если галочка стоит добавляем почтовый индекс
                    self.label.setText(self.address_text + '\n' + self.postal_code)
                else:
                    self.label.setText(self.address_text)
            else:  # если нет данных про почтовый индекс
                self.postal_code = ''
                self.index_checkbox.hide()
                self.label.setText(self.address_text)

            self.label.show()
            self.label.adjustSize()
            self.pt.clear()
            self.pt.append(cords.replace(' ', ','))
            return cords

    def clear_search(self):
        self.pt.clear()
        self.search_edit.clear()
        self.search_edit.clearFocus()
        self.setFocus()
        self.getImage()
        self.image.setPixmap(QPixmap(self.map_file))
        self.label.hide()
        self.index_checkbox.hide()

    def index_state(self):
        if self.index_checkbox.isChecked():
            self.label.setText(self.label.text() + '\n' + self.postal_code)
        else:
            self.label.setText(self.address_text)

        self.label.adjustSize()

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
