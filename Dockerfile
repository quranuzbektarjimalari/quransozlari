FROM php:8.2-cli

# curl o'rnatish
RUN apt-get update && apt-get install -y curl unzip

# bot.php faylini konteynerga nusxalash
COPY . /usr/src/myapp
WORKDIR /usr/src/myapp

CMD ["php", "bot.php"]
