import Func

func_answer = {'курс': Func.curs_value,
               'валюта': Func.curs_value,
               'доллар': Func.curs_value,
               'евро': Func.curs_value,
               'eur': Func.curs_value,
               'usd': Func.curs_value,
               'погода': Func.weather,
               'как скачать?': Func.how_download,
               'как отправить?': Func.how_unload,
               'онгоинги': Func.AnimeGo_Ongoings,
               'онгоинг': Func.AnimeGo_Ongoings,
               'выходит': Func.AnimeGo_Ongoings,
               'что выходит': Func.AnimeGo_Ongoings,
               'онг': Func.AnimeGo_Ongoings,
               'случайное аниме': Func.AnimeGo_Finish,
               'посоветуй аниме': Func.AnimeGo_Finish,
               'посоветуй фильм': Func.Film_popular,
               'фильм': Func.Film_popular,
               'популярный фильм': Func.Film_popular,
               'популярные фильмы': Func.Film_popular,
               'популярное': Func.Film_popular}
func_answer_more_word = {'коронавирус': Func.covid,
                         'погода': Func.weather}

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
