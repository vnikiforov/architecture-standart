import csv
from datetime import datetime
import xml.etree.ElementTree as ET

def csv_to_drawio_gantt(csv_file_path, output_xml_path):
    # Цветовая схема для команд
    TEAM_COLORS = {
        'Команда сайта': {'fill': '#4A90E2', 'stroke': '#357ABD'},
        'Команда ИК': {'fill': '#50E3C2', 'stroke': '#3BBF9D'},
        'Команда бэк-офиса': {'fill': '#F5A623', 'stroke': '#D6901F'},
        'Команда АБС': {'fill': '#BD10E0', 'stroke': '#8B0DA5'},
        'Команда БД': {'fill': '#7ED321', 'stroke': '#67B017'},
        'QA команда': {'fill': '#D0021B', 'stroke': '#A80116'},
        'Команда безопасности': {'fill': '#8B572A', 'stroke': '#6F4522'},
        'DevOps команда': {'fill': '#417505', 'stroke': '#315A04'},
        '': {'fill': '#9B9B9B', 'stroke': '#7A7A7A'}  # Для задач без команды
    }
    
    # Читаем CSV
    tasks = []
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            task_name = row['Task'].strip()
            # Определяем уровень вложенности по отступам
            level = (len(row['Task']) - len(task_name)) // 2
            tasks.append({
                'name': task_name,
                'start': row['Start Date'],
                'end': row['End Date'],
                'responsible': row['Responsible'].strip(),
                'level': level
            })
    
    # Создаем XML структуру draw.io
    mxfile = ET.Element('mxfile', {
        'host': 'app.diagrams.net',
        'modified': datetime.now().isoformat(),
        'agent': 'Python Script',
        'version': '21.6.5'
    })
    
    diagram = ET.SubElement(mxfile, 'diagram', {'name': 'Диаграмма Ганта: Депозиты Онлайн MVP', 'id': 'GanttDiagram'})
    mxgraphmodel = ET.SubElement(diagram, 'mxGraphModel', {
        'dx': '2000',
        'dy': '1200',
        'grid': '1',
        'gridSize': '10',
        'guides': '1',
        'tooltips': '1',
        'connect': '1',
        'arrows': '1',
        'fold': '1',
        'page': '1',
        'pageScale': '1',
        'pageWidth': '2500',
        'pageHeight': '1500',
        'math': '0',
        'shadow': '0'
    })
    
    root = ET.SubElement(mxgraphmodel, 'root')
    
    # Background cell
    ET.SubElement(root, 'mxCell', {'id': '0'})
    ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})
    
    # Расчет позиций
    base_date = datetime(2025, 10, 6)
    y_position = 100
    task_height = 35
    day_width = 6  # пикселей на день
    
    # Создаем временную шкалу (ось X)
    create_timeline(root, base_date, day_width)
    
    # Создаем задачи
    for i, task in enumerate(tasks):
        # Рассчитываем длину задачи в днях
        start_date = datetime.strptime(task['start'], '%Y-%m-%d')
        end_date = datetime.strptime(task['end'], '%Y-%m-%d')
        duration_days = (end_date - start_date).days + 1
        
        # Позиция по X
        days_from_start = (start_date - base_date).days
        x_position = 300 + (days_from_start * day_width)  # Отступ для временной шкалы
        width = max(duration_days * day_width, 30)  # Минимальная ширина 30px
        
        # Определяем стиль в зависимости от уровня и команды
        style, y_offset = get_task_style(task, TEAM_COLORS, y_position, task_height)
        
        # Создаем задачу
        task_label = create_task_label(task)
            
        task_cell = ET.SubElement(root, 'mxCell', {
            'id': f'task_{i}',
            'value': task_label,
            'style': style,
            'parent': '1',
            'vertex': '1'
        })
        
        ET.SubElement(task_cell, 'mxGeometry', {
            'x': str(x_position),
            'y': str(y_position + y_offset),
            'width': str(width),
            'height': str(task_height - 5),  # Немного уменьшаем высоту для лучшего вида
            'as': 'geometry'
        })
        
        # Добавляем текстовую метку слева (название задачи)
        if task['level'] <= 1:  # Только для проекта и фаз
            label_cell = ET.SubElement(root, 'mxCell', {
                'id': f'label_{i}',
                'value': task['name'],
                'style': f"text;html=1;align=right;verticalAlign=middle;resizable=0;points=[];autosize=1;spacingLeft=4;fontSize={'14' if task['level'] == 0 else '12'};fontStyle={'1' if task['level'] == 0 else '0'}",
                'parent': '1',
                'vertex': '1'
            })
            ET.SubElement(label_cell, 'mxGeometry', {
                'x': '50',
                'y': str(y_position + y_offset),
                'width': '240',
                'height': str(task_height - 5),
                'as': 'geometry'
            })
        
        y_position += task_height + (5 if task['level'] >= 2 else 10)
    
    # Добавляем легенду
    create_legend(root, TEAM_COLORS, y_position + 50)
    
    # Сохраняем XML
    tree = ET.ElementTree(mxfile)
    tree.write(output_xml_path, encoding='utf-8', xml_declaration=True)
    print(f"Диаграмма Ганта сохранена в: {output_xml_path}")

