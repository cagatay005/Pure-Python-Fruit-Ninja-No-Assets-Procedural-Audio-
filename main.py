import pygame
import random
import math
import os

# --- Ayarlar ---
WIDTH = 1080
HEIGHT = 720
FPS = 60
GRAVITY = 0.25
COMBO_WINDOW = 800 

# Renk Paleti
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BOMB_COLOR = (40, 40, 40)
BROWN_STEM = (101, 67, 33)
POPUP_COLOR = (255, 255, 100)
COMBO_COLOR = (0, 255, 255)
TRAIL_COLOR = (255, 255, 255)
TRAIL_GLOW = (0, 191, 255)

ICE_COLOR = (0, 255, 255)
ICE_OVERLAY = (0, 100, 200)
CRITICAL_COLOR = (255, 0, 255)
LIGHTNING_COLOR = (200, 100, 255)
BANANA_COLOR = (255, 230, 50)
HEART_COLOR = (255, 50, 50)
GOLD_COLOR = (255, 215, 0)

# Meyve Konfigürasyonu
FRUIT_CONFIG = {
    "apple": { "score": 1, "weight": 40, "radius": 40, "colors": {"body": (220, 20, 60), "light": (240, 80, 80), "leaf": (34, 139, 34)} },
    "orange": { "score": 2, "weight": 35, "radius": 42, "colors": {"body": (255, 140, 0), "dimple": (200, 100, 0)} },
    "kiwi": { "score": 5, "weight": 15, "radius": 35, "colors": {"body": (139, 69, 19), "fuzz": (100, 50, 10)} },
    "watermelon": { "score": 8, "weight": 8, "radius": 55, "colors": {"body": (0, 100, 0), "stripe": (50, 205, 50)} },
    "golden_apple": { "score": 50, "weight": 1, "radius": 30, "colors": {"body": (255, 215, 0), "glow": (255, 255, 200)} },
    "ice_fruit": { "score": 0, "weight": 2, "radius": 38, "colors": {"body": (0, 200, 255), "glow": (200, 255, 255)} },
    "banana": { "score": 0, "weight": 3, "radius": 40, "colors": {"body": (255, 230, 50), "spots": (100, 70, 20)} }
}

# --- KILIÇ MARKETİ VE ÖZELLİKLERİ ---
BLADES_DB = {
    "default": {
        "name": "Klasik", 
        "cost": 0,   
        "color": (255, 255, 255), 
        "glow": (0, 191, 255),
        "desc": "Standart kılıç.",
        "bonus_score": 0,
        "crit_bonus": 0.0,
        "combo_window_add": 0
    },
    "fire": {
        "name": "Alev",   
        "cost": 150,  
        "color": (255, 255, 0),   
        "glow": (255, 50, 0),
        "desc": "YAKICI! +2 Puan & Ahşabı Yakar.",
        "bonus_score": 2,
        "crit_bonus": 0.0,
        "combo_window_add": 0
    },
    "matrix": {
        "name": "Matrix", 
        "cost": 450, 
        "color": (200, 255, 200), 
        "glow": (0, 255, 0),
        "desc": "ZAMAN! Combo süresi uzar.",
        "bonus_score": 0,
        "crit_bonus": 0.0,
        "combo_window_add": 300
    },
    "void": {
        "name": "Void",   
        "cost": 1000, 
        "color": (50, 0, 100),    
        "glow": (200, 0, 255),
        "desc": "GÜÇ! %20 Ekstra Kritik Şansı.",
        "bonus_score": 0,
        "crit_bonus": 0.20,
        "combo_window_add": 0
    }
}

BOMB_CHANCE = 0.20
CRITICAL_CHANCE = 0.10 

pygame.mixer.pre_init(44100, -16, 2, 512) 
pygame.init()

window = pygame.display.set_mode((WIDTH, HEIGHT))
screen = pygame.Surface((WIDTH, HEIGHT)) 

pygame.display.set_caption("Fruit Ninja: Dazzling Effects Update")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Verdana", 28, bold=True)
score_font = pygame.font.SysFont("Verdana", 40, bold=True)
popup_font = pygame.font.SysFont("Verdana", 30, bold=True)
crit_font = pygame.font.SysFont("Verdana", 45, bold=True) 
combo_font = pygame.font.SysFont("Verdana", 45, bold=True)
title_font = pygame.font.SysFont("Verdana", 60, bold=True)
shop_font = pygame.font.SysFont("Verdana", 24, bold=True)

