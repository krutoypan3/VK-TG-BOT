import Func

func_answer = {'курс': Func.curs_value,
               'валюта': Func.curs_value,
               'доллар': Func.curs_value,
               'евро': Func.curs_value,
               'eur': Func.curs_value,
               'usd': Func.curs_value,
               'погода': Func.weather,
               'как скачать?': Func.how_download,
               'как отправить?': Func.how_unload}
file_answer = {
    'мои файлы': '',
    'аудио': 'audio/',
    'документы': 'document/',
    'граффити': 'graffiti/',
    'фото': 'photo/',
    'видео': 'video/',
    'гс': 'voice/'
}
smile_list = {
    'audio/': '&#127925;',
    'photo/': '&#128247;',
    'video/': '&#127916;',
    'document/': '&#128190;',
    'graffiti/': '&#127912;',
    '': '',
    'voice/': '&#127908;'
}

keyboard = {
    'главная': Func.main_keyboard,
    'мои файлы': Func.my_files_keyboard,
    'аудио': Func.my_files_keyboard_content,
    'документы': Func.my_files_keyboard_content,
    'граффити': Func.my_files_keyboard_content,
    'фото': Func.my_files_keyboard_content,
    'видео': Func.my_files_keyboard_content,
    'гс': Func.my_files_keyboard_content
}
