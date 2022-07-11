from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsPixmapItem, QFileDialog
from PyQt5.QtGui import QBrush, QPen, QPixmap, QColor, QFont, QPainter
from PyQt5.QtCore import Qt, QRectF, QFileInfo
from math import tan, radians, cos, sin
from fpdf import FPDF


Form, Window = uic.loadUiType("GUI.ui")
app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)
window.show()
desktop_screen = QApplication.desktop()
window.setGeometry(0, 30, desktop_screen.width(), desktop_screen.height() - 70)
man_height_pix = 400
man_width_pix = 130
scale = man_height_pix/1800
pen = QPen(QColor(139, 69, 19))
brush = QBrush(QColor(139, 69, 19))
top_view_offset = 50  # Расстояние от вида сбоку до вида сверху
blueprint_offset = 50 # Расстояние от изображения фигуры человека до чертежа
check = 0
scene = 0


def interval_input_check():
    global check
    check = 1
    count_interval_on_quantity()


def image_scale():
    if form.input_height.text().isnumeric() and form.input_depth.text().isnumeric():
        s_height = int(form.input_height.text())*scale
        s_depth = int(form.input_depth.text())
    if man_height_pix > s_height:
        form.graphicsView.resetTransform()
        form.graphicsView.scale((form.graphicsView.height() - 20)/(top_view_offset + man_height_pix + s_depth),
                                (form.graphicsView.height() - 20)/(top_view_offset + man_height_pix + s_depth))
    else:
        form.graphicsView.resetTransform()
        form.graphicsView.scale((form.graphicsView.height() - 20)/(top_view_offset + s_height + s_depth),
                                (form.graphicsView.height() - 20)/(top_view_offset + s_height + s_depth))


