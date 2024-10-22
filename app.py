import os
from flask import Flask, render_template, request, send_file
#from flask_WTF import FlaskForm, RecaptchaField
#from wtforms import SubmitField
from PIL import Image,ImageDraw
import matplotlib.pyplot as plt
import io

app = Flask(__name__)
# загрузка исходного изображения
@app.route('/')
def index():
    return render_template('index.html')

# # настройка ключей reCAPTCHA
# app.config['RECAPTCHA_USE_SSL']=False
# app.config['RECAPTCHA_PUBLIC_KEY'] = '6LcnE2kqAAAAAL-cXOuYwT8OqgV7mGThMIRr7lWO'  # Ключ сайта
# app.config['RECAPTCHA_PRIVATE_KEY'] = '6LcnE2kqAAAAAPIhylF5cgwfAo3T_8mDAxBbnhMP'  # Секретный ключ
# app.config['RECAPTHCA_OPTIONS']={'theme':'white'}
#
# # форма с капчей
# class ReCaptchaForm(FlaskForm):
#     recaptcha = RecaptchaField()
#     submit = SubmitField('Обработать изображение')

# обработка изображения
@app.route('/process', methods=['POST'])
def process_image():
    #form = ReCaptchaForm()

    #if form.validate_on_submit():
        cell_size_percent = int(request.form['cell_size'])  # Размер клетки в %

        # открытие исходного изображения
        img = Image.open('static/input_image.jpg')
        width, height = img.size

        # вычисление размера клетки
        cell_size = int(min(width, height) * (cell_size_percent / 100))

        # создание изображения с шахматным узором
        new_img = img.copy()
        draw = ImageDraw.Draw(new_img)

        for y in range(0, height, cell_size):
            for x in range(0, width, cell_size):
                if (x // cell_size + y // cell_size) % 2 == 0:  # Черно-белый узор
                    draw.rectangle([x, y, x + cell_size, y + cell_size], fill=(0, 0, 0))

        new_img.save('static/processed_image.jpg')

        # сохранение нового изображения в память
        img_io = io.BytesIO()
        new_img.save(img_io, 'JPEG')
        img_io.seek(0)

        # построение графиков распределения цветов
        plot_color_distribution(img, new_img)

        return send_file(img_io, mimetype='image/jpeg')
    #else:
        #return render_template('index.html',form=form)

# функция для построения графика распределения цветов
import numpy as np

def plot_color_distribution(original_img, processed_img):
    # преобразрвание изображения в массив numpy
    original_data = np.array(original_img)
    processed_data = np.array(processed_img)

    # функция для построения графика
    def plot_histogram(image_data, ax, title):
        # разбивка изображение на три канала (RGB)
        red_channel = image_data[:, :, 0].flatten()
        green_channel = image_data[:, :, 1].flatten()
        blue_channel = image_data[:, :, 2].flatten()

        # построение графика для каждого канала
        ax.hist(red_channel, bins=256, color='red', alpha=0.5, label='Red channel')
        ax.hist(green_channel, bins=256, color='green', alpha=0.5, label='Green channel')
        ax.hist(blue_channel, bins=256, color='blue', alpha=0.5, label='Blue channel')
        ax.set_title(title)
        ax.legend()

    # очистка предыдущих графиков
    plt.clf()

    # создание фигур и оси для графиков
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    # построение графиков для оригинального и обработанного изображений
    plot_histogram(original_data, axes[0], 'Распределение цветов на изначальном изображении')
    plot_histogram(processed_data, axes[1], 'Распределение цветов после обработки')

    # проверка, существует ли папка "static". я не совсем понял, почему, но без неё итоговое изображение не сохранялось
    static_folder = 'static'
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)

    # cохранение графика
    plt.savefig(os.path.join(static_folder, 'color_distribution.png'))
    print("Графики сохранены!")


# запуск приложения
if __name__ == '__main__':
    app.run(debug=True)