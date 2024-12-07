import pygame
import math
import sys
import os
from pygame.locals import *

# 初始化Pygame
pygame.init()

# 设置窗口
WIDTH = 1000
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("凸透镜成像演示")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

# 比例尺（像素/厘米）
SCALE = 20  # 20像素 = 1厘米

# 初始参数（厘米）
focal_length = 6  # 焦距
object_distance = 15  # 物距
object_height = 5  # 物体高度
lens_x = WIDTH * 0.6  # 透镜位置移到窗口右侧一点

# 控制区域布局参数
control_area_left = 30  # 控制区域左边距
label_width = 80  # 标签宽度
slider_width = 200  # 滑块宽度
input_width = 60  # 输入框宽度
unit_width = 40  # 单位标签宽度
element_spacing = 20  # 元素之间的间距
element_height = 30  # 元素高度

# 计算各元素的水平位置
label_x = control_area_left
slider_x = label_x + label_width + element_spacing
input_x = slider_x + slider_width + element_spacing
unit_x = input_x + input_width + element_spacing/2

# 计算各行的垂直位置
base_y = HEIGHT - 140
focal_y = base_y
distance_y = base_y + 45
height_y = base_y + 90

# 设置中文字体
def get_font(size=24):  # 默认字体大小改为24
    windows_font = os.path.join(os.environ['SYSTEMROOT'], 'Fonts', 'msyh.ttc')
    try:
        if os.path.exists(windows_font):
            return pygame.font.Font(windows_font, size)
    except:
        pass
    
    try:
        return pygame.font.SysFont('microsoftyahei', size)
    except:
        try:
            return pygame.font.SysFont('simsun', size)
        except:
            print("警告：未能找到合适的中文字体，文字显示可能会有问题")
            return pygame.font.Font(None, size)

# 创建字体对象
font = get_font(24)  # 主要文字大小为24
small_font = pygame.font.Font(None, 24)

class InputBox:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = BLACK
        self.text = str(initial_val)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.active = False
        self.font = small_font
        self.cursor_visible = True
        self.cursor_timer = 0
        self.temp_text = ""  # 用于存储编辑时的临时文本

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.temp_text = self.text  # 开始编辑时保存当前值
            else:
                if self.active:  # 如果之前是激活状态，尝试更新值
                    try:
                        value = float(self.text)
                        if self.min_val <= value <= self.max_val:
                            self.value = value
                        else:
                            self.text = str(self.value)  # 如果超出范围，恢复原值
                    except ValueError:
                        self.text = str(self.value)  # 如果输入无效，恢复原值
                self.active = False
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                try:
                    value = float(self.text)
                    if self.min_val <= value <= self.max_val:
                        self.value = value
                    else:
                        self.text = str(self.value)  # 如果超出范围，恢复原值
                except ValueError:
                    self.text = str(self.value)  # 如果输入无效，恢复原值
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isnumeric() or event.unicode == '.':
                # 检查是否已经有小数点
                if event.unicode == '.' and '.' in self.text:
                    return
                # 限制输入长度
                if len(self.text) < 5:  # 最多5个字符
                    self.text += event.unicode

    def update(self, value):
        if not self.active:
            self.text = f"{value:.1f}"
            self.value = value

    def draw(self, screen):
        # 绘制输入框背景
        pygame.draw.rect(screen, LIGHT_GRAY, self.rect)
        # 绘制边框
        color = RED if self.active else BLACK
        pygame.draw.rect(screen, color, self.rect, 2)
        
        # 绘制文本
        text_surface = self.font.render(self.text, True, color)
        # 计算文本位置，使其在输入框内居中
        text_x = self.rect.x + 5
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
        
        # 如果输入框处于活动状态，绘制闪烁的光标
        if self.active:
            self.cursor_timer += 1
            if self.cursor_timer >= 30:  # 每30帧切换一次光标显示状态
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
            
            if self.cursor_visible:
                cursor_x = text_x + text_surface.get_width() + 2
                cursor_y = text_y
                cursor_height = text_surface.get_height()
                pygame.draw.line(screen, color, 
                               (cursor_x, cursor_y), 
                               (cursor_x, cursor_y + cursor_height), 
                               2)

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.rect.x
            self.value = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
            self.value = max(self.min_val, min(self.max_val, self.value))

    def update(self, value):
        if not self.dragging:
            self.value = value

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)
        pos = self.rect.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        pygame.draw.circle(screen, BLACK, (int(pos), self.rect.centery), 10)

