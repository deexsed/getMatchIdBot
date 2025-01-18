# Инструкция по настройке и запуску Telegram-бота

## Требования

Для работы бота требуется:
- Python 3.10.6 (более новые версии, скорее всего, будут работать, но насчет более старых версий уверенности нет).
- pip 24.3.1 (аналогично, более новые версии должны работать).
- Библиотеки, указанные в файле `requirements.txt`.

## Установка репозитория с GitHub

Чтобы установить проект на свой компьютер, выполните следующие шаги:

1. **Убедитесь, что у вас установлен Git**:
   - Если Git не установлен, скачайте и установите его с [официального сайта](https://git-scm.com/).
   - Проверьте установку, выполнив в терминале команду:
     ```bash
     git --version
     ```

2. **Клонируйте репозиторий**:
   - Откройте терминал и перейдите в папку, куда вы хотите скопировать проект.
   - Выполните команду:
     ```bash
     git clone https://github.com/ваш-username/ваш-репозиторий.git
     ```
   - Замените `ваш-username` и `ваш-репозиторий` на соответствующие значения.

3. **Перейдите в папку проекта**:
   - После клонирования перейдите в папку проекта:
     ```bash
     cd ваш-репозиторий
     ```

4. **Установите зависимости**:
   - Установите необходимые пакеты, выполнив команду:
     ```bash
     pip install -r requirements.txt
     ```

Теперь проект готов к настройке и запуску.

## Регистрация бота в Telegram через BotFather

Чтобы зарегистрировать бота в Telegram, выполните следующие шаги:

1. **Откройте Telegram**: Запустите приложение Telegram на вашем устройстве.
2. **Найдите BotFather**:
   - В строке поиска введите `@BotFather`.
   - Выберите BotFather из списка результатов (у него будет синяя галочка, подтверждающая, что это официальный бот).
3. **Запустите BotFather**:
   - Нажмите кнопку «START» или введите команду `/start`.
4. **Создайте нового бота**:
   - Введите команду `/newbot` и отправьте её.
5. **Укажите имя бота**:
   - Вам будет предложено ввести имя для вашего бота. Это имя будет отображаться в чатах и контактах.
6. **Придумайте уникальный юзернейм**:
   - После этого вам нужно будет придумать юзернейм для бота, который должен заканчиваться на «bot» (например, `MyFirstBot`). Юзернейм должен состоять только из латинских букв и цифр, а также быть уникальным.
7. **Получите токен**:
   - После успешной регистрации BotFather предоставит вам токен API, который нужен для работы с ботом. Сохраните его в безопасном месте, так как он будет использоваться для авторизации вашего бота.

## Настройка и запуск бота

Для начала работы выполните следующие шаги:

1. **Установите необходимые пакеты**:
   - В консоли введите команду:
     ```bash
     pip install -r requirements.txt
     ```
   - Дождитесь окончания установки всех пакетов.

2. **Настройте файл `heroes.json`**:
   - В файле `heroes.json` укажите необходимых героев. Они будут отображаться у пользователя при вводе героя. В названии можно указать что угодно.

   <div align="center">
     <img src="https://github.com/user-attachments/assets/49df6383-2c11-4c30-b489-059aa66cc1c0" alt="Пример heroes.json" width="500">
     <br>
     <em>Пример содержимого файла heroes.json</em>
   </div>

   <div align="center">
     <img src="https://github.com/user-attachments/assets/2840598b-7da7-4b04-b0fc-d476ba43d987" alt="Пример отображения героев" width="500">
     <br>
     <em>Пример отображения героев у пользователя</em>
   </div>

3. **Настройте файл `config.py`**:
   - В файле `config.py` укажите токен бота, полученный от @BotFather.

   <div align="center">
     <img src="https://github.com/user-attachments/assets/aa5a1b9e-e31c-428c-9d4a-1d46e1bed491" alt="Пример config.py" width="500">
     <br>
     <em>Пример содержимого файла config.py</em>
   </div>

4. **Запустите бота**:
   - Запустите файл `start_bot.bat` для начала работы бота.

5. **Получение статистики матчей**:
   - После записи первого матча в папке проекта появится файл `matchStat.xlsx`. В нем будут находиться все полученные номера матчей.

6. **Наслаждайтесь**:
   - Теперь вы можете использовать бота и наслаждаться его функционалом!

## Удаление установленных пакетов

Если вы хотите удалить установленные пакеты, выполните следующую команду в терминале:

```bash
pip uninstall -y -r requirements.txt
```

---

**Примечание**: Убедитесь, что все шаги выполнены корректно, чтобы бот работал без ошибок. Если возникнут проблемы, проверьте, правильно ли вы указали токен и установили все необходимые библиотеки.