# --- Sesler ---
try:
    sound_throw = pygame.mixer.Sound("throw.wav")
    sound_squish = pygame.mixer.Sound("squish.wav") 
    sound_boom = pygame.mixer.Sound("boom.wav")
    sound_miss = pygame.mixer.Sound("miss.wav")
    sound_freeze = pygame.mixer.Sound("throw.wav")
    sound_heal = pygame.mixer.Sound("squish.wav") 
    sound_buy = pygame.mixer.Sound("squish.wav")
    
    sound_throw.set_volume(0.2); sound_squish.set_volume(0.8)
    sound_boom.set_volume(0.8); sound_miss.set_volume(0.5)
except:
    class DummySound: 
        def play(self): pass
    sound_throw = sound_squish = sound_boom = sound_miss = sound_freeze = sound_heal = sound_buy = DummySound()

# --- SIFIRLAMA ---
if os.path.exists("save.txt"):
    os.remove("save.txt")

# --- MAĞAZA ---
def draw_shop(surface, total_money, current_blade, owned_blades):
    dark = pygame.Surface((WIDTH, HEIGHT)); dark.set_alpha(220); dark.fill(BLACK)
    surface.blit(dark, (0,0))
    
    title = title_font.render("KILIÇ MAĞAZASI", True, WHITE)
    money_txt = font.render(f"Bakiye: {total_money} G", True, GOLD_COLOR)
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    surface.blit(money_txt, (WIDTH//2 - money_txt.get_width()//2, 120))
    
    start_y = 200
    buttons = [] 
    
    for i, (b_id, data) in enumerate(BLADES_DB.items()):
        y_pos = start_y + (i * 100)
        
        pygame.draw.rect(surface, data["color"], (150, y_pos, 50, 50))
        pygame.draw.rect(surface, data["glow"], (145, y_pos-5, 60, 60), 3)
        
        name_txt = shop_font.render(data["name"], True, WHITE)
        cost_txt = shop_font.render(f"{data['cost']} G", True, GOLD_COLOR)
        
        # Açıklama metni
        desc_font = pygame.font.SysFont("Verdana", 14)
        desc_txt = desc_font.render(data["desc"], True, (200, 200, 200))
        
        surface.blit(name_txt, (220, y_pos))
        surface.blit(desc_txt, (220, y_pos + 30))
        surface.blit(cost_txt, (420, y_pos + 10))
        
        status_text = ""
        btn_color = (100, 100, 100)
        text_color = WHITE
        
        if current_blade == b_id:
            status_text = "KUŞANILDI"; btn_color = (0, 200, 0); text_color = BLACK
        elif b_id in owned_blades:
            status_text = "SEÇ"; btn_color = (200, 200, 200); text_color = BLACK
        elif total_money >= data["cost"]:
            status_text = "SATIN AL"; btn_color = (200, 200, 0); text_color = BLACK
        else:
            status_text = "YETERSİZ"; btn_color = (100, 0, 0)
            
        btn_rect = pygame.Rect(580, y_pos, 160, 50)
        pygame.draw.rect(surface, btn_color, btn_rect, border_radius=10)
        
        btn_txt = shop_font.render(status_text, True, text_color)
        surface.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width()//2, btn_rect.centery - btn_txt.get_height()//2))
        
        buttons.append({"rect": btn_rect, "id": b_id, "cost": data["cost"]})
        
    esc_txt = font.render("'ESC' ile Menüye Dön", True, WHITE)
    surface.blit(esc_txt, (WIDTH//2 - esc_txt.get_width()//2, HEIGHT - 60))
    return buttons

# --- EFEKTLER ---
def draw_dynamic_trail(surface, trail_points, is_frozen, blade_id):
    if len(trail_points) < 2: return
    
    if is_frozen:
        glow_col = (0, 255, 255); core_col = (200, 255, 255)
    else:
        blade_data = BLADES_DB[blade_id]
        glow_col = blade_data["glow"]; core_col = blade_data["color"]
    
    for i in range(len(trail_points) - 1):
        progress = i / len(trail_points)
        thickness = int(15 * progress)
        if thickness > 0:
            # Daha parlak bir dış parlama için alpha blending
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(s, (glow_col[0], glow_col[1], glow_col[2], 100), trail_points[i], trail_points[i+1], thickness + 8)
            surface.blit(s, (0,0))
            pygame.draw.line(surface, glow_col, trail_points[i], trail_points[i+1], thickness + 4)
        if thickness > 2:
            pygame.draw.line(surface, core_col, trail_points[i], trail_points[i+1], thickness)

def draw_permanent_splatter(surface, x, y, color):
    splatter_size = 120
    splat_surf = pygame.Surface((splatter_size, splatter_size), pygame.SRCALPHA)
    wet_color = (color[0], color[1], color[2], 180) # Biraz daha opak
    center = splatter_size // 2
    for _ in range(15):
        bx = center + random.randint(-35, 35)
        by = center + random.randint(-35, 35)
        radius = random.randint(8, 22)
        pygame.draw.circle(splat_surf, wet_color, (bx, by), radius)
    surface.blit(splat_surf, (x - center, y - center))

def draw_burn_mark(surface, x, y):
    burn_size = 140
    burn_surf = pygame.Surface((burn_size, burn_size), pygame.SRCALPHA)
    center = burn_size // 2
    
    for _ in range(10):
        bx = center + random.randint(-30, 30)
        by = center + random.randint(-30, 30)
        r = random.randint(15, 30)
        pygame.draw.circle(burn_surf, (255, 100, 0, 50), (bx, by), r)

    for _ in range(20):
        bx = center + random.randint(-25, 25)
        by = center + random.randint(-25, 25)
        r = random.randint(10, 25)
        pygame.draw.circle(burn_surf, (30, 20, 10, 200), (bx, by), r)
    pygame.draw.circle(burn_surf, (255, 200, 100, 150), (center, center), random.randint(10, 15))

    surface.blit(burn_surf, (x - center, y - center))

def draw_lightning(surface, x, y):
    for _ in range(5): 
        start_x, start_y = x, y
        for _ in range(3): 
            end_x = start_x + random.randint(-40, 40)
            end_y = start_y + random.randint(-40, 40)
            pygame.draw.line(surface, LIGHTNING_COLOR, (start_x, start_y), (end_x, end_y), 4)
            pygame.draw.line(surface, WHITE, (start_x, start_y), (end_x, end_y), 2)
            start_x, start_y = end_x, end_y

def draw_menu(surface, high_score, total_money):
    dark = pygame.Surface((WIDTH, HEIGHT)); dark.set_alpha(100); dark.fill(BLACK)
    surface.blit(dark, (0,0))
    title = title_font.render("FRUIT NINJA", True, (255, 200, 0))
    subtitle = font.render("SPACE: Oyna  |  M: Mağaza", True, WHITE)
    best = font.render(f"En İyi: {high_score}", True, (0, 255, 255))
    money = font.render(f"Para: {total_money} G", True, GOLD_COLOR)
    
    surface.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3 - 20))
    surface.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2))
    surface.blit(best, (WIDTH//2 - best.get_width()//2, HEIGHT//2 + 60))
    surface.blit(money, (WIDTH//2 - money.get_width()//2, HEIGHT//2 + 110))

def draw_pause_screen(surface):
    dark = pygame.Surface((WIDTH, HEIGHT)); dark.set_alpha(150); dark.fill(BLACK)
    surface.blit(dark, (0,0))
    pause_text = title_font.render("DURAKLATILDI", True, WHITE)
    resume_text = font.render("Devam etmek için 'P' tuşuna bas", True, (200, 200, 200))
    surface.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 30))
    surface.blit(resume_text, (WIDTH//2 - resume_text.get_width()//2, HEIGHT//2 + 50))

def draw_leaf(surface, x, y, color):
    leaf_points = [(x, y), (x+15, y-10), (x+25, y-5), (x+15, y+5)]
    pygame.draw.polygon(surface, color, leaf_points)
    pygame.draw.polygon(surface, (0,0,0), leaf_points, 1)

def create_fruit_surface(f_type, radius):
    s_size = radius * 2 + 20 
    surface = pygame.Surface((s_size, s_size), pygame.SRCALPHA)
    cx, cy = s_size // 2, s_size // 2 
    data = FRUIT_CONFIG.get(f_type, {})
    cols = data.get("colors", {})

    if f_type == "apple":
        pygame.draw.circle(surface, (180, 0, 0), (cx, cy+3), radius)
        pygame.draw.circle(surface, cols["body"], (cx, cy), radius)
        pygame.draw.ellipse(surface, (255, 255, 255, 100), (cx-radius//2, cy-radius//2, radius//1.5, radius//2.5))
        pygame.draw.line(surface, BROWN_STEM, (cx, cy-radius+5), (cx, cy-radius-10), 4)
        draw_leaf(surface, cx, cy-radius-10, cols["leaf"])
    elif f_type == "orange":
        pygame.draw.circle(surface, (200, 100, 0), (cx, cy+2), radius)
        pygame.draw.circle(surface, cols["body"], (cx, cy), radius)
        for _ in range(15):
            ox = cx + random.randint(-radius+5, radius-5)
            oy = cy + random.randint(-radius+5, radius-5)
            if math.hypot(ox-cx, oy-cy) < radius - 5: pygame.draw.circle(surface, cols["dimple"], (ox, oy), 2)
        pygame.draw.circle(surface, (50, 100, 0), (cx, cy-radius+2), 4)
    elif f_type == "kiwi":
        pygame.draw.circle(surface, (100, 50, 10), (cx, cy), radius)
        pygame.draw.circle(surface, cols["body"], (cx, cy), radius-2)
        for _ in range(30):
            kx = cx + random.randint(-radius, radius)
            ky = cy + random.randint(-radius, radius)
            if math.hypot(kx-cx, ky-cy) < radius: pygame.draw.line(surface, cols["fuzz"], (kx, ky), (kx+2, ky+2), 1)
    elif f_type == "watermelon":
        pygame.draw.circle(surface, cols["body"], (cx, cy), radius)
        for i in range(-2, 3):
            pygame.draw.arc(surface, cols["stripe"], (cx - radius + (i*10), cy - radius, radius*2, radius*2), 0, 3.14, 4)
    elif f_type == "golden_apple":
        pygame.draw.circle(surface, (255, 255, 200, 100), (cx, cy), radius+5)
        pygame.draw.circle(surface, cols["body"], (cx, cy), radius)
        pygame.draw.circle(surface, (255, 255, 255), (cx-10, cy-10), 8)
    elif f_type == "ice_fruit":
        pygame.draw.circle(surface, (200, 255, 255), (cx, cy), radius)
        pygame.draw.circle(surface, cols["body"], (cx, cy), radius-4)
        for i in range(0, 360, 45):
            rad = math.radians(i)
            tx = cx + math.cos(rad) * (radius - 10)
            ty = cy + math.sin(rad) * (radius - 10)
            pygame.draw.line(surface, (255, 255, 255), (cx, cy), (tx, ty), 2)
    elif f_type == "banana":
        pygame.draw.circle(surface, cols["body"], (cx, cy), radius)
        for _ in range(5):
             bx = cx + random.randint(-20, 20)
             by = cy + random.randint(-20, 20)
             pygame.draw.circle(surface, cols["spots"], (bx, by), 2)
        pygame.draw.circle(surface, (100, 80, 20), (cx - 15, cy - radius + 5), 4)
    return surface

def create_wood_background():
    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill((85, 55, 30))
    for y in range(0, HEIGHT, 100):
        pygame.draw.line(bg, (65, 40, 20), (0, y), (WIDTH, y), 5)
    return bg

background_surface = create_wood_background()

# --- SINIFLAR ---
class ComboPopup:
    def __init__(self, x, y, count):
        self.x = x; self.y = y
        self.text_surf = combo_font.render(f"x{count} COMBO", True, COMBO_COLOR)
        self.outline_surf = combo_font.render(f"x{count} COMBO", True, BLACK)
        self.timer = 50; self.y_speed = -3 
    def update(self):
        self.y += self.y_speed; self.timer -= 1
        return self.timer > 0
    def draw(self):
        rect = self.text_surf.get_rect(center=(self.x, self.y))
        screen.blit(self.outline_surf, (rect.x + 3, rect.y + 3))
        screen.blit(self.text_surf, rect)

class ScorePopup:
    def __init__(self, x, y, points_or_text, color=POPUP_COLOR, is_critical=False):
        self.x = x; self.y = y; self.is_critical = is_critical
        fnt = crit_font if is_critical else popup_font
        txt = str(points_or_text)
        if isinstance(points_or_text, int):
             txt = f"CRITICAL +{points_or_text}" if is_critical else f"+{points_or_text}"
        col = CRITICAL_COLOR if is_critical else color
        self.text_surf = fnt.render(txt, True, col)
        if is_critical: self.outline_surf = fnt.render(txt, True, WHITE)
        self.timer = 80 if is_critical else 60
        self.y_speed = -1 if is_critical else -2
        self.alpha = 255
    def update(self):
        self.y += self.y_speed; self.timer -= 1
        if self.timer < 20:
            self.alpha = int((self.timer / 20) * 255)
            self.text_surf.set_alpha(self.alpha)
            if self.is_critical: self.outline_surf.set_alpha(self.alpha)
        return self.timer > 0
    def draw(self):
        rect = self.text_surf.get_rect(center=(self.x, self.y))
        if self.is_critical: screen.blit(self.outline_surf, (rect.x + 2, rect.y + 2))
        screen.blit(self.text_surf, rect)

class Fruit:
    def __init__(self, fruit_type):
        self.x = random.randint(100, WIDTH - 100)
        self.y = HEIGHT + 50
        self.speed_x = random.randint(-4, 4)
        if fruit_type == "golden_apple": self.speed_y = random.randint(-22, -18)
        else: self.speed_y = random.randint(-19, -14)
        self.type = fruit_type
        self.active = True
        self.angle = 0
        self.rot_speed = random.uniform(-5, 5)
        if random.random() < 0.3: sound_throw.play()
        if self.type == "bomb":
            self.radius = 35; self.points = 0; self.inner_color = (50, 50, 50)
        else:
            data = FRUIT_CONFIG[self.type]
            self.radius = data["radius"]; self.points = data["score"]
            self.inner_color = (200, 200, 200)
            if "body" in data["colors"]: self.inner_color = data["colors"]["body"]
            self.original_image = create_fruit_surface(self.type, self.radius)
            self.image = self.original_image
            w = self.original_image.get_width(); h = self.original_image.get_height()
            self.image_left = self.original_image.subsurface(pygame.Rect(0, 0, w//2, h))
            self.image_right = self.original_image.subsurface(pygame.Rect(w//2, 0, w//2, h))
    def update(self, time_scale=1.0):
        self.x += self.speed_x * time_scale
        self.y += self.speed_y * time_scale
        self.speed_y += GRAVITY * time_scale
        self.angle += self.rot_speed * time_scale
        if self.y > HEIGHT + 100: self.active = False; return "dropped"
        return "active"
    def draw(self):
        if self.active:
            if self.type == "bomb":
                pygame.draw.circle(screen, (0,0,0), (int(self.x+3), int(self.y+3)), self.radius)
                pygame.draw.circle(screen, BOMB_COLOR, (int(self.x), int(self.y)), self.radius)
                off = 15
                pygame.draw.line(screen, (200, 0, 0), (self.x - off, self.y - off), (self.x + off, self.y + off), 5)
                pygame.draw.line(screen, (200, 0, 0), (self.x + off, self.y - off), (self.x - off, self.y + off), 5)
                if pygame.time.get_ticks() % 200 < 100: pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y - self.radius - 5)), 5)
            else:
                rotated_image = pygame.transform.rotate(self.original_image, self.angle)
                new_rect = rotated_image.get_rect(center=(self.x, self.y))
                screen.blit(rotated_image, new_rect.topleft)
    def check_collision(self, mouse_pos):
        dist = math.sqrt((self.x - mouse_pos[0])**2 + (self.y - mouse_pos[1])**2)
        return dist <= self.radius

class SlicedFruit:
    def __init__(self, x, y, image, initial_angle, velocity_x):
        self.x = x; self.y = y; self.original_image = image
        self.angle = initial_angle; self.speed_x = velocity_x
        self.speed_y = random.uniform(-5, -2); self.rot_speed = random.uniform(-10, 10); self.active = True
    def update(self, time_scale=1.0):
        self.x += self.speed_x * time_scale
        self.y += self.speed_y * time_scale
        self.speed_y += GRAVITY * time_scale
        self.angle += self.rot_speed * time_scale
        if self.y > HEIGHT + 100: self.active = False; return False
        return True
    def draw(self):
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        new_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, new_rect.topleft)

class Particle:
    def __init__(self, x, y, color, is_chunk=False, p_type="default"):
        self.x, self.y = x, y; self.color = color; self.is_chunk = is_chunk
        self.p_type = p_type
        self.speed_x = random.uniform(-6, 6); self.speed_y = random.uniform(-6, 6)
        self.radius = random.randint(8, 12) if is_chunk else random.randint(3, 6)
        self.timer = 50 if is_chunk else 30
        
        # Özel parçacık ayarları
        if self.p_type == "spark":
            self.radius = random.randint(1, 3)
            self.timer = random.randint(10, 20)
            self.speed_x *= 1.5; self.speed_y *= 1.5
        elif self.p_type == "smoke":
            self.radius = random.randint(10, 20)
            self.timer = random.randint(40, 60)
            self.speed_y = random.uniform(-2, -0.5) # Yavaşça yüksel
            self.speed_x = random.uniform(-1, 1)

    def update(self, time_scale=1.0):
        self.x += self.speed_x * time_scale
        self.y += self.speed_y * time_scale
        
        if self.p_type != "smoke":
             self.speed_y += GRAVITY * time_scale
        
        self.timer -= 1

    def draw(self):
        if self.timer > 0:
            scale = self.timer / (50 if self.is_chunk else 30)
            if self.p_type == "smoke": scale = self.timer / 60

            r = int(self.radius * scale)
            if r > 0:
                draw_pos = (int(self.x), int(self.y))
                if self.p_type == "spark":
                     # Kıvılcımlar parlak çizgiler gibi görünür
                     end_pos = (int(self.x - self.speed_x), int(self.y - self.speed_y))
                     pygame.draw.line(screen, self.color, draw_pos, end_pos, 2)
                elif self.p_type == "smoke":
                     # Duman için şeffaf daire
                     s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                     pygame.draw.circle(s, (self.color[0], self.color[1], self.color[2], 100), (r, r), r)
                     screen.blit(s, (self.x-r, self.y-r))
                else:
                    pygame.draw.circle(screen, self.color, draw_pos, r)

def create_splash_effect(x, y, color, particles_list):
    for _ in range(5): particles_list.append(Particle(x, y, color, is_chunk=True))
    for _ in range(15): 
        lc = (min(color[0]+30, 255), min(color[1]+30, 255), min(color[2]+30, 255))
        particles_list.append(Particle(x, y, lc, is_chunk=False))

def create_blade_particles(x, y, blade_type, particles_list):
    if blade_type == "fire":
        # Ana ateş topları
        for _ in range(10):
            p = Particle(x, y, (255, random.randint(50, 150), 0), is_chunk=False)
            p.speed_y = random.uniform(-6, -2) 
            particles_list.append(p)
        # Kıvılcımlar (Hızlı, parlak sarı/beyaz)
        for _ in range(15):
            p = Particle(x, y, (255, 255, random.randint(0, 100)), p_type="spark")
            particles_list.append(p)
        # Duman (Yavaş yükselen gri)
        for _ in range(5):
             p = Particle(x, y, (50, 50, 50), p_type="smoke")
             particles_list.append(p)
            
    elif blade_type == "matrix":
        # Dijital kareler
        for _ in range(12):
            col = (0, random.randint(150, 255), 50)
            p = Particle(x, y, col, is_chunk=False)
            p.radius = random.randint(2, 5)
            p.speed_x = random.choice([-4, -2, 2, 4])
            p.speed_y = random.choice([-4, -2, 2, 4])
            particles_list.append(p)

    elif blade_type == "void":
        for _ in range(15):
            p = Particle(x, y, (random.randint(50, 100), 0, random.randint(150, 255)), is_chunk=False)
            p.radius = random.randint(4, 8)
            p.speed_x = random.uniform(-8, 8)
            p.speed_y = random.uniform(-8, 8)
            particles_list.append(p)

def game_loop():
    global background_surface
    running = True
    GAME_STATE = "MENU"
    score = 0; lives = 3
    fruits = []; particles = []; mouse_trail = []; popups = []; sliced_fruits = []
    spawn_timer = 0; combo_count = 0; last_hit_time = 0; shake_timer = 0
    freeze_timer = 0; time_scale = 1.0; base_spawn_rate = 35
    lightning_effects = [] 

    background_surface = create_wood_background() 
    fruit_types = list(FRUIT_CONFIG.keys())
    fruit_weights = [FRUIT_CONFIG[k]["weight"] for k in fruit_types]
    
    # Başlangıç Değerleri
    high_score = 0
    total_money = 0
    current_blade = "default"
    owned_blades = ["default"]

    while running:
        clock.tick(FPS)
        screen.blit(background_surface, (0, 0))

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: running = False
            
            if GAME_STATE == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        GAME_STATE = "PLAYING"
                        score = 0; lives = 3; fruits.clear(); particles.clear()
                        sliced_fruits.clear(); popups.clear(); lightning_effects.clear()
                        background_surface = create_wood_background() 
                        freeze_timer = 0
                    elif event.key == pygame.K_m:
                        GAME_STATE = "SHOP"
            
            elif GAME_STATE == "SHOP":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    GAME_STATE = "MENU"
            
            elif GAME_STATE == "PLAYING":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    GAME_STATE = "PAUSED"; pygame.mixer.pause()
            
            elif GAME_STATE == "PAUSED":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    GAME_STATE = "PLAYING"; pygame.mixer.unpause()
            
            elif GAME_STATE == "GAME_OVER":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    GAME_STATE = "MENU"

        # --- STATE LOGIC ---
        if GAME_STATE == "MENU":
            spawn_timer += 1
            if spawn_timer > 35: 
                spawn_timer = 0
                sel = random.choices(fruit_types, weights=fruit_weights, k=1)[0]
                fruits.append(Fruit(sel))
            for f in fruits[:]:
                f.update()
                if not f.active: fruits.remove(f)
                else: f.draw()
            draw_menu(screen, high_score, total_money)
            m_pos = pygame.mouse.get_pos()
            mouse_trail.append(m_pos)
            if len(mouse_trail) > 9: mouse_trail.pop(0)
            if len(mouse_trail) > 1: draw_dynamic_trail(screen, mouse_trail, False, current_blade)

        elif GAME_STATE == "SHOP":
            shop_buttons = draw_shop(screen, total_money, current_blade, owned_blades)
            if pygame.mouse.get_pressed()[0]:
                m_pos = pygame.mouse.get_pos()
                for btn in shop_buttons:
                    if btn["rect"].collidepoint(m_pos):
                        b_id = btn["id"]
                        cost = btn["cost"]
                        if current_blade == b_id: pass
                        elif b_id in owned_blades:
                            current_blade = b_id
                            sound_buy.play(); pygame.time.delay(200)
                        elif total_money >= cost:
                            total_money -= cost
                            owned_blades.append(b_id)
                            current_blade = b_id
                            sound_buy.play(); pygame.time.delay(200)

        elif GAME_STATE == "PLAYING":
            current_spawn_rate = max(15, base_spawn_rate - (score // 50))
            if freeze_timer > 0:
                freeze_timer -= 1
                time_scale = 0.3 
                ice_overlay = pygame.Surface((WIDTH, HEIGHT)); ice_overlay.set_alpha(50 + int(random.random()*20)); ice_overlay.fill(ICE_OVERLAY)
                screen.blit(ice_overlay, (0,0))
                if freeze_timer < 60:
                     f_txt = font.render("FREEZE ENDING!", True, (255, 0, 0))
                     screen.blit(f_txt, (WIDTH//2 - 100, HEIGHT//2))
            else: time_scale = 1.0

            spawn_timer += 1
            if spawn_timer > current_spawn_rate: 
                spawn_timer = 0
                if random.random() < BOMB_CHANCE: fruits.append(Fruit("bomb"))
                else:
                    sel = random.choices(fruit_types, weights=fruit_weights, k=1)[0]
                    fruits.append(Fruit(sel))

            m_pos = pygame.mouse.get_pos()
            m_press = pygame.mouse.get_pressed()[0]
            if m_press:
                mouse_trail.append(m_pos)
                if len(mouse_trail) > 9: mouse_trail.pop(0)
            else: mouse_trail.clear()

            for f in fruits[:]:
                status = f.update(time_scale)
                if status == "dropped":
                    if f.type != "bomb" and f.type != "ice_fruit" and f.type != "banana":
                        lives -= 1; sound_miss.play()
                        if lives <= 0: 
                            GAME_STATE = "GAME_OVER"; sound_boom.play(); shake_timer = 20
                            if score > high_score: high_score = score
                            total_money += (score // 10)
                        combo_count = 0 
                    fruits.remove(f)
                elif not f.active: fruits.remove(f)
                elif m_press and f.check_collision(m_pos):
                    # --- KILIÇ EFEKTLERİ UYGULAMA ---
                    blade_stats = BLADES_DB[current_blade]
                    
                    # Gelişmiş parçacıklar
                    create_blade_particles(f.x, f.y, current_blade, particles)

                    # --- ALEV KILICI AHŞABI YAKAR ---
                    if current_blade == "fire":
                        draw_burn_mark(background_surface, f.x, f.y)

                    if f.type == "bomb":
                        shake_timer = 30; sound_boom.play(); pygame.display.flip(); pygame.time.delay(100)
                        GAME_STATE = "GAME_OVER"; screen.fill(WHITE); pygame.display.flip()
                        if score > high_score: high_score = score
                        total_money += (score // 10)
                        
                    elif f.type == "banana":
                        lives = min(3, lives + 1)
                        popups.append(ScorePopup(f.x, f.y, "EXTRA LIFE!", HEART_COLOR))
                        sound_heal.play()
                        create_splash_effect(f.x, f.y, f.inner_color, particles)
                        sliced_fruits.append(SlicedFruit(f.x, f.y, f.image_left, f.angle, -5))
                        sliced_fruits.append(SlicedFruit(f.x, f.y, f.image_right, f.angle, 5))
                        fruits.remove(f)
                        
                    elif f.type == "ice_fruit":
                        freeze_timer = 300; score += 0
                        popups.append(ScorePopup(f.x, f.y, "FREEZE!", ICE_COLOR))
                        sound_freeze.play()
                        create_splash_effect(f.x, f.y, f.inner_color, particles)
                        sliced_fruits.append(SlicedFruit(f.x, f.y, f.image_left, f.angle, -5))
                        sliced_fruits.append(SlicedFruit(f.x, f.y, f.image_right, f.angle, 5))
                        fruits.remove(f)
                        
                    else:
                        current_time = pygame.time.get_ticks()
                        
                        # --- MATRIX KILICI: COMBO UZATMA ---
                        actual_window = COMBO_WINDOW + blade_stats["combo_window_add"]
                        
                        if current_time - last_hit_time < actual_window: combo_count += 1
                        else: combo_count = 1 
                        last_hit_time = current_time
                        
                        extra_points = 0
                        if combo_count >= 3:
                            extra_points = combo_count
                            popups.append(ComboPopup(f.x, f.y - 50, combo_count))
                        
                        is_crit = False
                        # --- ALEV KILICI: BONUS PUAN ---
                        points_to_add = f.points + extra_points + blade_stats["bonus_score"]
                        
                        # --- VOID KILICI: KRİTİK ŞANS ---
                        current_crit_chance = CRITICAL_CHANCE + blade_stats["crit_bonus"]
                        
                        if random.random() < current_crit_chance:
                            is_crit = True
                            points_to_add *= 5 
                            shake_timer = 5 
                            lightning_effects.append([f.x, f.y, 10])
                        
                        score += points_to_add
                        popups.append(ScorePopup(f.x, f.y, points_to_add, is_critical=is_crit))
                        
                        sound_squish.play()
                        create_splash_effect(f.x, f.y, f.inner_color, particles)
                        draw_permanent_splatter(background_surface, f.x, f.y, f.inner_color)
                        sliced_fruits.append(SlicedFruit(f.x, f.y, f.image_left, f.angle, -5))
                        sliced_fruits.append(SlicedFruit(f.x, f.y, f.image_right, f.angle, 5))
                        fruits.remove(f)

            for p in particles[:]:
                p.update(time_scale); 
                if p.timer <= 0: particles.remove(p) 
                else: p.draw()
            for sf in sliced_fruits[:]:
                if not sf.update(time_scale): sliced_fruits.remove(sf)
                else: sf.draw()
            for f in fruits: f.draw()
            
            for l in lightning_effects[:]:
                draw_lightning(screen, l[0], l[1])
                l[2] -= 1
                if l[2] <= 0: lightning_effects.remove(l)

            popups = [p for p in popups if p.update()]
            for p in popups: p.draw()
            if len(mouse_trail) > 1: draw_dynamic_trail(screen, mouse_trail, (freeze_timer>0), current_blade)

            ui_bg = pygame.Surface((220, 100)); ui_bg.set_alpha(100); ui_bg.fill((0,0,0))
            screen.blit(ui_bg, (10, 10))
            screen.blit(score_font.render(f"Skor: {score}", True, (255, 215, 0)), (20, 20))
            best_txt = font.render(f"Best: {high_score}", True, (0, 200, 200))
            screen.blit(best_txt, (20, 60))
            for i in range(3):
                c = (255, 50, 50) if i < lives else (100, 100, 100)
                screen.blit(font.render("X", True, c), (WIDTH - 50 - (i * 40), 20))
            if combo_count > 1:
                combo_text = font.render(f"Combo: {combo_count}", True, COMBO_COLOR)
                screen.blit(combo_text, (WIDTH - 180, 80))

        elif GAME_STATE == "PAUSED":
            for p in particles: p.draw()
            for sf in sliced_fruits: sf.draw()
            for f in fruits: f.draw()
            for p in popups: p.draw()
            if len(mouse_trail) > 1: draw_dynamic_trail(screen, mouse_trail, False, current_blade)
            ui_bg = pygame.Surface((220, 100)); ui_bg.set_alpha(100); ui_bg.fill((0,0,0))
            screen.blit(ui_bg, (10, 10))
            screen.blit(score_font.render(f"Skor: {score}", True, (255, 215, 0)), (20, 20))
            best_txt = font.render(f"Best: {high_score}", True, (0, 200, 200))
            screen.blit(best_txt, (20, 60))
            for i in range(3):
                c = (255, 50, 50) if i < lives else (100, 100, 100)
                screen.blit(font.render("X", True, c), (WIDTH - 50 - (i * 40), 20))
            draw_pause_screen(screen)

        elif GAME_STATE == "GAME_OVER":
            dark = pygame.Surface((WIDTH, HEIGHT)); dark.set_alpha(180); dark.fill(BLACK)
            screen.blit(dark, (0,0))
            t1 = score_font.render("OYUN BİTTİ!", True, (255, 50, 50))
            t2 = font.render(f"Skorun: {score}", True, WHITE)
            earned = score // 10
            t_money = font.render(f"Kazanılan: +{earned} G", True, GOLD_COLOR)
            t3 = font.render(f"En İyi: {high_score}", True, (0, 255, 255))
            t4 = font.render("'R' tuşuna basarak Menüye Dön", True, (100, 255, 100))
            screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 100))
            screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 - 40))
            screen.blit(t_money, (WIDTH//2 - t_money.get_width()//2, HEIGHT//2))
            screen.blit(t3, (WIDTH//2 - t3.get_width()//2, HEIGHT//2 + 40))
            screen.blit(t4, (WIDTH//2 - t4.get_width()//2, HEIGHT//2 + 100))

        render_offset = (0, 0)
        if shake_timer > 0:
            shake_timer -= 1
            render_offset = (random.randint(-8, 8), random.randint(-8, 8))
        window.blit(screen, render_offset)
        
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    game_loop()
