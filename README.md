# Parametric EQ в Яндекс.Станции

## Зачем, если есть "Дом с Алисой"?

В Станции встроен довольно неплохой Parametric EQ *(увы, только с Peaking бэндами)*, но Яндекс
просто не дает его использовать. Встроенные настройки
не дают четкого контроля над Q, частотой бэндов и
их количеством.

Этот проект дает возможность исправить это недоразумение.

## Как использовать

1. Установить Python 3
    * macOS: Установите [Homebrew](https://brew.sh), затем в терминале введите `brew install python3.8`
    * Windows: Скачайте установщик с [официального сайта](https://www.python.org/downloads/), при установке установите галочку "Установить в PATH" (это важно!)
    * Linux: В большинстве дистрибутивов уже установлен
2. Скачайте этот репозиторий и распакуйте
3. Запускаем команды поочередно в терминале / cmd
```sh
# Для установки
git clone 'https://github.com/tdrkDev/Yandex-Station-Advanced-EQ.git'
cd *перетащите в окно терминала распакованную папку*
python3 -m pip install -r requirements.txt

# Для использования
python3 eq_updater.py
```

## Как создать свой пресет
1. Скопируйте presets/sample.py в ту же папку под названием вида 'кодовоеимя_автор.py'
    * Что за кодовые имена?
        | Кодовое имя | Название |
        |-------------|----------|
        | yandexstation | Яндекс.Станция |
        | yandexstation_2 | Яндекс.Станция Макс |
        | yandexmini | Яндекс.Станция Мини |
        | yandexmini_2 | Яндекс.Станция Мини 2 |
        | yandexmicro | Яндекс.Станция Лайт |
        | yandexmidi | Яндекс.Станция 2 |
        | cucumber | Яндекс.Станция Миди |
        | chiron | Яндекс.Станция Дуо Макс |
2. Формат файла:
    ```python
    preset = {
        'author': 'имя автора',
        'description': 'описание пресета',
        'device': 'кодовое имя',
        'bands': [
            {
                "freq": частота бэнда (Гц),
                "gain": уровень (дБ, допустимы десятичные дроби),
                "width": ширина (Гц),
            },
            ...
        ]
    }
    ```
    * Как работает `width`?
        Грубо говоря, от `freq` бенда в обе стороны идет плавное снижение `gain` на расстояние, равное `width` / 2.
        
        *aka Q в Parametric EQ курильщика*
    
3. Добавляем пресет в preset.py
    * Делаем по аналогии с другими пресетами.

## Благодарности

* Спасибо проекту Яндекс.Станция для HomeAssistant за реализацию входа в аккаунт Яндекс!