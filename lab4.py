import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
from typing import List, Tuple, Optional
import time

st.set_page_config(
    page_title="Алгоритмы отсечения",
    page_icon="✂️",
    layout="wide"
)

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Point({self.x:.2f}, {self.y:.2f})"
    
    def to_tuple(self):
        return (self.x, self.y)

class Segment:
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2
    
    def __repr__(self):
        return f"Segment({self.p1}, {self.p2})"

class Polygon:
    def __init__(self, points: List[Point]):
        self.points = points
        self.closed = True
    
    def get_edges(self) -> List[Segment]:
        edges = []
        n = len(self.points)
        for i in range(n):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % n] if self.closed else (self.points[i + 1] if i < n - 1 else None)
            if p2:
                edges.append(Segment(p1, p2))
        return edges
    
    def is_convex(self) -> bool:
        if len(self.points) < 3:
            return True
        
        n = len(self.points)
        sign = None
        
        for i in range(n):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % n]
            p3 = self.points[(i + 2) % n]
            
            cross = (p2.x - p1.x) * (p3.y - p2.y) - (p2.y - p1.y) * (p3.x - p2.x)
            
            if cross != 0:
                if sign is None:
                    sign = 1 if cross > 0 else -1
                elif sign * cross < 0:
                    return False
        
        return True

