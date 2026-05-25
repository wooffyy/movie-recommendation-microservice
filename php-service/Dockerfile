FROM php:8.2-cli

WORKDIR /app

RUN docker-php-ext-install pdo pdo_mysql

COPY . .

EXPOSE 8080

CMD ["php", "-S", "0.0.0.0:8080"]