import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

# Конфигурация сервера
hostName = "localhost"
serverPort = 8088


class MyServer(BaseHTTPRequestHandler):
    """Класс HTTP-сервера, обрабатывающий GET и POST запросы."""

    # Словарь для соответствия URL-путей и файлов на сервере
    FILE_PATHS = {
        '/': 'html_file/index.html',  # Корневой URL
        '/index.html': 'html_file/index.html',  # Главная страница
        '/category.html': 'html_file/category.html',  # Страница категорий
        '/orders.html': 'html_file/orders.html',  # Страница заказов
        '/contact.html': 'html_file/contact.html'  # Контактная страница
    }

    # Словарь типов для различных расширений файлов
    CONTENT_TYPES = {
        '.html': 'text/html',  # HTML-документы
        '.css': 'text/css',  # CSS-стили
        '.js': 'application/javascript',  # JavaScript-файлы
        '.png': 'image/png',  # PNG изображения
        '.jpg': 'image/jpeg',  # JPEG изображения
        '.jpeg': 'image/jpeg',  # Альтернативное расширение JPEG
        '.gif': 'image/gif',  # GIF изображения
        'default': 'application/octet-stream'  # Стандартный тип для неизвестных файлов
    }

    def get_content_type(self, path):
        """Определяет Content-Type файла на основе его расширения."""
        ext = os.path.splitext(path)[1].lower()  # Извлекаем расширение файла
        return self.CONTENT_TYPES.get(ext, self.CONTENT_TYPES['default'])

    def do_GET(self):
        """Обрабатывает GET-запросы. Возвращает запрошенный файл или ошибку 404."""
        # Определяем путь к файлу на основе URL
        file_path = self.FILE_PATHS.get(self.path)

        # Обработка статических файлов (CSS, JS, изображения)
        if file_path is None and (self.path.startswith('/css/') or
                                  self.path.startswith('/js/') or
                                  self.path == '/avatar.png'):
            file_path = 'html_file' + self.path.replace('/', os.sep)

        # Проверка существования файла
        if file_path is None or not os.path.exists(file_path):
            self.send_error(404, "File Not Found")
            return

        # Определяем Content-Type и является ли файл бинарным (изображением)
        content_type = self.get_content_type(file_path)
        is_binary = content_type.startswith('image/')

        # Отправляем HTTP-заголовки
        self.send_response(200)  # Код успешного ответа
        self.send_header("Content-type", content_type)
        self.end_headers()

        # Читаем и отправляем содержимое файла
        with open(file_path, 'rb' if is_binary else 'r',
                  encoding=None if is_binary else 'utf-8') as file:
            content = file.read()
            if not is_binary:
                content = content.encode('utf-8')  # Кодируем текст в bytes
            self.wfile.write(content)

    def do_POST(self):
        """Обрабатывает POST-запросы."""
        if self.path != '/contact.html':
            self.send_error(404, "Not Found")
            return

        # Получаем длину и данные формы
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')

        # Парсим данные формы
        parsed_data = parse_qs(post_data)

        # Выводим полученные данные в консоль сервера
        print("\nПолученные данные формы (раскодированные):")
        for key, value in parsed_data.items():
            print(f"{key}: {value[0]}")

        # Отправляем редирект (303 See Other) на контактную страницу
        self.send_response(303)
        self.send_header('Location', '/contact.html')
        self.end_headers()


if __name__ == "__main__":
    """Точка входа в приложение. Создает и запускает HTTP-сервер."""
    # Создаем экземпляр сервера
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print(f"Server started http://{hostName}:{serverPort}")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    # Закрываем сервер при завершении работы
    webServer.server_close()
    print("Server stopped.")