class ClippingAlgorithms:
    @staticmethod
    def liang_barsky(x1: float, y1: float, x2: float, y2: float, 
                     xmin: float, ymin: float, xmax: float, ymax: float) -> Optional[Tuple[Point, Point]]:
        dx = x2 - x1
        dy = y2 - y1
        
        p = [-dx, dx, -dy, dy]
        q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]
        
        u1 = 0.0
        u2 = 1.0
        
        for i in range(4):
            if abs(p[i]) < 1e-10:
                if q[i] < 0:
                    return None
            else:
                r = q[i] / p[i]
                if p[i] < 0:
                    if r > u2:
                        return None
                    elif r > u1:
                        u1 = r
                else:
                    if r < u1:
                        return None
                    elif r < u2:
                        u2 = r
        
        if u1 > u2:
            return None
        
        if u1 == 0 and u2 == 1:
            clipped_p1 = Point(x1, y1)
            clipped_p2 = Point(x2, y2)
        else:
            clipped_p1 = Point(x1 + u1 * dx, y1 + u1 * dy)
            clipped_p2 = Point(x1 + u2 * dx, y1 + u2 * dy)
        
        return (clipped_p1, clipped_p2)
    
    @staticmethod
    def sutherland_hodgman_polygon(polygon: Polygon, 
                                   xmin: float, ymin: float, 
                                   xmax: float, ymax: float) -> Polygon:
        def clip_edge(input_poly: List[Point], edge: str) -> List[Point]:
            output = []
            n = len(input_poly)
            
            for i in range(n):
                current = input_poly[i]
                next_pt = input_poly[(i + 1) % n]
                
                if edge == 'left':
                    current_inside = current.x >= xmin
                    next_inside = next_pt.x >= xmin
                elif edge == 'right':
                    current_inside = current.x <= xmax
                    next_inside = next_pt.x <= xmax
                elif edge == 'bottom':
                    current_inside = current.y >= ymin
                    next_inside = next_pt.y >= ymin
                elif edge == 'top':
                    current_inside = current.y <= ymax
                    next_inside = next_pt.y <= ymax
                
                if current_inside and next_inside:
                    output.append(next_pt)
                elif current_inside and not next_inside:
                    if edge == 'left':
                        y = current.y + (next_pt.y - current.y) * (xmin - current.x) / (next_pt.x - current.x)
                        output.append(Point(xmin, y))
                    elif edge == 'right':
                        y = current.y + (next_pt.y - current.y) * (xmax - current.x) / (next_pt.x - current.x)
                        output.append(Point(xmax, y))
                    elif edge == 'bottom':
                        x = current.x + (next_pt.x - current.x) * (ymin - current.y) / (next_pt.y - current.y)
                        output.append(Point(x, ymin))
                    elif edge == 'top':
                        x = current.x + (next_pt.x - current.x) * (ymax - current.y) / (next_pt.y - current.y)
                        output.append(Point(x, ymax))
                elif not current_inside and next_inside:
                    if edge == 'left':
                        y = current.y + (next_pt.y - current.y) * (xmin - current.x) / (next_pt.x - current.x)
                        output.append(Point(xmin, y))
                        output.append(next_pt)
                    elif edge == 'right':
                        y = current.y + (next_pt.y - current.y) * (xmax - current.x) / (next_pt.x - current.x)
                        output.append(Point(xmax, y))
                        output.append(next_pt)
                    elif edge == 'bottom':
                        x = current.x + (next_pt.x - current.x) * (ymin - current.y) / (next_pt.y - current.y)
                        output.append(Point(x, ymin))
                        output.append(next_pt)
                    elif edge == 'top':
                        x = current.x + (next_pt.x - current.x) * (ymax - current.y) / (next_pt.y - current.y)
                        output.append(Point(x, ymax))
                        output.append(next_pt)
            
            return output
        
        clipped_points = polygon.points.copy()
        
        for edge in ['left', 'right', 'bottom', 'top']:
            if clipped_points:
                clipped_points = clip_edge(clipped_points, edge)
        
        return Polygon(clipped_points) if clipped_points else None
    
    @staticmethod
    def cyrus_beck_polygon(subject_polygon: Polygon, clip_polygon: Polygon) -> Polygon:
        def get_normal(p1: Point, p2: Point) -> Tuple[float, float]:
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            return (-dy, dx)
        
        def dot_product(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
            return v1[0] * v2[0] + v1[1] * v2[1]
        
        def line_intersection(p1: Point, p2: Point, edge_p1: Point, edge_p2: Point) -> Optional[Point]:
            x1, y1 = p1.x, p1.y
            x2, y2 = p2.x, p2.y
            x3, y3 = edge_p1.x, edge_p1.y
            x4, y4 = edge_p2.x, edge_p2.y
            
            denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if abs(denom) < 1e-10:
                return None
            
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
            u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
            
            if 0 <= t <= 1 and 0 <= u <= 1:
                return Point(x1 + t * (x2 - x1), y1 + t * (y2 - y1))
            
            return None
        
        clip_edges = clip_polygon.get_edges()
        
        result_polygon = subject_polygon.points.copy()
        
        for edge in clip_edges:
            if not result_polygon:
                break
            
            normal = get_normal(edge.p1, edge.p2)
            
            new_polygon = []
            
            n = len(result_polygon)
            for i in range(n):
                current = result_polygon[i]
                next_pt = result_polygon[(i + 1) % n]
                
                v_current = (current.x - edge.p1.x, current.y - edge.p1.y)
                v_next = (next_pt.x - edge.p1.x, next_pt.y - edge.p1.y)
                
                d_current = dot_product(normal, v_current)
                d_next = dot_product(normal, v_next)
                
                if d_current >= 0 and d_next >= 0:
                    new_polygon.append(next_pt)
                elif d_current >= 0 and d_next < 0:
                    intersection = line_intersection(current, next_pt, edge.p1, edge.p2)
                    if intersection:
                        new_polygon.append(intersection)
                elif d_current < 0 and d_next >= 0:
                    intersection = line_intersection(current, next_pt, edge.p1, edge.p2)
                    if intersection:
                        new_polygon.append(intersection)
                        new_polygon.append(next_pt)
            
            result_polygon = new_polygon
        
        return Polygon(result_polygon) if result_polygon else None

def parse_input_file(content: str):
    lines = content.strip().split('\n')
    
    if len(lines) < 2:
        return None
    
    try:
        n = int(lines[0].strip())
        
        segments = []
        for i in range(1, n + 1):
            if i >= len(lines):
                break
            coords = list(map(float, lines[i].strip().split()))
            if len(coords) >= 4:
                p1 = Point(coords[0], coords[1])
                p2 = Point(coords[2], coords[3])
                segments.append(Segment(p1, p2))
        
        if len(lines) > n + 1:
            window_coords = list(map(float, lines[n + 1].strip().split()))
            if len(window_coords) >= 4:
                xmin, ymin, xmax, ymax = window_coords[0], window_coords[1], window_coords[2], window_coords[3]
            else:
                xmin, ymin, xmax, ymax = -10, -10, 10, 10
        else:
            xmin, ymin, xmax, ymax = -10, -10, 10, 10
        
        return segments, (xmin, ymin, xmax, ymax)
    
    except:
        return None

def create_plot(segments: List[Segment], polygon: Optional[Polygon] = None,
                clip_window: Optional[Tuple[float, float, float, float]] = None,
                clipped_segments: List[Segment] = None,
                clipped_polygon: Optional[Polygon] = None,
                algorithm_name: str = "",
                grid_size: int = 20):
    fig, ax = plt.subplots(figsize=(12, 10))
    
    ax.set_xticks(np.arange(-grid_size, grid_size + 1, 1))
    ax.set_yticks(np.arange(-grid_size, grid_size + 1, 1))
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)
    
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.axvline(x=0, color='black', linewidth=0.5)
    
    ax.set_xlim(-grid_size, grid_size)
    ax.set_ylim(-grid_size, grid_size)
    
    ax.set_xlabel('X координата', fontsize=12)
    ax.set_ylabel('Y координата', fontsize=12)
    ax.set_title(f"Алгоритм отсечения: {algorithm_name}", fontsize=14, pad=20)
    
    if clip_window:
        xmin, ymin, xmax, ymax = clip_window
        rect = patches.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin,
                               linewidth=2, edgecolor='red', facecolor='none', 
                               alpha=0.7, label='Отсекающее окно')
        ax.add_patch(rect)
    
    if segments:
        for i, segment in enumerate(segments):
            ax.plot([segment.p1.x, segment.p2.x], [segment.p1.y, segment.p2.y],
                   'b-', linewidth=2, alpha=0.5, label='Исходный отрезок' if i == 0 else None)
            ax.plot(segment.p1.x, segment.p1.y, 'bo', markersize=6, alpha=0.7)
            ax.plot(segment.p2.x, segment.p2.y, 'bo', markersize=6, alpha=0.7)
    
    if polygon:
        poly_points = [p.to_tuple() for p in polygon.points]
        if polygon.closed:
            poly_points.append(poly_points[0])
        
        x_vals = [p[0] for p in poly_points]
        y_vals = [p[1] for p in poly_points]
        
        ax.plot(x_vals, y_vals, 'g-', linewidth=2, alpha=0.7, label='Исходный многоугольник')
        for point in polygon.points:
            ax.plot(point.x, point.y, 'go', markersize=6, alpha=0.7)
    
    if clipped_segments:
        for i, segment in enumerate(clipped_segments):
            ax.plot([segment.p1.x, segment.p2.x], [segment.p1.y, segment.p2.y],
                   'g-', linewidth=3, alpha=1.0, label='Отсеченный отрезок' if i == 0 else None)
            ax.plot(segment.p1.x, segment.p1.y, 'go', markersize=8, alpha=1.0)
            ax.plot(segment.p2.x, segment.p2.y, 'go', markersize=8, alpha=1.0)
    
    if clipped_polygon:
        poly_points = [p.to_tuple() for p in clipped_polygon.points]
        if clipped_polygon.closed:
            poly_points.append(poly_points[0])
        
        x_vals = [p[0] for p in poly_points]
        y_vals = [p[1] for p in poly_points]
        
        ax.fill(x_vals, y_vals, 'yellow', alpha=0.5, label='Отсеченный многоугольник')
        ax.plot(x_vals, y_vals, 'g-', linewidth=3, alpha=1.0)
        for point in clipped_polygon.points:
            ax.plot(point.x, point.y, 'go', markersize=8, alpha=1.0)
    
    if segments or polygon or clipped_segments or clipped_polygon:
        ax.legend(loc='upper right', fontsize=10)
    
    ax.set_aspect('equal', adjustable='box')
    plt.tight_layout()
    
    return fig

