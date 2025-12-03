import matplotlib.pyplot as plt
import numpy as np
import time
from dataclasses import dataclass
from typing import List, Tuple
import math

@dataclass
class Point:
    x: int
    y: int

class RasterAlgorithms:
    """Класс, реализующий базовые растровые алгоритмы"""
    
    @staticmethod
    def step_by_step(x1: int, y1: int, x2: int, y2: int) -> List[Point]:
        """Пошаговый алгоритм"""
        points = []
        if x1 == x2:  # Вертикальная линия
            for y in range(min(y1, y2), max(y1, y2) + 1):
                points.append(Point(x1, y))
        else:
            k = (y2 - y1) / (x2 - x1)
            b = y1 - k * x1
            
            if abs(k) <= 1:  # Более пологие линии
                x_start, x_end = sorted([x1, x2])
                for x in range(x_start, x_end + 1):
                    y = round(k * x + b)
                    points.append(Point(x, y))
            else:  # Более крутые линии
                y_start, y_end = sorted([y1, y2])
                for y in range(y_start, y_end + 1):
                    x = round((y - b) / k) if k != 0 else x1
                    points.append(Point(x, y))
        return points
    
    @staticmethod
    def dda(x1: int, y1: int, x2: int, y2: int) -> List[Point]:
        """Алгоритм ЦДА (Digital Differential Analyzer)"""
        points = []
        
        dx = x2 - x1
        dy = y2 - y1
        
        steps = max(abs(dx), abs(dy))
        
        if steps == 0:
            points.append(Point(x1, y1))
            return points
        
        x_inc = dx / steps
        y_inc = dy / steps
        
        x = x1
        y = y1
        
        for _ in range(steps + 1):
            points.append(Point(round(x), round(y)))
            x += x_inc
            y += y_inc
        
        return points
    
    @staticmethod
    def bresenham_line(x1: int, y1: int, x2: int, y2: int) -> List[Point]:
        """Алгоритм Брезенхема для отрезков"""
        points = []
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        steep = dy > dx
        
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
            dx, dy = dy, dx
        
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        
        dx = x2 - x1
        dy = abs(y2 - y1)
        
        error = dx // 2
        y_step = 1 if y1 < y2 else -1
        y = y1
        
        for x in range(x1, x2 + 1):
            if steep:
                points.append(Point(y, x))
            else:
                points.append(Point(x, y))
            
            error -= dy
            if error < 0:
                y += y_step
                error += dx
        
        return points
    
    @staticmethod
    def bresenham_circle(xc: int, yc: int, r: int) -> List[Point]:
        """Алгоритм Брезенхема для окружности"""
        points = []
        x = 0
        y = r
        d = 3 - 2 * r
        
        def add_points(xc, yc, x, y):
            """Добавляем 8 симметричных точек"""
            points.extend([
                Point(xc + x, yc + y),
                Point(xc - x, yc + y),
                Point(xc + x, yc - y),
                Point(xc - x, yc - y),
                Point(xc + y, yc + x),
                Point(xc - y, yc + x),
                Point(xc + y, yc - x),
                Point(xc - y, yc - x)
            ])
        
        add_points(xc, yc, x, y)
        
        while y >= x:
            x += 1
            
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
            
            add_points(xc, yc, x, y)
        
        # Удаляем дубликаты
        unique_points = []
        seen = set()
        for p in points:
            key = (p.x, p.y)
            if key not in seen:
                seen.add(key)
                unique_points.append(p)
        
        return unique_points

def plot_results(points, title, algorithm_name, grid_size=20):
    """Создает график с результатами"""
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Настраиваем сетку
    ax.set_xticks(np.arange(-grid_size, grid_size + 1, 1))
    ax.set_yticks(np.arange(-grid_size, grid_size + 1, 1))
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Рисуем оси
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.axvline(x=0, color='black', linewidth=0.5)
    
    # Устанавливаем пределы
    ax.set_xlim(-grid_size, grid_size)
    ax.set_ylim(-grid_size, grid_size)
    
    # Подписи
    ax.set_xlabel('X координата', fontsize=12)
    ax.set_ylabel('Y координата', fontsize=12)
    ax.set_title(f"{algorithm_name}\n{title}", fontsize=14, pad=20)
    
    # Отмечаем целочисленные точки сетки
    for i in range(-grid_size, grid_size + 1):
        for j in range(-grid_size, grid_size + 1):
            ax.plot(i, j, 'o', color='lightgray', markersize=3, alpha=0.5)
    
    # Рисуем точки алгоритма
    x_vals = [p.x for p in points]
    y_vals = [p.y for p in points]
    
    if "окружность" in algorithm_name.lower():
        ax.plot(x_vals, y_vals, 's', color='red', markersize=8)
    else:
        ax.plot(x_vals, y_vals, 's', color='blue', markersize=8)
    
    # Подписываем некоторые точки
    if points and len(points) < 20:
        for i, p in enumerate(points[:10]):
            ax.text(p.x + 0.2, p.y + 0.2, f'({p.x},{p.y})', 
                   fontsize=8, alpha=0.7)
    
    ax.set_aspect('equal', adjustable='box')
    plt.tight_layout()
    return fig

