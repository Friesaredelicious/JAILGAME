import pygame
import time

# Initialize Pygame
try:
    pygame.init()
except Exception as e:
    print(f"Error initializing Pygame: {e}")
    exit()

# Screen settings
WIDTH, HEIGHT = 800, 600
try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Europe Conquest Game")
except Exception as e:
    print(f"Error setting up display: {e}")
    exit()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Load map image
try:
    map_image = pygame.image.load("europe_map.png")
    map_image = pygame.transform.scale(map_image, (WIDTH, HEIGHT))
except FileNotFoundError:
    print("Error: europe_map.png not found. Please add a map image in the same directory.")
    exit()
except Exception as e:
    print(f"Error loading map image: {e}")
    exit()

# Font
try:
    font = pygame.font.SysFont("arial", 20)
    title_font = pygame.font.SysFont("arial", 30, bold=True)
except Exception as e:
    print(f"Error loading font: {e}")
    exit()

# NEW: Message system for on-screen notifications
message = ""
message_timer = 0
MESSAGE_DURATION = 3  # Seconds to display message

# Point-in-polygon function for click detection
def point_in_polygon(point, polygon):
    x, y = point
    n = len(polygon)
    inside = False
    px, py = polygon[0]
    for i in range(n + 1):
        sx, sy = polygon[i % n]
        if y > min(py, sy) and y <= max(py, sy) and x <= max(px, sx):
            if py != sy:
                xinters = (y - py) * (sx - px) / (sy - py) + px
            if px == sx or x <= xinters:
                inside = not inside
        px, py = sx, sy
    return inside

# NEW: Function to calculate polygon centroid for text positioning
def get_polygon_centroid(polygon):
    x_sum, y_sum, area = 0, 0, 0
    n = len(polygon)
    for i in range(n):
        x0, y0 = polygon[i]
        x1, y1 = polygon[(i + 1) % n]
        cross = x0 * y1 - x1 * y0
        area += cross
        x_sum += (x0 + x1) * cross
        y_sum += (y0 + y1) * cross
    area /= 2
    if area == 0:
        return polygon[0]  # Fallback to first point if area is zero
    x_sum /= (6 * area)
    y_sum /= (6 * area)
    return (int(x_sum), int(y_sum))

# Country data: name, tax income per second, cost, polygon [(x1, y1), (x2, y2), ...]
countries = {
    "France": {
        "tax": 10,
        "cost": 100,
        "polygon": [
            (200, 300), (250, 250), (300, 250), (320, 300),
            (300, 350), (250, 400), (200, 350), (180, 320)
        ],
        "owned": False
    },
    "Germany": {
        "tax": 15,
        "cost": 150,
        "polygon": [
            (350, 200), (400, 150), (450, 150), (470, 200),
            (450, 250), (420, 300), (380, 300), (340, 250)
        ],
        "owned": False
    },
    "Spain": {
        "tax": 8,
        "cost": 80,
        "polygon": [
            (150, 400), (200, 350), (250, 350), (270, 400),
            (250, 450), (200, 450), (150, 420)
        ],
        "owned": False
    },
    "Italy": {
        "tax": 12,
        "cost": 120,
        "polygon": [
            (320, 350), (350, 300), (380, 300), (400, 350),
            (380, 400), (350, 450), (320, 400)
        ],
        "owned": False
    },
    "Poland": {
        "tax": 7,
        "cost": 70,
        "polygon": [
            (450, 200), (500, 150), (550, 150), (570, 200),
            (550, 250), (500, 300), (450, 250)
        ],
        "owned": False
    },
}

# Player data
money = 100
last_tax_time = time.time()
selected_country = None

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            selected_country = None
            for country, data in countries.items():
                if point_in_polygon(mouse_pos, data["polygon"]):
                    selected_country = country
                    if not data["owned"]:
                        if money >= data["cost"]:
                            money -= data["cost"]
                            data["owned"] = True
                            # NEW: Show purchase message on screen
                            message = f"Bought {country}!"
                            message_timer = current_time
                        else:
                            # NEW: Show error message on screen
                            message = f"Not enough money to buy {country}!"
                            message_timer = current_time
                    break

    # Collect taxes every second
    current_time = time.time()
    if current_time - last_tax_time >= 1:
        total_tax = sum(data["tax"] for data in countries.values() if data["owned"])
        money += total_tax
        last_tax_time = current_time

    # Draw
    screen.fill(WHITE)
    screen.blit(map_image, (0, 0))

    # Draw country borders and prices
    for country, data in countries.items():
        polygon = data["polygon"]
        color = GREEN if data["owned"] else RED
        pygame.draw.polygon(screen, color, polygon, 0)  # Filled
        pygame.draw.polygon(screen, BLACK, polygon, 3)  # Black outline
        if country == selected_country:
            pygame.draw.polygon(screen, YELLOW, polygon, 5)  # Yellow highlight
        # NEW: Display price for unowned countries
        if not data["owned"]:
            try:
                price_text = font.render(f"${data['cost']}", True, BLACK)
                centroid = get_polygon_centroid(polygon)
                text_rect = price_text.get_rect(center=centroid)
                screen.blit(price_text, text_rect)
            except Exception as e:
                print(f"Error rendering price for {country}: {e}")

    # Display selected country name at top center
    if selected_country:
        try:
            country_text = title_font.render(selected_country, True, BLACK)
            text_rect = country_text.get_rect(center=(WIDTH // 2, 30))
            screen.blit(country_text, text_rect)
        except Exception as e:
            print(f"Error rendering country name: {e}")

    # Display player stats
    try:
        money_text = font.render(f"Money: ${money}", True, BLACK)
        income_text = font.render(f"Income: ${sum(data['tax'] for data in countries.values() if data['owned'])}/s", True, BLACK)
        owned_text = font.render(f"Owned: {sum(1 for data in countries.values() if data['owned'])}/{len(countries)}", True, BLACK)
        screen.blit(money_text, (10, 10))
        screen.blit(income_text, (10, 40))
        screen.blit(owned_text, (10, 70))
    except Exception as e:
        print(f"Error rendering player stats: {e}")

    # NEW: Display on-screen message
    if message and current_time - message_timer < MESSAGE_DURATION:
        try:
            message_text = font.render(message, True, BLACK)
            text_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT - 30))
            screen.blit(message_text, text_rect)
        except Exception as e:
            print(f"Error rendering message: {e}")

    # Update display
    try:
        pygame.display.flip()
    except Exception as e:
        print(f"Error updating display: {e}")
    clock.tick(60)

# Quit
try:
    pygame.quit()
except Exception as e:
    print(f"Error quitting Pygame: {e}")