def main():
    st.title("✂️ Лабораторная работа 5: Алгоритмы отсечения")
    st.markdown("**Визуализация алгоритмов отсечения отрезков и многоугольников**")
    
    tab1, tab2, tab3 = st.tabs(["📁 Загрузка данных", "⚙️ Ручной ввод", "📊 Результаты"])
    
    with tab1:
        st.header("Загрузка данных из файла")
        
        with st.expander("Формат входного файла"):
            st.code("""
n
X1_1 Y1_1 X2_1 Y2_1
X1_2 Y1_2 X2_2 Y2_2
...
X1_n Y1_n X2_n Y2_n
Xmin Ymin Xmax Ymax
            """)
        
        uploaded_file = st.file_uploader("Загрузите файл с данными", type=['txt', 'dat'])
        
        if uploaded_file is not None:
            content = uploaded_file.read().decode('utf-8')
            result = parse_input_file(content)
            
            if result:
                segments, clip_window = result
                st.success(f"✅ Загружено {len(segments)} отрезков")
                
                st.session_state.segments = segments
                st.session_state.clip_window = clip_window
                st.session_state.data_source = 'file'
                
                with st.expander("Просмотр данных"):
                    st.write(f"Отсекающее окно: {clip_window}")
                    st.write("Отрезки:")
                    for i, seg in enumerate(segments):
                        st.write(f"{i+1}: ({seg.p1.x:.1f}, {seg.p1.y:.1f}) → ({seg.p2.x:.1f}, {seg.p2.y:.1f})")
            else:
                st.error("Ошибка при чтении файла. Проверьте формат.")
    
    with tab2:
        st.header("Ручной ввод данных")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Отсекающее окно")
            xmin = st.slider("Xmin", -20, 20, -10)
            ymin = st.slider("Ymin", -20, 20, -10)
            xmax = st.slider("Xmax", -20, 20, 10)
            ymax = st.slider("Ymax", -20, 20, 10)
            
            if xmin >= xmax:
                st.warning("Xmin должен быть меньше Xmax")
            if ymin >= ymax:
                st.warning("Ymin должен быть меньше Ymax")
            
            clip_window = (xmin, ymin, xmax, ymax)
        
        with col2:
            st.subheader("Создание отрезков")
            
            preset_segments = st.selectbox("Предустановленные отрезки", 
                                          ["Случайные", "Горизонтальные", "Вертикальные", "Диагональные", "Вручную"])
            
            segments = []
            
            if preset_segments == "Случайные":
                num_segments = st.slider("Количество отрезков", 1, 10, 3)
                for i in range(num_segments):
                    x1 = np.random.randint(-15, 15)
                    y1 = np.random.randint(-15, 15)
                    x2 = np.random.randint(-15, 15)
                    y2 = np.random.randint(-15, 15)
                    segments.append(Segment(Point(x1, y1), Point(x2, y2)))
            
            elif preset_segments == "Горизонтальные":
                segments = [
                    Segment(Point(-15, 0), Point(15, 0)),
                    Segment(Point(-10, 5), Point(10, 5)),
                    Segment(Point(-12, -5), Point(12, -5))
                ]
            
            elif preset_segments == "Вертикальные":
                segments = [
                    Segment(Point(0, -15), Point(0, 15)),
                    Segment(Point(5, -10), Point(5, 10)),
                    Segment(Point(-5, -12), Point(-5, 12))
                ]
            
            elif preset_segments == "Диагональные":
                segments = [
                    Segment(Point(-15, -15), Point(15, 15)),
                    Segment(Point(-15, 10), Point(10, -15)),
                    Segment(Point(-10, -10), Point(10, 10))
                ]
            
            else:
                num_segments = st.slider("Количество отрезков", 1, 5, 2)
                for i in range(num_segments):
                    st.write(f"Отрезок {i+1}:")
                    col_x1, col_y1, col_x2, col_y2 = st.columns(4)
                    with col_x1:
                        x1 = st.number_input(f"X1_{i+1}", -20, 20, -10 + i*5)
                    with col_y1:
                        y1 = st.number_input(f"Y1_{i+1}", -20, 20, -5 + i*3)
                    with col_x2:
                        x2 = st.number_input(f"X2_{i+1}", -20, 20, 10 - i*5)
                    with col_y2:
                        y2 = st.number_input(f"Y2_{i+1}", -20, 20, 8 - i*3)
                    
                    segments.append(Segment(Point(x1, y1), Point(x2, y2)))
            
            st.subheader("Создание многоугольника для отсечения")
            create_polygon = st.checkbox("Создать многоугольник для отсечения (алгоритм Cyrus-Beck)")
            
            polygon = None
            if create_polygon:
                polygon_type = st.selectbox("Тип многоугольника", 
                                           ["Треугольник", "Прямоугольник", "Пятиугольник", "Пользовательский"])
                
                if polygon_type == "Треугольник":
                    polygon = Polygon([
                        Point(-5, -5),
                        Point(0, 8),
                        Point(5, -5)
                    ])
                elif polygon_type == "Прямоугольник":
                    polygon = Polygon([
                        Point(-6, -4),
                        Point(-6, 6),
                        Point(6, 6),
                        Point(6, -4)
                    ])
                elif polygon_type == "Пятиугольник":
                    polygon = Polygon([
                        Point(0, 8),
                        Point(-7, 3),
                        Point(-5, -5),
                        Point(5, -5),
                        Point(7, 3)
                    ])
                else:
                    num_points = st.slider("Количество вершин", 3, 8, 4)
                    points = []
                    for i in range(num_points):
                        angle = 2 * math.pi * i / num_points
                        radius = st.slider(f"Радиус вершины {i+1}", 3, 15, 8)
                        x = radius * math.cos(angle)
                        y = radius * math.sin(angle)
                        points.append(Point(x, y))
                    polygon = Polygon(points)
                
                if polygon and polygon.is_convex():
                    st.success("Многоугольник выпуклый ✓")
                elif polygon:
                    st.warning("Многоугольник невыпуклый. Алгоритм Cyrus-Beck требует выпуклый многоугольник.")
        
        if segments:
            st.session_state.segments = segments
            st.session_state.clip_window = clip_window
            st.session_state.polygon = polygon if create_polygon else None
            st.session_state.data_source = 'manual'
    
    with tab3:
        st.header("Выполнение отсечения и визуализация")
        
        if 'segments' not in st.session_state:
            st.warning("⚠️ Сначала загрузите или создайте данные во вкладках выше")
            return
        
        segments = st.session_state.segments
        clip_window = st.session_state.clip_window
        polygon = st.session_state.get('polygon', None)
        
        algorithm = st.selectbox(
            "Выберите алгоритм отсечения:",
            ["Лианга-Барски (прямоугольное окно)", 
             "Сазерленда-Ходгмана (многоугольник в прямоугольное окно)",
             "Cyrus-Beck (многоугольник в выпуклый многоугольник)"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            grid_size = st.slider("Размер сетки", 10, 30, 20)
        with col2:
            show_details = st.checkbox("Показать детали вычислений", value=True)
        
        if st.button("Выполнить отсечение", type="primary"):
            with st.spinner("Выполняется отсечение..."):
                start_time = time.perf_counter()
                
                clipped_segments = []
                clipped_polygon = None
                
                if algorithm == "Лианга-Барски (прямоугольное окно)":
                    xmin, ymin, xmax, ymax = clip_window
                    for segment in segments:
                        result = ClippingAlgorithms.liang_barsky(
                            segment.p1.x, segment.p1.y, segment.p2.x, segment.p2.y,
                            xmin, ymin, xmax, ymax
                        )
                        if result:
                            p1, p2 = result
                            clipped_segments.append(Segment(p1, p2))
                
                elif algorithm == "Сазерленда-Ходгмана (многоугольник в прямоугольное окно)":
                    if polygon:
                        xmin, ymin, xmax, ymax = clip_window
                        clipped_polygon = ClippingAlgorithms.sutherland_hodgman_polygon(
                            polygon, xmin, ymin, xmax, ymax
                        )
                
                elif algorithm == "Cyrus-Beck (многоугольник в выпуклый многоугольник)":
                    if polygon and st.session_state.get('polygon'):
                        test_polygon = Polygon([
                            Point(-8, -6),
                            Point(-8, 6),
                            Point(8, 6),
                            Point(8, -6)
                        ])
                        clipped_polygon = ClippingAlgorithms.cyrus_beck_polygon(
                            test_polygon, polygon
                        )
                
                end_time = time.perf_counter()
                execution_time = (end_time - start_time) * 1000
                
                fig = create_plot(
                    segments=segments,
                    polygon=polygon,
                    clip_window=clip_window if algorithm != "Cyrus-Beck" else None,
                    clipped_segments=clipped_segments if clipped_segments else None,
                    clipped_polygon=clipped_polygon,
                    algorithm_name=algorithm,
                    grid_size=grid_size
                )
                
                st.pyplot(fig)
                
                if show_details:
                    with st.expander("📊 Детали вычислений", expanded=True):
                        st.write(f"**Время выполнения:** {execution_time:.4f} мс")
                        
                        if algorithm == "Лианга-Барски (прямоугольное окно)":
                            st.write(f"**Отсекающее окно:** ({xmin}, {ymin}) - ({xmax}, {ymax})")
                            st.write(f"**Количество видимых отрезков:** {len(clipped_segments)} из {len(segments)}")
                            
                            for i, segment in enumerate(segments):
                                st.write(f"**Отрезок {i+1}:** ({segment.p1.x:.1f}, {segment.p1.y:.1f}) → ({segment.p2.x:.1f}, {segment.p2.y:.1f})")
                                result = ClippingAlgorithms.liang_barsky(
                                    segment.p1.x, segment.p1.y, segment.p2.x, segment.p2.y,
                                    xmin, ymin, xmax, ymax
                                )
                                if result:
                                    p1, p2 = result
                                    st.write(f"  Отсечен: ({p1.x:.1f}, {p1.y:.1f}) → ({p2.x:.1f}, {p2.y:.1f})")
                                else:
                                    st.write(f"  Полностью невидим")
                        
                        elif algorithm == "Сазерленда-Ходгмана (многоугольник в прямоугольное окно)":
                            if polygon:
                                st.write(f"**Исходный многоугольник:** {len(polygon.points)} вершин")
                                if clipped_polygon:
                                    st.write(f"**Отсеченный многоугольник:** {len(clipped_polygon.points)} вершин")
                                    st.write("Вершины отсеченного многоугольника:")
                                    for j, point in enumerate(clipped_polygon.points):
                                        st.write(f"  {j+1}: ({point.x:.2f}, {point.y:.2f})")
                                else:
                                    st.write("Многоугольник полностью невидим")
                        
                        elif algorithm == "Cyrus-Beck (многоугольник в выпуклый многоугольник)":
                            if polygon:
                                st.write(f"**Отсекающий многоугольник:** {len(polygon.points)} вершин")
                                st.write("Выпуклый: ✓" if polygon.is_convex() else "Выпуклый: ✗")
                                if clipped_polygon:
                                    st.write(f"**Отсеченный многоугольник:** {len(clipped_polygon.points)} вершин")
                                else:
                                    st.write("Многоугольник полностью невидим")
                
                with st.expander("📚 Теоретическая справка"):
                    if algorithm == "Лианга-Барски (прямоугольное окно)":
                        st.markdown("""
                        ### Алгоритм Лианга-Барски
                        
                        **Принцип работы:**
                        1. Отрезок задается параметрически:  
                           `x = x1 + u * (x2 - x1)`  
                           `y = y1 + u * (y2 - y1)`, где `u ∈ [0, 1]`
                        2. Для каждой границы окна вычисляется параметр u
                        3. Определяется интервал [u1, u2] видимой части отрезка
                        
                        **Формулы для границ:**
                        - Левая: `u = (xmin - x1) / (x2 - x1)`
                        - Правая: `u = (xmax - x1) / (x2 - x1)`
                        - Нижняя: `u = (ymin - y1) / (y2 - y1)`
                        - Верхняя: `u = (ymax - y1) / (y2 - y1)`
                        
                        **Преимущества:**
                        - Эффективен для прямоугольных окон
                        - Работает с параметрическим представлением
                        - Хорошая производительность
                        """)
                    
                    elif algorithm == "Сазерленда-Ходгмана (многоугольник в прямоугольное окно)":
                        st.markdown("""
                        ### Алгоритм Сазерленда-Ходгмана
                        
                        **Принцип работы:**
                        1. Многоугольник отсекается последовательно по каждой границе
                        2. Для каждого ребра проверяется его положение относительно границы
                        3. Генерируется новый многоугольник после каждой границы
                        
                        **Правила для каждой пары вершин:**
                        - Обе внутри → добавляем вторую вершину
                        - Внутри → снаружи → добавляем точку пересечения
                        - Снаружи → внутри → добавляем точку пересечения и вторую вершину
                        - Обе снаружи → ничего не добавляем
                        
                        **Преимущества:**
                        - Простота реализации
                        - Работает с произвольными многоугольниками
                        - Легко расширяется на выпуклые окна
                        """)
                    
                    elif algorithm == "Cyrus-Beck (многоугольник в выпуклый многоугольник)":
                        st.markdown("""
                        ### Алгоритм Cyrus-Beck
                        
                        **Принцип работы:**
                        1. Использует нормали к ребрам отсекающего многоугольника
                        2. Для каждой вершины вычисляется скалярное произведение с нормалью
                        3. Определяются точки пересечения
                        4. Строится новый отсеченный многоугольник
                        
                        **Требования:**
                        - Отсекающий многоугольник должен быть выпуклым
                        - Вершины упорядочены против часовой стрелки
                        
                        **Преимущества:**
                        - Работает с произвольными выпуклыми окнами
                        - Более общий алгоритм
                        - Хорошая производительность
                        """)
        
        else:
            st.info("Нажмите 'Выполнить отсечение' для визуализации")
            
            fig = create_plot(
                segments=segments,
                polygon=st.session_state.get('polygon', None),
                clip_window=clip_window,
                algorithm_name="Предварительный просмотр",
                grid_size=grid_size
            )
            st.pyplot(fig)
    
    with st.sidebar:
        st.header("Примеры файлов")
        
        example1 = """3
-15 -5 15 10
-5 -15 5 15
-10 5 10 -5
-8 -8 8 8"""
        
        example2 = """4
-12 -12 12 12
-12 12 12 -12
-5 -15 -5 15
15 -5 -15 5
-10 -10 10 10"""
        
        example3 = """1
0 0 0 0
-8 -8 8 8
6
0 10
-8 5
-6 -6
6 -6
8 5
0 10"""
        
        example_choice = st.selectbox("Выберите пример", ["Пример 1", "Пример 2", "Пример 3"])
        
        if example_choice == "Пример 1":
            example_content = example1
        elif example_choice == "Пример 2":
            example_content = example2
        else:
            example_content = example3
        
        st.download_button(
            label="Скачать пример",
            data=example_content,
            file_name=f"example_{example_choice.lower().replace(' ', '_')}.txt",
            mime="text/plain"
        )
        
        st.code(example_content)
        
        st.header("Настройки")
        st.markdown("""
        **Цвета на графике:**
        - 🔴 Красный: Отсекающее окно
        - 🔵 Синий: Исходные отрезки/многоугольник
        - 🟢 Зеленый: Отсеченные части
        - 🟡 Желтый: Заполненный отсеченный многоугольник
        """)
        
        st.header("Оценивание")
        st.markdown("""
        **Требования к работе:**
        - ✅ Система координат с масштабом
        - ✅ Отображение отсекающего окна
        - ✅ Визуализация исходных объектов
        - ✅ Выполнение отсечения
        - ✅ Визуализация результатов
        - ✅ Работа с файлами
        - ✅ Ручной ввод данных
        
        **Дополнительно:**
        - Теоретическое описание алгоритмов
        - Примеры вычислений
        - Сравнение алгоритмов
        """)

if __name__ == "__main__":
    if 'segments' not in st.session_state:
        st.session_state.segments = []
    if 'clip_window' not in st.session_state:
        st.session_state.clip_window = (-10, -10, 10, 10)
    if 'data_source' not in st.session_state:
        st.session_state.data_source = 'manual'
    
    main()
