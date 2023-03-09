# recipe-api
API for recipes on django rest framework
![image](https://user-images.githubusercontent.com/84863764/206945685-dd6e6c15-7f48-41a5-b48e-adae60abbe3e.png)

___

### Развертывание

1. Склонировать репозиторий:
   ```
   git clone https://github.com/Dana299/recipe-api.git && cd recipe-api
   ```

2. Создать `.env` файл по образцу `.env.example`. Понадобятся учетные данные для сервисного аккаунта в Yandex Cloud.

3. Поднять контейнеры
    ```
    docker-compose up
    ```

4. Перейти на страницу с документацией http://localhost:8000/swagger