def create_timeline(root, base_date, day_width):
    """Создает временную шкалу на диаграмме"""
    # Месяцы для временной шкалы
    months = [
        ('Окт 2025', datetime(2025, 10, 1), datetime(2025, 10, 31)),
        ('Ноя 2025', datetime(2025, 11, 1), datetime(2025, 11, 30)),
        ('Дек 2025', datetime(2025, 12, 1), datetime(2025, 12, 31)),
        ('Янв 2026', datetime(2026, 1, 1), datetime(2026, 1, 31)),
        ('Фев 2026', datetime(2026, 2, 1), datetime(2026, 2, 28)),
        ('Мар 2026', datetime(2026, 3, 1), datetime(2026, 3, 31))
    ]
    
    y_timeline = 40
    # Линия временной шкалы
    timeline = ET.SubElement(root, 'mxCell', {
        'id': 'timeline',
        'value': '',
        'style': 'shape=line;strokeWidth=2;strokeColor=#666666;',
        'parent': '1',
        'vertex': '1'
    })
    ET.SubElement(timeline, 'mxGeometry', {
        'x': '300',
        'y': str(y_timeline),
        'width': str(180 * day_width),  # Примерная длина до марта 2026
        'height': '1',
        'as': 'geometry'
    })
    
    # Добавляем месяцы
    for i, (month_name, start, end) in enumerate(months):
        days_from_base = (start - base_date).days
        x_pos = 300 + (days_from_base * day_width)
        
        month_cell = ET.SubElement(root, 'mxCell', {
            'id': f'month_{i}',
            'value': month_name,
            'style': 'text;html=1;align=center;verticalAlign=middle;resizable=0;points=[];autosize=1;fontSize=11;fontStyle=1',
            'parent': '1',
            'vertex': '1'
        })
        ET.SubElement(month_cell, 'mxGeometry', {
            'x': str(x_pos),
            'y': str(y_timeline - 25),
            'width': '60',
            'height': '20',
            'as': 'geometry'
        })

def get_task_style(task, team_colors, y_position, task_height):
    """Определяет стиль задачи в зависимости от уровня и команды"""
    level = task['level']
    team = task['responsible']
    
    base_style = "rounded=1;whiteSpace=wrap;html=1;fontSize=11;"
    
    if level == 0:  # Основной проект
        style = f"{base_style}fillColor=#2C3E50;strokeColor=#1A252F;fontSize=14;fontStyle=1;gradientColor=#34495E"
        y_offset = 0
    elif level == 1:  # Фазы
        style = f"{base_style}fillColor=#3498DB;strokeColor=#2980B9;fontSize=12;fontStyle=1;gradientColor=#5DADE2"
        y_offset = 0
    else:  # Подзадачи
        colors = team_colors.get(team, team_colors[''])
        style = f"{base_style}fillColor={colors['fill']};strokeColor={colors['stroke']};fontSize=10"
        # Смещение для визуальной иерархии
        y_offset = 0
    
    # Добавляем тень для лучшей визуализации
    style += ";shadow=1"
    
    return style, y_offset

def create_task_label(task):
    """Создает метку для задачи"""
    if task['level'] <= 1:
        return task['name']
    else:
        label = task['name']
        if task['responsible']:
            label += f"\n{task['responsible']}"
        return label

def create_legend(root, team_colors, start_y):
    """Создает легенду с цветовым кодированием команд"""
    legend_x = 1800
    legend_y = start_y
    
    # Заголовок легенды
    legend_title = ET.SubElement(root, 'mxCell', {
        'id': 'legend_title',
        'value': 'Команды:',
        'style': 'text;html=1;align=left;verticalAlign=middle;resizable=0;points=[];autosize=1;fontSize=14;fontStyle=1',
        'parent': '1',
        'vertex': '1'
    })
    ET.SubElement(legend_title, 'mxGeometry', {
        'x': str(legend_x),
        'y': str(legend_y),
        'width': '100',
        'height': '30',
        'as': 'geometry'
    })
    
    legend_y += 40
    
    # Элементы легенды
    for i, (team, colors) in enumerate(team_colors.items()):
        if team == '':  # Пропускаем пустую команду
            continue
            
        # Цветной квадрат
        color_rect = ET.SubElement(root, 'mxCell', {
            'id': f'legend_color_{i}',
            'value': '',
            'style': f"shape=rectangle;rounded=1;whiteSpace=wrap;html=1;fillColor={colors['fill']};strokeColor={colors['stroke']};",
            'parent': '1',
            'vertex': '1'
        })
        ET.SubElement(color_rect, 'mxGeometry', {
            'x': str(legend_x),
            'y': str(legend_y),
            'width': '20',
            'height': '20',
            'as': 'geometry'
        })
        
        # Название команды
        team_label = ET.SubElement(root, 'mxCell', {
            'id': f'legend_label_{i}',
            'value': team,
            'style': 'text;html=1;align=left;verticalAlign=middle;resizable=0;points=[];autosize=1;fontSize=11;',
            'parent': '1',
            'vertex': '1'
        })
        ET.SubElement(team_label, 'mxGeometry', {
            'x': str(legend_x + 30),
            'y': str(legend_y),
            'width': '150',
            'height': '20',
            'as': 'geometry'
        })
        
        legend_y += 30

# Использование
if __name__ == "__main__":
    csv_to_drawio_gantt('gantt_data.csv', 'diagram_gantt.drawio')
    print("Диаграмма Ганта успешно создана!")
    print("\nОсобенности реализации:")
    print("✓ Цветовое кодирование по командам")
    print("✓ Временная шкала с месяцами") 
    print("✓ Легенда команд")
    print("✓ Иерархическое отображение задач")
    print("✓ Автоматическое размещение меток")