def draw_arrow(screen, color, start_pos, height, is_image=False):
    """绘制箭头表示物体或像"""
    x, y = start_pos
    if not is_image:
        # 绘制箭身
        pygame.draw.line(screen, color, (x, y), (x, y - height), 3)
        # 绘制箭头
        pygame.draw.polygon(screen, color, [
            (x, y - height),  # 箭头尖端
            (x - 10, y - height + 20),  # 左侧
            (x + 10, y - height + 20)   # 右侧
        ])
    else:
        # 绘制倒立的箭头
        pygame.draw.line(screen, color, (x, y), (x, y + height), 3)
        pygame.draw.polygon(screen, color, [
            (x, y + height),  # 箭头尖端
            (x - 10, y + height - 20),  # 左侧
            (x + 10, y + height - 20)   # 右侧
        ])

def draw_lens():
    # 绘制透镜中轴线（主光轴）
    pygame.draw.line(screen, BLACK, (0, HEIGHT//2), (WIDTH, HEIGHT//2), 1)
    
    # 绘制透镜轮廓
    lens_height = 300
    lens_center_y = HEIGHT // 2
    curve_width = 30
    
    # 绘制透镜左右曲面
    points_left = []
    points_right = []
    for i in range(lens_height):
        y = lens_center_y - lens_height//2 + i
        x_offset = math.sqrt(curve_width * curve_width * (1 - ((y - lens_center_y) * (y - lens_center_y)) / ((lens_height/2) * (lens_height/2))))
        points_left.append((lens_x - x_offset, y))
        points_right.append((lens_x + x_offset, y))
    
    # 绘制透镜轮廓
    pygame.draw.lines(screen, BLACK, False, points_left, 2)
    pygame.draw.lines(screen, BLACK, False, points_right, 2)
    
    # 填充透镜区域为浅蓝色半透明
    lens_surface = pygame.Surface((curve_width * 2, lens_height))
    lens_surface.set_alpha(50)
    lens_surface.fill((200, 200, 255))
    screen.blit(lens_surface, (lens_x - curve_width, lens_center_y - lens_height//2))

    # 绘制焦点F和2F
    # F点
    pygame.draw.circle(screen, RED, (int(lens_x - focal_length * SCALE), HEIGHT//2), 4)
    pygame.draw.circle(screen, RED, (int(lens_x + focal_length * SCALE), HEIGHT//2), 4)
    # 2F点
    pygame.draw.circle(screen, RED, (int(lens_x - 2 * focal_length * SCALE), HEIGHT//2), 4)
    pygame.draw.circle(screen, RED, (int(lens_x + 2 * focal_length * SCALE), HEIGHT//2), 4)
    
    # 绘制F和2F标记
    f_text = font.render("F", True, RED)
    f2_text = font.render("2F", True, RED)
    
    # 左侧标记
    screen.blit(f_text, (lens_x - focal_length * SCALE - 10, HEIGHT//2 + 10))
    screen.blit(f2_text, (lens_x - 2 * focal_length * SCALE - 15, HEIGHT//2 + 10))
    
    # 右侧标记
    screen.blit(f_text, (lens_x + focal_length * SCALE - 10, HEIGHT//2 + 10))
    screen.blit(f2_text, (lens_x + 2 * focal_length * SCALE - 15, HEIGHT//2 + 10))

def draw_optical_path():
    # 物体位置（转换为像素）
    object_x = lens_x - object_distance * SCALE
    object_y = HEIGHT // 2
    
    # 绘制物体（箭头）
    draw_arrow(screen, BLUE, (object_x, object_y), object_height * SCALE)
    # 标注物距u
    u_text = font.render("u", True, BLUE)
    screen.blit(u_text, (lens_x - object_distance * SCALE / 2, HEIGHT//2 + 20))
    
    # 计算像距（厘米）
    if object_distance != focal_length:  # 当物距不等于焦距时才有成像
        # 根据凸透镜成像公式计算像距
        image_distance = (focal_length * object_distance) / (object_distance - focal_length)
        # 计算像高
        image_height = -(image_distance * object_height) / object_distance
        # 计算像的位置
        image_x = lens_x + image_distance * SCALE
        image_y = HEIGHT // 2
        
        # 物体顶点和底部的位置
        object_top = (object_x, object_y - object_height * SCALE)
        object_bottom = (object_x, object_y)
        
        # 像的顶点和底部位置（倒立）
        image_top = (image_x, image_y + abs(image_height) * SCALE)
        image_bottom = (image_x, image_y)
        
        # 标注像距v
        v_text = font.render("v", True, RED)
        if image_distance > 0:  # 实像
            screen.blit(v_text, (lens_x + image_distance * SCALE / 2, HEIGHT//2 + 20))
        else:  # 虚像
            screen.blit(v_text, (lens_x + image_distance * SCALE / 2, HEIGHT//2 + 20))
        
        # 绘制成像
        if object_distance > focal_length:  # 实像（当物距大于焦距时）
            draw_arrow(screen, RED, (image_x, image_y), abs(image_height) * SCALE, True)
            # 显示成像高度和位置
            height_text = font.render(f"h': {abs(image_height):.1f} cm", True, RED)
            distance_text = font.render(f"v: {abs(image_distance):.1f} cm", True, RED)
            screen.blit(height_text, (image_x + 10, image_y - 50))
            screen.blit(distance_text, (image_x + 10, image_y - 20))
            
            # 绘制三条特征光线
            # 1. 平行于主光轴的光线
            pygame.draw.line(screen, RED, object_top, (lens_x, object_top[1]), 1)  # 入射光线
            pygame.draw.line(screen, RED, (lens_x, object_top[1]), image_top, 1)  # 折射光线
            
            # 2. 通过焦点的光线
            pygame.draw.line(screen, RED, object_top, (lens_x, HEIGHT//2), 1)  # 入射光线
            pygame.draw.line(screen, RED, (lens_x, HEIGHT//2), image_top, 1)  # 折射光线
            
            # 3. 通过光心的光线（直线穿过）
            pygame.draw.line(screen, RED, object_top, image_top, 1)
            
        else:  # 虚像（当物距小于焦距时）
            draw_arrow(screen, RED, (image_x, image_y), abs(image_height) * SCALE, False)
            # 显示成像高度和位置
            height_text = font.render(f"h': {abs(image_height):.1f} cm", True, RED)
            distance_text = font.render(f"v: {abs(image_distance):.1f} cm", True, RED)
            screen.blit(height_text, (image_x + 10, image_y - 50))
            screen.blit(distance_text, (image_x + 10, image_y - 20))
            
            # 1. 平行于主光轴的光线
            pygame.draw.line(screen, RED, object_top, (lens_x, object_top[1]), 1)  # 入射光线
            # 经过焦点的折射光线
            pygame.draw.line(screen, RED, (lens_x, object_top[1]), 
                           (lens_x + focal_length * SCALE, HEIGHT//2), 1)  # 实际光线
            draw_dashed_line(screen, (lens_x, object_top[1]), image_top, RED)  # 虚线延长线
            
            # 2. 通过焦点的光线
            pygame.draw.line(screen, RED, object_top, (lens_x, HEIGHT//2), 1)  # 入射光线
            pygame.draw.line(screen, RED, (lens_x, HEIGHT//2), 
                           (lens_x + WIDTH//2, HEIGHT//2), 1)  # 平行于主光轴的实际光线
            draw_dashed_line(screen, (lens_x, HEIGHT//2), image_top, RED)  # 虚线延长线
            
            # 3. 通过光心的光线
            pygame.draw.line(screen, RED, object_top, (lens_x, HEIGHT//2), 1)  # 到光心的实线
            draw_dashed_line(screen, (lens_x, HEIGHT//2), image_top, RED)  # 虚线延长线
    else:
        # 当物距等于焦距时，显示无穷远处成像的提示
        text = font.render("成像于无穷远处", True, RED)
        screen.blit(text, (lens_x + 100, HEIGHT//2 - 30))

def draw_dashed_line(surface, start_pos, end_pos, color, dash_length=10):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx * dx + dy * dy)
    dashes = int(distance / (2 * dash_length))
    unit_x = dx / (2 * dashes)
    unit_y = dy / (2 * dashes)
    
    for i in range(dashes):
        start_x = x1 + 2 * i * unit_x
        start_y = y1 + 2 * i * unit_y
        end_x = start_x + unit_x
        end_y = start_y + unit_y
        pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), 1)

def main():
    global focal_length, object_distance, object_height, screen, WIDTH, HEIGHT
    
    # 创建滑块和输入框
    focal_slider = Slider(slider_x, focal_y, slider_width, element_height, 3, 15, focal_length)
    distance_slider = Slider(slider_x, distance_y, slider_width, element_height, 3, 30, object_distance)
    height_slider = Slider(slider_x, height_y, slider_width, element_height, 1, 10, object_height)
    
    # 创建输入框
    focal_input = InputBox(input_x, focal_y, input_width, element_height, 3, 15, focal_length)
    distance_input = InputBox(input_x, distance_y, input_width, element_height, 3, 30, object_distance)
    height_input = InputBox(input_x, height_y, input_width, element_height, 1, 10, object_height)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            
            # 处理滑块和输入框事件
            focal_slider.handle_event(event)
            distance_slider.handle_event(event)
            height_slider.handle_event(event)
            focal_input.handle_event(event)
            distance_input.handle_event(event)
            height_input.handle_event(event)
        
        # 更新参数（优先使用输入框的值）
        if focal_input.active:
            try:
                focal_length = float(focal_input.text)
                focal_slider.update(focal_length)
            except ValueError:
                pass
        else:
            focal_length = focal_slider.value
            focal_input.update(focal_length)
            
        if distance_input.active:
            try:
                object_distance = float(distance_input.text)
                distance_slider.update(object_distance)
            except ValueError:
                pass
        else:
            object_distance = distance_slider.value
            distance_input.update(object_distance)
            
        if height_input.active:
            try:
                object_height = float(height_input.text)
                height_slider.update(object_height)
            except ValueError:
                pass
        else:
            object_height = height_slider.value
            height_input.update(object_height)
        
        # 绘制
        screen.fill(WHITE)
        draw_lens()
        draw_optical_path()
        
        # 绘制标签
        focal_text = font.render(f"焦距 f:", True, BLACK)
        distance_text = font.render(f"物距 u:", True, BLACK)
        height_text = font.render(f"物高 h:", True, BLACK)
        
        # 绘制参数标签
        screen.blit(focal_text, (label_x, focal_y))
        screen.blit(distance_text, (label_x, distance_y))
        screen.blit(height_text, (label_x, height_y))
        
        # 绘制单位标签
        unit_text = font.render("cm", True, BLACK)
        screen.blit(unit_text, (unit_x, focal_y))
        screen.blit(unit_text, (unit_x, distance_y))
        screen.blit(unit_text, (unit_x, height_y))
        
        # 绘制滑块和输入框
        focal_slider.draw(screen)
        distance_slider.draw(screen)
        height_slider.draw(screen)
        focal_input.draw(screen)
        distance_input.draw(screen)
        height_input.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
