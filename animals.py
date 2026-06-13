# База данных обитателей зоопарка
ZOO_INHABITANTS = {
    "tiger": {
        "title": "Амурский тигр",
        "bio": "Сильный и самостоятельный хищник, предпочитающий уединение. Тигр — гордость дикой природы.",
        "photo": "tiger.jpg",
        "sponsor_link": "Оформить опекунство: https://moscowzoo.ru/animals/kinds/amurskiy_tigr"
    },
    "polar_bear": {
        "title": "Белый медведь",
        "bio": "Выносливый северный житель, не боящийся лютых морозов. Настоящий странник Арктики.",
        "photo": "polar_bear.jpg",
        "sponsor_link": "Подробнее об опеке: https://moscowzoo.ru/animals/kinds/belyy_medved"
    },
    "meerkat": {
        "title": "Сурикат",
        "bio": "Компанейский и внимательный зверёк, который всегда предупредит семью об опасности.",
        "photo": "meerkat.jpg",
        "sponsor_link": "Вступить в программу: https://moscowzoo.ru/animals/kinds/surikat"
    },
    "flamingo": {
        "title": "Фламинго",
        "bio": "Элегантная яркая птица, обожающая быть в эпицентре событий. Душа любой компании.",
        "photo": "flamingo.jpg",
        "sponsor_link": "Поддержать зоосад: https://moscowzoo.ru/animals/kinds/rozovyy_flamingo"
    },
    "elephant": {
        "title": "Азиатский слон",
        "bio": "Мудрый и степенный великан, трепетно заботящийся о родных. Символ семейного тепла.",
        "photo": "elephant.jpg",
        "sponsor_link": "Стать попечителем: https://moscowzoo.ru/animals/kinds/aziatskiy_slon"
    },
    "snow_leopard": {
        "title": "Снежный барс (ирбис)",
        "bio": "Таинственный горный житель, привыкший к высоте и одиночеству. Легендарный дух вершин.",
        "photo": "snow_leopard.jpg",
        "sponsor_link": "Сохранить исчезающий вид: https://moscowzoo.ru/animals/kinds/irbis_snezhnyy_bars"
    }
}

# Список идентификаторов для быстрого доступа
AVAILABLE_SPECIES = list(ZOO_INHABITANTS.keys())