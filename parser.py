import os
import re
import base64
import socket
import urllib.request
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Константы настроек
METADATA = """# Название: 🍟improved-potatoVPN
# Безлимит без ограничений 
# Ссылка на бота: потом уставлю
# Реклама тгк: Мой ТГК потом вставлю 2

"""

def ping_host(host, port, timeout=2):
    """Простая TCP проверка доступности (пинг)"""
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, int(port)))
        s.close()
        return True
    except Exception:
        return False

def parse_config(config_str):
    """Извлекает хост и порт из vless ссылки для проверки"""
    try:
        if not config_str.startswith("vless://"):
            return None
        # Простой парсинг строки
        parts = config_str.split("@")
        if len(parts) < 2: return None
        host_port_part = parts[1].split("?")[0].split("#")[0]
        if ":" in host_port_part:
            host, port = host_port_part.split(":")
        else:
            host, port = host_port_part, 443
        return host, port
    except:
        return None

def rename_and_format(config_str, index):
    """Меняет имя конфигурации (после знака #)"""
    try:
        parsed = urlparse(config_str)
        query = parse_qs(parsed.query)
        new_name = f"🍀improvedVPN [{index}]"
        
        # Пересобираем URL с новым фрагментом (именем)
        new_url = urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, urlencode(query, doseq=True), new_name
        ))
        return new_url
    except:
        return config_str

def process_sources():
    os.makedirs("configs", exist_ok=True)
    if not os.path.exists("sources.txt"):
        with open("sources.txt", "w") as f: f.write("")
        print("Создан пустой файл sources.txt. Добавьте туда ссылки.")
        return

    with open("sources.txt", "r") as f:
        sources = [line.strip() for line in f if line.strip()]

    all_files_performance = []

    for src_idx, source in enumerate(sources):
        try:
            req = urllib.request.Request(source, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8')
        except Exception as e:
            print(f"Ошибка при скачивании {source}: {e}")
            continue

        # Собираем только vless конфигурации
        configs = [line.strip() for line in content.splitlines() if line.strip().startswith("vless://")]
        if not configs:
            continue

        # Разбиваем на части по 200 штук
        chunk_size = 200
        for chunk_idx, i in enumerate(range(0, len(configs), chunk_size)):
            chunk = configs[i:i + chunk_size]
            file_configs = []
            valid_count = 0

            for item_idx, config in enumerate(chunk):
                global_idx = i + item_idx + 1
                formatted_config = rename_and_format(config, global_idx)
                file_configs.append(formatted_config)
                
                # Проверка пинга
                net_info = parse_config(config)
                if net_info and ping_host(net_info[0], net_info[1]):
                    valid_count += 1

            # Формируем имя файла
            filename = f"configs/source_{src_idx + 1}_part_{chunk_idx + 1}.txt"
            
            # Запись в файл с метаданными
            with open(filename, "w", encoding="utf-8") as f:
                f.write(METADATA)
                f.write("\n".join(file_configs))

            # Считаем "качество" файла по проценту живых конфигов
            success_rate = valid_count / len(chunk) if chunk else 0
            all_files_performance.append((filename, success_rate))

    # Выявляем 2 лучших файла
    all_files_performance.sort(key=lambda x: x[1], reverse=True)
    best_files = all_files_performance[:2]

    # Сохраняем ссылки на них в закодированном Base64 виде
    # Предполагается базовый URL вашего GitHub Pages (изменится автоматически при работе)
    repo_owner = os.getenv("GITHUB_REPOSITORY_OWNER", "username")
    repo_name = os.getenv("GITHUB_REPOSITORY", "repo").split("/")[-1]
    base_url = f"https://{repo_owner}.github.io/{repo_name}/"

    best_urls_content = ""
    for file_path, _ in best_files:
        best_urls_content += f"{base_url}{file_path}\n"

    # Кодируем результат в base64
    b64_content = base64.b64encode(best_urls_content.encode('utf-8')).decode('utf-8')
    with open("best_configs.txt", "w", encoding="utf-8") as f:
        f.write(b64_content)

if __name__ == "__main__":
    process_sources()
