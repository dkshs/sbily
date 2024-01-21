#!/bin/zsh

# Loading colors
autoload -U colors
colors

# # To do the migrations
# python manage.py migrate

echo "$bold_color$fg[green]Application started${reset_color}"
echo "$bold_color$fg[yellow]Access: http://localhost:8080/ \n${reset_color}"

python manage.py runserver 0.0.0.0:8080