def print_points_table(points, algorithm_name):
    """Выводит таблицу точек"""
    print(f"\n{'='*60}")
    print(f"Алгоритм: {algorithm_name}")
    print(f"Количество точек: {len(points)}")
    print(f"{'='*60}")
    
    # Выводим точки по 5 в строку
    for i in range(0, len(points), 5):
        row_points = points[i:i+5]
        row_str = "  ".join([f"({p.x:3},{p.y:3})" for p in row_points])
        print(row_str)
    
    print(f"{'='*60}")

def main():
    """Основная функция консольного приложения"""
    print("="*60)
    print("ЛАБОРАТОРНАЯ РАБОТА 4: БАЗОВЫЕ РАСТРОВЫЕ АЛГОРИТМЫ")
    print("="*60)
    
    raster = RasterAlgorithms()
    
    # Примеры для демонстрации
    examples = [
        {
            "name": "Пошаговый алгоритм",
            "algorithm": raster.step_by_step,
            "params": (-5, -5, 10, 8)
        },
        {
            "name": "Алгоритм ЦДА",
            "algorithm": raster.dda,
            "params": (-5, -5, 10, 8)
        },
        {
            "name": "Алгоритм Брезенхема (отрезок)",
            "algorithm": raster.bresenham_line,
            "params": (-5, -5, 10, 8)
        },
        {
            "name": "Алгоритм Брезенхема (окружность)",
            "algorithm": raster.bresenham_circle,
            "params": (0, 0, 8)
        }
    ]
    
    results = []
    
    # Выполняем все алгоритмы
    for example in examples:
        print(f"\nВыполняется {example['name']}...")
        
        # Измеряем время
        start_time = time.perf_counter()
        points = example['algorithm'](*example['params'])
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000  # мс
        
        # Сохраняем результаты
        results.append({
            "name": example['name'],
            "points": points,
            "time": execution_time,
            "params": example['params']
        })
        
        # Выводим информацию
        print_points_table(points, example['name'])
        print(f"Время выполнения: {execution_time:.4f} мс")
        
        # Для пошагового алгоритма показываем вычисления
        if example['name'] == "Пошаговый алгоритм":
            x1, y1, x2, y2 = example['params']
            if x1 != x2:
                k = (y2 - y1) / (x2 - x1)
                b = y1 - k * x1
                print(f"\nВычисления:")
                print(f"  k = (y2 - y1) / (x2 - x1) = ({y2} - {y1}) / ({x2} - {x1}) = {k:.2f}")
                print(f"  b = y1 - k * x1 = {y1} - {k:.2f} * {x1} = {b:.2f}")
                print(f"  Уравнение: y = {k:.2f}x + {b:.2f}")
        
        # Для окружности показываем параметры
        elif example['name'] == "Алгоритм Брезенхема (окружность)":
            xc, yc, r = example['params']
            print(f"\nПараметры окружности:")
            print(f"  Центр: ({xc}, {yc})")
            print(f"  Радиус: {r}")
            print(f"  Начальное d = 3 - 2r = 3 - 2*{r} = {3 - 2*r}")
    
    # Создаем графики
    print(f"\n{'='*60}")
    print("СОЗДАНИЕ ГРАФИКОВ...")
    
    for i, result in enumerate(results):
        if "окружность" in result["name"].lower():
            title = f"Центр: {result['params'][0:2]}, R={result['params'][2]}"
        else:
            title = f"Отрезок: {result['params'][0:2]} → {result['params'][2:4]}"
        
        fig = plot_results(result["points"], title, result["name"])
        
        # Сохраняем график
        filename = f"алгоритм_{i+1}.png"
        fig.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"  График сохранен: {filename}")
        plt.close(fig)
    
    # Выводим сравнение производительности
    print(f"\n{'='*60}")
    print("СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ АЛГОРИТМОВ")
    print(f"{'='*60}")
    print(f"{'Алгоритм':<35} {'Время (мс)':<15} {'Отн. скорость':<15}")
    print(f"{'-'*65}")
    
    base_time = results[0]["time"]  # Время пошагового алгоритма
    for result in results:
        rel_speed = base_time / result["time"] if result["time"] > 0 else 0
        print(f"{result['name']:<35} {result['time']:<15.4f} {rel_speed:<15.2f}")
    
    print(f"\n{'='*60}")
    print("ВСЕ ГРАФИКИ СОХРАНЕНЫ В ФАЙЛЫ:")
    print("  алгоритм_1.png - Пошаговый алгоритм")
    print("  алгоритм_2.png - Алгоритм ЦДА")
    print("  алгоритм_3.png - Алгоритм Брезенхема (отрезок)")
    print("  алгоритм_4.png - Алгоритм Брезенхема (окружность)")
    print(f"{'='*60}")
    
    # Инструкция для пользователя
    print(f"\nИНСТРУКЦИЯ:")
    print("1. Для изменения параметров отредактируйте код в функции main()")
    print("2. Все графики автоматически сохраняются в PNG файлы")
    print("3. Для создания веб-приложения запустите: streamlit run raster_algorithms.py")

if __name__ == "__main__":
    main()
    # Ожидаем нажатия Enter перед закрытием
    input("\nНажмите Enter для выхода...")