def count_interval_on_quantity():

    if form.input_height.text().isnumeric() and form.input_interval.text().isnumeric() \
            and form.input_width.text().isnumeric() and form.input_rod_width.text().isnumeric() \
            and form.input_quantity.text().isnumeric() and form.input_depth.text().isnumeric() \
            and form.input_bottom_rod_width.text().isnumeric() and form.input_top_rod_width.text().isnumeric()\
            and form.input_angle.text().isnumeric():
        height = int(form.input_height.text())
        interval = int(form.input_interval.text())
        width = int(form.input_width.text())
        rod_width = int(form.input_rod_width.text())
        depth = int(form.input_depth.text())
        quantity = int(form.input_quantity.text())
        bottom_rod_width = int(form.input_bottom_rod_width.text())
        top_rod_width = int(form.input_top_rod_width.text())
        angle = int(form.input_angle.text())
        s_width = width*scale
        s_height = height*scale
        s_rod_width = rod_width*scale
        s_depth = depth*scale
    else:
        return form.result_output.setPlainText('Проверьте исходные данные')

    if angle > 45:
        angle = 45
        form.input_angle.setText('45')
    r_angle = radians(angle)
    angled_rod_width = rod_width*cos(r_angle) + depth*sin(r_angle)
    
    global check
    if check == 1:
        quantity = width//interval + 1
        form.input_quantity.setText(str(quantity))
        check = 0

    pic = QGraphicsPixmapItem()
    pic.setPixmap(QPixmap('MAN.jpg').scaled(man_width_pix, man_height_pix))
    global scene
    scene = QGraphicsScene()
    scene.setObjectName('graphicsScene')
    scene.addItem(pic)
    scene.setBackgroundBrush(QBrush(Qt.white))

    if ((s_width - s_rod_width)/(quantity - 1) - s_rod_width) > 0:
        i = 0
        if bottom_rod_width > 0:
            scene.addRect(man_width_pix + blueprint_offset, man_height_pix, s_width, -bottom_rod_width*scale,
                          pen, brush)
        if top_rod_width > 0:
            scene.addRect(man_width_pix + blueprint_offset, man_height_pix - s_height,
                          s_width, top_rod_width*scale, pen, brush)

        scene.addRect(man_width_pix + blueprint_offset, man_height_pix + top_view_offset + s_depth + 40, 1, 1,
                      QPen(Qt.white), QBrush(Qt.white))

        while i < quantity:
            # Вид сбоку
            scene.addRect(man_width_pix + blueprint_offset + (i*(s_width - angled_rod_width*scale)/(quantity - 1)),
                          man_height_pix, angled_rod_width*scale, -s_height, pen, brush)
            # Вид сверху
            rect = scene.addRect(man_width_pix + blueprint_offset +
                                 (i*(s_width - angled_rod_width*scale)/(quantity - 1)),
                                 man_height_pix + top_view_offset, s_rod_width, s_depth, pen, brush)
            rect.setTransformOriginPoint(man_width_pix + blueprint_offset +
                                         (i*(s_width - angled_rod_width*scale)/(quantity - 1)),
                                         man_height_pix + top_view_offset + s_depth)
            rect.setRotation(angle)
            i += 1

        form.graphicsView.setScene(scene)
        form.result_output.setPlainText('Расстояние между рейками = ' +
                                        str(int((width - rod_width)/(quantity - 1) - rod_width)) + ' мм')

        counted_interval = (s_width - s_rod_width)/(quantity - 1) - s_rod_width
        step_pix = (s_width - angled_rod_width*scale)/(quantity - 1)
        angled_interval = \
            (s_width - s_rod_width)/(quantity - 1)*cos(r_angle) - s_rod_width*cos(r_angle)
        form.input_interval.setText(str(int(step_pix/scale)))

        # Простановка размеров на чертеже
        text = scene.addText(str(rod_width), QFont())
        text.setPos(man_width_pix + blueprint_offset + s_rod_width/2 - 10,
                    man_height_pix + top_view_offset + s_depth + 10)
        text.setTransformOriginPoint(-(s_rod_width/2 - 10), -10)
        text.setRotation(angle)

        scene.addText(str(height), QFont()).setPos(man_width_pix + 10, man_height_pix - s_height/2-10)
        text = scene.addText(str(int(angled_interval//scale)), QFont())
        text.setPos(man_width_pix + blueprint_offset + step_pix + s_rod_width + angled_interval/2 - 15,
                    man_height_pix + top_view_offset + s_depth + 10)
        text.setTransformOriginPoint(-(s_rod_width + counted_interval/2 - 15), -10)
        text.setRotation(angle)

        scene.addText(str(width), QFont()).setPos(man_width_pix + blueprint_offset + s_width/2 - 15,
                                                  man_height_pix + 10)
        scene.addText(str(int(step_pix/scale)),
                      QFont()).setPos(man_width_pix + blueprint_offset + step_pix/2 - 12 + s_depth*sin(r_angle),
                                      man_height_pix + top_view_offset - 30)

        text = scene.addText(str(depth), QFont())
        text.setPos(man_width_pix + blueprint_offset - 35, man_height_pix + top_view_offset + s_depth/2 - 11)
        text.setTransformOriginPoint(35, -(-s_depth/2 - 11))
        text.setRotation(angle)

        if angle > 0:
            # Размер зазора
            scene.addText(str(int(step_pix/scale - angled_rod_width)),
                          QFont()).setPos(man_width_pix + blueprint_offset + angled_rod_width*scale +
                                          step_pix + (step_pix - angled_rod_width*scale)/2 - 11,
                                          man_height_pix + top_view_offset - 30)
            # Размерные линии зазора
            scene.addLine(man_width_pix + blueprint_offset + step_pix*2,
                          man_height_pix + top_view_offset - 10,
                          man_width_pix + blueprint_offset + step_pix + angled_rod_width*scale,
                          man_height_pix + top_view_offset - 10)
            scene.addLine(man_width_pix + blueprint_offset + step_pix*2,
                          man_height_pix - 13 + top_view_offset,
                          man_width_pix + blueprint_offset + step_pix*2,
                          man_height_pix + top_view_offset + s_depth)
            scene.addLine(man_width_pix + blueprint_offset + step_pix + angled_rod_width*scale,
                          man_height_pix - 13 + top_view_offset,
                          man_width_pix + blueprint_offset + step_pix + angled_rod_width*scale,
                          man_height_pix + top_view_offset + s_depth - s_depth*cos(r_angle) + s_rod_width*sin(r_angle))


        # Размерные линии высоты перегородки
        scene.addLine(man_width_pix + 40, man_height_pix, man_width_pix + 40, man_height_pix - s_height)
        scene.addLine(man_width_pix + 36, man_height_pix, man_width_pix + blueprint_offset, man_height_pix)
        scene.addLine(man_width_pix + 36, man_height_pix - s_height, man_width_pix + blueprint_offset,
                      man_height_pix - s_height)

        # Размерные линии ширины перегородки
        scene.addLine(man_width_pix + blueprint_offset, man_height_pix + 10,
                      man_width_pix + blueprint_offset + s_width, man_height_pix + 10)
        scene.addLine(man_width_pix + blueprint_offset, man_height_pix,
                      man_width_pix + blueprint_offset, man_height_pix + 13)
        scene.addLine(man_width_pix + blueprint_offset + s_width,
                      man_height_pix, man_width_pix + blueprint_offset + s_width,
                      man_height_pix + 13)

        # Размерные линии ширины рейки
        line = scene.addLine(man_width_pix + blueprint_offset, man_height_pix + 10 + top_view_offset + s_depth,
                             man_width_pix + blueprint_offset + s_rod_width,
                             man_height_pix + 10 + top_view_offset + s_depth)
        line.setTransformOriginPoint(man_width_pix + blueprint_offset, man_height_pix + top_view_offset + s_depth)
        line.setRotation(angle)

        line = scene.addLine(man_width_pix + blueprint_offset, man_height_pix + top_view_offset + s_depth,
                             man_width_pix + blueprint_offset, man_height_pix + 13 + top_view_offset + s_depth)
        line.setTransformOriginPoint(man_width_pix + blueprint_offset, man_height_pix + top_view_offset + s_depth)
        line.setRotation(angle)

        line = scene.addLine(man_width_pix + blueprint_offset + s_rod_width,
                             man_height_pix + top_view_offset + depth * scale,
                             man_width_pix + blueprint_offset + s_rod_width,
                             man_height_pix + 13 + top_view_offset + depth * scale)
        line.setTransformOriginPoint(man_width_pix + blueprint_offset, man_height_pix + top_view_offset + s_depth)
        line.setRotation(angle)

        # Размерные линии интервала
        line = scene.addLine(man_width_pix + blueprint_offset + step_pix + s_rod_width,
                             man_height_pix + 10 + top_view_offset + s_depth,
                             man_width_pix + blueprint_offset + step_pix +
                             step_pix*cos(r_angle),
                             man_height_pix + 10 + top_view_offset + s_depth)
        line.setTransformOriginPoint(man_width_pix + blueprint_offset + step_pix,
                                     man_height_pix + top_view_offset + s_depth)
        line.setRotation(angle)

        line = scene.addLine(man_width_pix + blueprint_offset + step_pix + s_rod_width,
                             man_height_pix + top_view_offset + s_depth,
                             man_width_pix + blueprint_offset + step_pix + s_rod_width,
                             man_height_pix + 13 + top_view_offset + s_depth)
        line.setTransformOriginPoint(man_width_pix + blueprint_offset + step_pix,
                                     man_height_pix + top_view_offset + s_depth)
        line.setRotation(angle)

        line = scene.addLine(man_width_pix + blueprint_offset + step_pix*2,
                             man_height_pix + top_view_offset + s_depth,
                             man_width_pix + blueprint_offset + step_pix*2,
                             man_height_pix + 13 + top_view_offset + s_depth +
                             (counted_interval+s_rod_width)*sin(r_angle))
        line.setTransformOriginPoint(man_width_pix + blueprint_offset + step_pix*2,
                                     man_height_pix + top_view_offset + s_depth)
        line.setRotation(angle)

        # Размерные линии шага
        scene.addLine(man_width_pix + blueprint_offset + s_depth*sin(r_angle),
                      man_height_pix + top_view_offset - 10,
                      man_width_pix + blueprint_offset + step_pix + s_depth*sin(r_angle),
                      man_height_pix + top_view_offset - 10)
        scene.addLine(man_width_pix + blueprint_offset + s_depth*sin(r_angle),
                      man_height_pix + top_view_offset + s_depth - s_depth*cos(r_angle),
                      man_width_pix + blueprint_offset + s_depth*sin(r_angle),
                      man_height_pix + top_view_offset - 13)
        scene.addLine(man_width_pix + blueprint_offset + step_pix + s_depth*sin(r_angle),
                      man_height_pix + top_view_offset + s_depth - s_depth*cos(r_angle),
                      man_width_pix + blueprint_offset + step_pix + s_depth*sin(r_angle),
                      man_height_pix + top_view_offset - 13)

        # Размерные линии глубины
        line = scene.addLine(man_width_pix + blueprint_offset - 7, man_height_pix + top_view_offset,
                             man_width_pix + blueprint_offset - 7,
                             man_height_pix + top_view_offset + s_depth)
        line.setTransformOriginPoint(man_width_pix + blueprint_offset, man_height_pix + top_view_offset + s_depth)
        line.setRotation(angle)
        line = scene.addLine(man_width_pix + blueprint_offset - 10, man_height_pix + top_view_offset,
                             man_width_pix + blueprint_offset,
                             man_height_pix + top_view_offset)
        line.setTransformOriginPoint(man_width_pix + blueprint_offset, man_height_pix + top_view_offset + s_depth)
        line.setRotation(angle)
        line = scene.addLine(man_width_pix + blueprint_offset - 10, man_height_pix + top_view_offset + s_depth,
                             man_width_pix + blueprint_offset,
                             man_height_pix + top_view_offset + s_depth)
        line.setTransformOriginPoint(man_width_pix + blueprint_offset, man_height_pix + top_view_offset + s_depth)
        line.setRotation(angle)
        image_scale()

    else:
        return form.result_output.setPlainText('Проверьте исходные данные')


def save_pdf():
    global scene
    if form.input_height.text().isnumeric() and form.input_interval.text().isnumeric() \
            and form.input_width.text().isnumeric() and form.input_rod_width.text().isnumeric() \
            and form.input_quantity.text().isnumeric() and form.input_depth.text().isnumeric() \
            and form.input_bottom_rod_width.text().isnumeric() and form.input_top_rod_width.text().isnumeric()\
            and form.input_angle.text().isnumeric():
        height = int(form.input_height.text())
        interval = int(form.input_interval.text())
        width = int(form.input_width.text())
        rod_width = int(form.input_rod_width.text())
        depth = int(form.input_depth.text())
        quantity = int(form.input_quantity.text())
        bottom_rod_width = int(form.input_bottom_rod_width.text())
        top_rod_width = int(form.input_top_rod_width.text())
        angle = int(form.input_angle.text())
    else:
        return form.result_output.setPlainText('Проверьте исходные данные')
    rect = QRectF(0, 0, scene.sceneRect().width(), scene.sceneRect().height())
    pix = QPixmap(int(scene.sceneRect().width()), int(scene.sceneRect().height()))
    painter = QPainter(pix)
    scene.render(painter, rect)
    painter.end()
    pix.save("capture.jpg", "JPG")
    line_gap = 6
    pdf = FPDF('P', 'mm')
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)
    pdf.image("capture.jpg", 5, 5, 190)
    pdf.cell(10, 210, ln=True)
    pdf.cell(50, line_gap, f'Высота перегородки = {height} мм.', ln=True)
    pdf.cell(50, line_gap, f'Ширина перегородки = {width} мм.', ln=True)
    pdf.cell(50, line_gap, f'Глубина стойки = {depth} мм.', ln=True)
    pdf.cell(50, line_gap, f'Ширина стойки = {rod_width} мм.', ln=True)
    pdf.cell(50, line_gap, f'Количество стоек = {rod_width} шт.', ln=True)
    pdf.cell(50, line_gap, f'Толщина верхней рейки = {top_rod_width} мм.', ln=True)
    pdf.cell(50, line_gap, f'Толщина нижней рейки = {bottom_rod_width} мм.', ln=True)
    pdf.cell(50, line_gap, f'Угол поворота стоек = {angle} град.', ln=True)
    fn, _ = QFileDialog.getSaveFileName(None, 'PDF', '', 'PDF (*.pdf)')
    print(fn)
    if fn != '':
        if QFileInfo(fn).suffix() == "":
            fn += '.pdf'
        print(fn)
        pdf.output(fn)


# Первичная отрисовка
count_interval_on_quantity()
# Вызов функции по нажатию кнопки "Рассчитать" или Enter
form.count_button.clicked.connect(save_pdf)
form.input_rod_width.returnPressed.connect(count_interval_on_quantity)
form.input_height.returnPressed.connect(count_interval_on_quantity)
form.input_width.returnPressed.connect(count_interval_on_quantity)
form.input_depth.returnPressed.connect(count_interval_on_quantity)
form.input_quantity.returnPressed.connect(count_interval_on_quantity)
form.input_interval.returnPressed.connect(interval_input_check)
form.input_bottom_rod_width.returnPressed.connect(count_interval_on_quantity)
form.input_top_rod_width.returnPressed.connect(count_interval_on_quantity)
form.input_angle.returnPressed.connect(count_interval_on_quantity)

app.exec()
