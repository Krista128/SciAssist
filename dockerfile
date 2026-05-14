FROM python:3.13

RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    python3-dev \
    libyaml-dev \
    xvfb \
    # КЛЮЧЕВОЕ: добавляем недостающую библиотеку
    libxcb-cursor0 \
    # Остальные библиотеки
    libxkbcommon-x11-0 \
    libxkbfile1 \
    libxcb1 \
    libxext6 \
    libxrandr2 \
    libdbus-1-dev \
    libegl1-mesa-dev \
    libopengl0 \
    libxkbcommon0 \
    libnspr4 \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libglib2.0-0 \
    libgtk-3-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libx11-6 \
    libx11-xcb1 \
    x11-utils \
    # Добавляем утилиту для отладки на всякий случай
    ldd \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt отдельно для кэширования слоев Docker
COPY requirements.txt /SciAssist/
WORKDIR /SciAssist

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной проект
COPY . /SciAssist/

# Переменные окружения для Qt
ENV QT_DEBUG_PLUGINS=0 
ENV QT_QPA_PLATFORM=offscreen  

# Исправленная команда запуска
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & export DISPLAY=:99 && python app.py"]