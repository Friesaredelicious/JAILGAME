import pygame
import time
from datetime import datetime, timedelta

# Initialize Pygame
try:
    pygame.init()
except Exception as e:
    print(f"Error initializing Pygame: {e}")
    exit()

# Screen settings (fixed windowed)
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
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)

# Load map image
try:
    map_image = pygame.image.load("europe_map.png")
    map_image = pygame.transform.scale(map_image, (WIDTH, HEIGHT))
except FileNotFoundError:
    print("Error: europe_map.png not found. Please add a map image.")
    exit()
except Exception as e:
    print(f"Error loading map image: {e}")
    exit()

# Fonts (reduced sizes to ensure text fits)
try:
    font = pygame.font.SysFont("arial", 14)  # Smaller for buttons/panels
    dialog_font = pygame.font.SysFont("arial", 12)  # Smaller for dialogs
    title_font = pygame.font.SysFont("arial", 24, bold=True)  # Smaller for titles
except Exception as e:
    print(f"Error loading font: {e}")
    exit()

# Message system
message = ""
message_timer = 0
MESSAGE_DURATION = 3

# Confirmation dialog states
confirmation_active = False
confirmation_country = None
first_purchase = True
buy_gang_first_confirm = False
buy_gang_second_confirm = False
sell_gang_confirm = False
member_to_sell = None
cancel_business_confirm = False
cancel_business_index = None
borrow_confirm_active = False  # New: Verification for borrowing
borrow_amount = 0  # New: Track borrow amount for confirmation

# Panel and dialog states
panel_active = False
panel_country = None
gang_panel_active = False
current_gang_tab = "Members"
gang_panel_pos = [500, 150]
choose_business_dialog = False
assign_business_dialog = False
business_to_assign = None
last_business_income_time = time.time()
borrow_money_dialog = False
change_location_dialog = False
assign_member_dialog = False
member_to_assign = None
paused = False
profile_dialog = False
profile_member = None
profile_member_index = None
profile_member_country = None
relocate_business_dialog = False
business_to_relocate = None

# Country data
countries = {
    "France": {
        "cost": 150,
        "population": 67000,
        "gang_members": 0,
        "business_income": 0,
        "polygon": [
            (180, 320), (185, 300), (195, 280), (210, 270), (230, 260), (250, 255), (270, 260),
            (290, 270), (310, 280), (320, 300), (325, 320), (320, 340), (310, 360), (290, 380),
            (270, 400), (250, 410), (230, 405), (210, 400), (190, 390), (180, 370), (175, 350),
            (175, 330), (180, 320)
        ],
        "owned": False
    },
    "Germany": {
        "cost": 225,
        "population": 84000,
        "gang_members": 0,
        "business_income": 0,
        "polygon": [
            (340, 250), (350, 230), (360, 210), (380, 190), (400, 180), (420, 175), (440, 180),
            (460, 190), (470, 210), (465, 230), (460, 250), (450, 270), (440, 290), (420, 310),
            (400, 320), (380, 315), (360, 300), (350, 280), (340, 260), (340, 250)
        ],
        "owned": False
    },
    "Spain": {
        "cost": 120,
        "population": 47000,
        "gang_members": 0,
        "business_income": 0,
        "polygon": [
            (140, 420), (150, 400), (160, 380), (170, 360), (190, 350), (210, 345), (230, 350),
            (250, 360), (270, 380), (280, 400), (275, 420), (260, 440), (240, 450), (220, 460),
            (200, 465), (180, 460), (160, 450), (145, 440), (140, 420)
        ],
        "owned": False
    },
    "Italy": {
        "cost": 180,
        "population": 59000,
        "gang_members": 0,
        "business_income": 0,
        "polygon": [
            (310, 400), (320, 380), (330, 360), (340, 340), (350, 320), (360, 300), (380, 290),
            (400, 300), (410, 320), (405, 340), (400, 360), (390, 380), (380, 400), (370, 420),
            (360, 440), (350, 460), (340, 450), (330, 430), (320, 410), (310, 400)
        ],
        "owned": False
    },
    "Poland": {
        "cost": 105,
        "population": 38000,
        "gang_members": 0,
        "business_income": 0,
        "polygon": [
            (440, 250), (450, 230), (460, 210), (480, 200), (500, 195), (520, 200), (540, 210),
            (550, 230), (555, 250), (550, 270), (540, 290), (520, 300), (500, 305), (480, 300),
            (460, 290), (450, 280), (440, 260), (440, 250)
        ],
        "owned": False
    },
}

# Player data
money = 0
gang_members = []
country_gang_members = {country: [] for country in countries}
reputation = 0
bank_debt = 0
bank_interest = 0  # New: Track total interest owed
first_bought_country = None
selected_country = None
business_to_assign = None

# Interest rates for borrowing (logical, not random)
# Interest is charged per second when debt > 0, scaled by amount
BORROW_INTEREST_RATES = {
    100: 0.001,    # 0.1% per second (~$0.10/s for $100)
    500: 0.0015,   # 0.15% per second (~$0.75/s for $500)
    1000: 0.002,   # 0.2% per second (~$2/s for $1000)
    5000: 0.0025,  # 0.25% per second (~$12.50/s for $5000)
    10000: 0.003,  # 0.3% per second (~$30/s for $10000)
}
last_interest_time = time.time()  # Track when interest was last applied

# Business tracking
country_business = {country: None for country in countries}
active_businesses = []
# Business income rates (per second, base rate)
BUSINESS_INCOME_RATES = {
    "Gun Production": 100,
    "Local Business Takeover": 50,
    "Drug Production": 150,
    "Tax Frauds": 75,
}

# Date system
start_date = datetime(2010, 12, 2)
last_date_update = time.time()
current_date = start_date
DATE_UPDATE_INTERVAL = 5

# Button rectangles (moved gang/bank buttons down with spacing)
gang_button = pygame.Rect(10, 150, 100, 40)  # Moved down to y=150
bank_button = pygame.Rect(10, 210, 100, 40)  # y=150+40+20 (gap)
pause_button = pygame.Rect(10, HEIGHT - 50, 100, 40)  # Bottom-left
# Column rectangles for upper main panel
col_width = 140
col1_rect = pygame.Rect(50, 10, col_width, 50)  # Money
col2_rect = pygame.Rect(50 + col_width, 10, col_width, 50)  # Bank Debt
col3_rect = pygame.Rect(50 + col_width * 2, 10, col_width, 50)  # Reputation
col4_rect = pygame.Rect(50 + col_width * 3, 10, col_width, 50)  # Owned Territory
col5_rect = pygame.Rect(50 + col_width * 4, 10, col_width, 50)  # Date
# Profile dialog buttons
profile_close_button = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 60, 80, 30)
unassign_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 80, 30)
sell_profile_button = pygame.Rect(WIDTH // 2 - 10, HEIGHT // 2 + 60, 80, 30)  # New: Sell button in profile

# Point-in-polygon function
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

# Centroid function
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
        return polygon[0]
    x_sum /= (6 * area)
    y_sum /= (6 * area)
    return (int(x_sum), int(y_sum))

# Update date
def update_date(current_time):
    global current_date, last_date_update
    if current_time - last_date_update >= DATE_UPDATE_INTERVAL:
        days_to_add = int((current_time - last_date_update) / DATE_UPDATE_INTERVAL)
        current_date += timedelta(days=days_to_add)
        last_date_update = current_time
    return current_date.strftime("%d.%m.%Y")
# Game loop
running = True
clock = pygame.time.Clock()
while running:
    # Define confirmation dialog buttons
    first_confirm_yes = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 80, 30)
    first_confirm_no = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 50, 80, 30)
    second_confirm_yes = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 80, 30)
    second_confirm_no = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 50, 80, 30)
    sell_confirm_yes = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 80, 30)
    sell_confirm_no = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 50, 80, 30)
    cancel_business_yes = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 80, 30)
    cancel_business_no = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 50, 80, 30)
    yes_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 80, 30)
    no_button = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 50, 80, 30)
    gun_button = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 - 20, 150, 25)
    local_button = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 + 10, 150, 25)
    drug_button = pygame.Rect(WIDTH // 2 + 30, HEIGHT // 2 - 20, 150, 25)
    tax_button = pygame.Rect(WIDTH // 2 + 30, HEIGHT // 2 + 10, 150, 25)
    borrow_100 = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 - 40, 80, 25)
    borrow_500 = pygame.Rect(WIDTH // 2 - 90, HEIGHT // 2 - 40, 80, 25)
    borrow_1000 = pygame.Rect(WIDTH // 2, HEIGHT // 2 - 40, 80, 25)
    borrow_5000 = pygame.Rect(WIDTH // 2 - 135, HEIGHT // 2 + 10, 80, 25)
    borrow_10000 = pygame.Rect(WIDTH // 2 - 45, HEIGHT // 2 + 10, 80, 25)
    borrow_cancel = pygame.Rect(WIDTH // 2 - 135, HEIGHT // 2 + 60, 80, 25)
    pay_debt_button = pygame.Rect(WIDTH // 2 - 45, HEIGHT // 2 + 60, 80, 25)
    borrow_confirm_yes = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 80, 30)  # New: Borrow confirmation
    borrow_confirm_no = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 50, 80, 30)
    panel_close_button = pygame.Rect(670, 350, 80, 25)
    panel_buy_button = pygame.Rect(510, 350, 80, 25)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if pause_button.collidepoint(mouse_pos):
                paused = not paused
                message = "Paused" if paused else "Resumed"
                message_timer = time.time()
            if paused:
                continue

            if confirmation_active:
                if yes_button.collidepoint(mouse_pos):
                    if confirmation_country:
                        data = countries[confirmation_country]
                        cost = 0 if first_purchase else data["cost"]
                        if money >= cost:
                            money -= cost
                            data["owned"] = True
                            message = f"Bought {confirmation_country}!"
                            message_timer = time.time()
                            if first_purchase:
                                first_purchase = False
                                first_bought_country = confirmation_country
                        else:
                            message = f"Not enough money to buy {confirmation_country}!"
                            message_timer = time.time()
                        confirmation_active = False
                        confirmation_country = None
                elif no_button.collidepoint(mouse_pos):
                    confirmation_active = False
                    confirmation_country = None
            elif buy_gang_first_confirm:
                if first_confirm_yes.collidepoint(mouse_pos):
                    buy_gang_first_confirm = False
                    buy_gang_second_confirm = True
                elif first_confirm_no.collidepoint(mouse_pos):
                    buy_gang_first_confirm = False
            elif buy_gang_second_confirm:
                if second_confirm_yes.collidepoint(mouse_pos):
                    if money >= 150:
                        money -= 150
                        gang_members.append(f"Gang Member {len(gang_members) + len([m for country in country_gang_members.values() for m in country]) + 1}")
                        message = "Bought a new gang member!"
                        message_timer = time.time()
                    else:
                        message = "Not enough money to buy a gang member!"
                        message_timer = time.time()
                    buy_gang_second_confirm = False
                elif second_confirm_no.collidepoint(mouse_pos):
                    buy_gang_second_confirm = False
            elif sell_gang_confirm:
                if sell_confirm_yes.collidepoint(mouse_pos):
                    if member_to_sell is not None:
                        money += 90
                        sold_member = gang_members.pop(member_to_sell)
                        message = f"Sold {sold_member} for $90!"
                        message_timer = time.time()
                    sell_gang_confirm = False
                    member_to_sell = None
                elif sell_confirm_no.collidepoint(mouse_pos):
                    sell_gang_confirm = False
                    member_to_sell = None
            elif cancel_business_confirm:
                if cancel_business_yes.collidepoint(mouse_pos):
                    if money >= 700 and active_businesses:
                        money -= 700
                        business = active_businesses.pop(cancel_business_index)
                        country = business["country"]
                        country_business[country] = None
                        countries[country]["business_income"] = 0
                        message = f"Cancelled {business['type']} in {country} for $700!"
                        message_timer = time.time()
                    else:
                        message = "Not enough money or no business to cancel!"
                        message_timer = time.time()
                    cancel_business_confirm = False
                    cancel_business_index = None
                elif cancel_business_no.collidepoint(mouse_pos):
                    cancel_business_confirm = False
                    cancel_business_index = None
            elif borrow_confirm_active:
                if borrow_confirm_yes.collidepoint(mouse_pos):
                    money += borrow_amount
                    bank_debt += borrow_amount
                    message = f"Borrowed ${borrow_amount} from the bank!"
                    message_timer = time.time()
                    borrow_confirm_active = False
                    borrow_amount = 0
                elif borrow_confirm_no.collidepoint(mouse_pos):
                    borrow_confirm_active = False
                    borrow_amount = 0
            elif choose_business_dialog:
                if gun_button.collidepoint(mouse_pos):
                    if money >= 500:
                        money -= 500
                        business_to_assign = "Gun Production"
                        assign_business_dialog = True
                        message = "Selected Gun Production! $500 deducted."
                        message_timer = time.time()
                    else:
                        message = "Need at least $500 to start a business!"
                        message_timer = time.time()
                    choose_business_dialog = False
                elif local_button.collidepoint(mouse_pos):
                    if money >= 500:
                        money -= 500
                        business_to_assign = "Local Business Takeover"
                        assign_business_dialog = True
                        message = "Selected Local Business Takeover! $500 deducted."
                        message_timer = time.time()
                    else:
                        message = "Need at least $500 to start a business!"
                        message_timer = time.time()
                    choose_business_dialog = False
                elif drug_button.collidepoint(mouse_pos):
                    if money >= 500:
                        money -= 500
                        business_to_assign = "Drug Production"
                        assign_business_dialog = True
                        message = "Selected Drug Production! $500 deducted."
                        message_timer = time.time()
                    else:
                        message = "Need at least $500 to start a business!"
                        message_timer = time.time()
                    choose_business_dialog = False
                elif tax_button.collidepoint(mouse_pos):
                    if money >= 500:
                        money -= 500
                        business_to_assign = "Tax Frauds"
                        assign_business_dialog = True
                        message = "Selected Tax Frauds! $500 deducted."
                        message_timer = time.time()
                    else:
                        message = "Need at least $500 to start a business!"
                        message_timer = time.time()
                    choose_business_dialog = False
            elif change_location_dialog:
                dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
                owned_countries = [country for country, data in countries.items() if data["owned"]]
                for i, country in enumerate(owned_countries):
                    country_button = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 - 60 + i * 30, 360, 25)
                    if country_button.collidepoint(mouse_pos):
                        first_bought_country = country
                        message = f"HQ location changed to {country}!"
                        message_timer = time.time()
                        change_location_dialog = False
                        break
                if not dialog_rect.collidepoint(mouse_pos):
                    change_location_dialog = False
            elif assign_business_dialog:
                dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
                owned_countries = [country for country, data in countries.items() if data["owned"] and country_business[country] is None]
                for i, country in enumerate(owned_countries):
                    country_button = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 - 60 + i * 30, 360, 25)
                    if country_button.collidepoint(mouse_pos):
                        if business_to_assign:
                            country_business[country] = business_to_assign
                            num_members = len(country_gang_members[country])
                            base_income = BUSINESS_INCOME_RATES[business_to_assign]
                            countries[country]["business_income"] = int(base_income * (1 + num_members * 0.1))
                            active_businesses.append({"type": business_to_assign, "country": country})
                            message = f"Assigned {business_to_assign} to {country}!"
                            message_timer = time.time()
                        assign_business_dialog = False
                        business_to_assign = None
                        break
                if not dialog_rect.collidepoint(mouse_pos):
                    assign_business_dialog = False
                    business_to_assign = None
            elif assign_member_dialog:
                dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
                owned_countries = [country for country, data in countries.items() if data["owned"]]
                for i, country in enumerate(owned_countries):
                    country_button = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 - 60 + i * 30, 360, 25)
                    if country_button.collidepoint(mouse_pos):
                        if member_to_assign is not None:
                            member = gang_members.pop(member_to_assign)
                            country_gang_members[country].append(member)
                            if country_business[country]:
                                base_income = BUSINESS_INCOME_RATES[country_business[country]]
                                num_members = len(country_gang_members[country])
                                countries[country]["business_income"] = int(base_income * (1 + num_members * 0.1))
                            message = f"Assigned {member} to {country}!"
                            message_timer = time.time()
                        assign_member_dialog = False
                        member_to_assign = None
                        break
                if not dialog_rect.collidepoint(mouse_pos):
                    assign_member_dialog = False
                    member_to_assign = None
            elif borrow_money_dialog:
                dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
                if borrow_100.collidepoint(mouse_pos):
                    borrow_amount = 100
                    borrow_confirm_active = True
                elif borrow_500.collidepoint(mouse_pos):
                    borrow_amount = 500
                    borrow_confirm_active = True
                elif borrow_1000.collidepoint(mouse_pos):
                    borrow_amount = 1000
                    borrow_confirm_active = True
                elif borrow_5000.collidepoint(mouse_pos):
                    borrow_amount = 5000
                    borrow_confirm_active = True
                elif borrow_10000.collidepoint(mouse_pos):
                    borrow_amount = 10000
                    borrow_confirm_active = True
                elif borrow_cancel.collidepoint(mouse_pos):
                    borrow_money_dialog = False
                elif pay_debt_button.collidepoint(mouse_pos):
                    if bank_debt > 0:
                        if money >= bank_debt + bank_interest:
                            money -= bank_debt + bank_interest
                            message = f"Paid off ${bank_debt} debt and ${bank_interest} interest!"
                            message_timer = time.time()
                            bank_debt = 0
                            bank_interest = 0
                        else:
                            message = "Not enough money to pay debt and interest!"
                            message_timer = time.time()
                    borrow_money_dialog = False
                elif not dialog_rect.collidepoint(mouse_pos):
                    borrow_money_dialog = False
            elif profile_dialog:
                if profile_close_button.collidepoint(mouse_pos):
                    profile_dialog = False
                    profile_member = None
                    profile_member_index = None
                    profile_member_country = None
                elif unassign_button.collidepoint(mouse_pos) and profile_member_country:
                    member = country_gang_members[profile_member_country].pop(profile_member_index)
                    gang_members.append(member)
                    num_members = len(country_gang_members[profile_member_country])
                    if country_business[profile_member_country]:
                        base_income = BUSINESS_INCOME_RATES[country_business[profile_member_country]]
                        countries[profile_member_country]["business_income"] = int(base_income * (1 + num_members * 0.1))
                    message = f"Unassigned {member} from {profile_member_country}!"
                    message_timer = time.time()
                    profile_dialog = False
                    profile_member = None
                    profile_member_index = None
                    profile_member_country = None
                elif sell_profile_button.collidepoint(mouse_pos) and not profile_member_country:
                    member_to_sell = profile_member_index
                    sell_gang_confirm = True
            elif relocate_business_dialog:
                dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
                owned_countries = [country for country, data in countries.items() if data["owned"] and country_business[country] is None]
                for i, country in enumerate(owned_countries):
                    country_button = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 - 60 + i * 30, 360, 25)
                    if country_button.collidepoint(mouse_pos):
                        if business_to_relocate is not None:
                            business = active_businesses[business_to_relocate]
                            old_country = business["country"]
                            country_business[old_country] = None
                            countries[old_country]["business_income"] = 0
                            business["country"] = country
                            country_business[country] = business["type"]
                            num_members = len(country_gang_members[country])
                            base_income = BUSINESS_INCOME_RATES[business["type"]]
                            countries[country]["business_income"] = int(base_income * (1 + num_members * 0.1))
                            message = f"Relocated {business['type']} to {country}!"
                            message_timer = time.time()
                        relocate_business_dialog = False
                        business_to_relocate = None
                        break
                if not dialog_rect.collidepoint(mouse_pos):
                    relocate_business_dialog = False
                    business_to_relocate = None
            elif gang_panel_active:
                panel_x, panel_y = gang_panel_pos
                gang_panel_rect = pygame.Rect(panel_x + 50, panel_y, 250, 300)
                members_tab_button = pygame.Rect(panel_x, panel_y, 50, 30)
                business_tab_button = pygame.Rect(panel_x, panel_y + 30, 50, 30)
                location_tab_button = pygame.Rect(panel_x, panel_y + 60, 50, 30)
                vehicle_tab_button = pygame.Rect(panel_x, panel_y + 90, 50, 30)
                diplomacy_tab_button = pygame.Rect(panel_x, panel_y + 120, 50, 30)
                gang_close_button = pygame.Rect(panel_x + 220, panel_y + 270, 80, 25)
                buy_gang_member_button = pygame.Rect(panel_x + 60, panel_y + 30, 230, 25)
                choose_business_button = pygame.Rect(panel_x + 60, panel_y + 30, 230, 25)
                if gang_close_button.collidepoint(mouse_pos):
                    gang_panel_active = False
                    current_gang_tab = "Members"
                elif members_tab_button.collidepoint(mouse_pos):
                    current_gang_tab = "Members"
                elif business_tab_button.collidepoint(mouse_pos):
                    current_gang_tab = "Business"
                elif location_tab_button.collidepoint(mouse_pos):
                    current_gang_tab = "Location"
                elif vehicle_tab_button.collidepoint(mouse_pos):
                    current_gang_tab = "Vehicle"
                elif diplomacy_tab_button.collidepoint(mouse_pos):
                    current_gang_tab = "Gang Diplomacy"
                elif current_gang_tab == "Members":
                    if buy_gang_member_button.collidepoint(mouse_pos):
                        buy_gang_first_confirm = True
                    all_members = []
                    for i, member in enumerate(gang_members):
                        all_members.append((member, None, i))
                    for country in countries:
                        for i, member in enumerate(country_gang_members[country]):
                            all_members.append((member, country, i))
                    for i, (member, country, index) in enumerate(all_members):
                        member_rect = pygame.Rect(panel_x + 60, panel_y + 70 + i * 20, 150, 20)
                        profile_button = pygame.Rect(panel_x + 270, panel_y + 70 + i * 20, 20, 20)
                        assign_button = pygame.Rect(panel_x + 170, panel_y + 70 + i * 20, 90, 20)
                        minus_button = pygame.Rect(panel_x + 295, panel_y + 70 + i * 20, 20, 20)
                        if member_rect.collidepoint(mouse_pos):
                            profile_dialog = True
                            profile_member = member
                            profile_member_index = index
                            profile_member_country = country
                            break
                        elif profile_button.collidepoint(mouse_pos):
                            profile_dialog = True
                            profile_member = member
                            profile_member_index = index
                            profile_member_country = country
                            break
                        elif assign_button.collidepoint(mouse_pos) and not country:
                            assign_member_dialog = True
                            member_to_assign = index
                            break
                        elif minus_button.collidepoint(mouse_pos) and not country:
                            sell_gang_confirm = True
                            member_to_sell = index
                            break
                elif current_gang_tab == "Business":
                    if choose_business_button.collidepoint(mouse_pos):
                        owned_countries = [country for country, data in countries.items() if data["owned"]]
                        if owned_countries:
                            choose_business_dialog = True
                        else:
                            message = "You must own a country to start a business!"
                            message_timer = time.time()
                    for i, business in enumerate(active_businesses):
                        relocate_button = pygame.Rect(panel_x + 170, panel_y + 90 + i * 20, 90, 20)
                        cancel_button = pygame.Rect(panel_x + 270, panel_y + 90 + i * 20, 20, 20)
                        if relocate_button.collidepoint(mouse_pos):
                            relocate_business_dialog = True
                            business_to_relocate = i
                            break
                        elif cancel_button.collidepoint(mouse_pos):
                            cancel_business_confirm = True
                            cancel_business_index = i
                            break
                elif current_gang_tab == "Location":
                    change_location_button = pygame.Rect(panel_x + 60, panel_y + 60, 230, 25)
                    if change_location_button.collidepoint(mouse_pos):
                        change_location_dialog = True
                elif not (gang_panel_rect.collidepoint(mouse_pos) or members_tab_button.collidepoint(mouse_pos) or
                          business_tab_button.collidepoint(mouse_pos) or location_tab_button.collidepoint(mouse_pos) or
                          vehicle_tab_button.collidepoint(mouse_pos) or diplomacy_tab_button.collidepoint(mouse_pos)):
                    gang_panel_active = False
                    current_gang_tab = "Members"
            elif panel_active:
                panel_rect = pygame.Rect(500, 150, 250, 230)
                if panel_close_button.collidepoint(mouse_pos):
                    panel_active = False
                    panel_country = None
                    selected_country = None
                elif panel_buy_button.collidepoint(mouse_pos) and panel_country and not countries[panel_country]["owned"]:
                    confirmation_active = True
                    confirmation_country = panel_country
                elif not panel_rect.collidepoint(mouse_pos):
                    panel_active = False
                    panel_country = None
                    selected_country = None
            else:
                if gang_button.collidepoint(mouse_pos):
                    gang_panel_active = True
                    panel_active = False
                    panel_country = None
                    selected_country = None
                    current_gang_tab = "Members"
                elif bank_button.collidepoint(mouse_pos):
                    borrow_money_dialog = True
                    panel_active = False
                    gang_panel_active = False
                else:
                    selected_country = None
                    panel_active = False
                    panel_country = None
                    for country, data in countries.items():
                        if point_in_polygon(mouse_pos, data["polygon"]):
                            selected_country = country
                            panel_active = True
                            panel_country = country
                            gang_panel_active = False
                            break

    # Update time, interest, and income (paused state respected)
    if paused:
        current_time = time.time()
        date_str = current_date.strftime("%d.%m.%Y")
    else:
        current_time = time.time()
        # Apply business income
        if current_time - last_business_income_time >= 1:
            for country, data in countries.items():
                if data["owned"] and country_business[country]:
                    income = data["business_income"]
                    money += income
            last_business_income_time = current_time
        # Apply interest on debt
        if bank_debt > 0 and current_time - last_interest_time >= 1:
            for amount, rate in BORROW_INTEREST_RATES.items():
                if amount <= bank_debt:
                    interest = bank_debt * rate
                    bank_interest += interest
            last_interest_time = current_time
        date_str = update_date(current_time)

    # Render
    mouse_pos = pygame.mouse.get_pos()
    screen.fill(WHITE)
    screen.blit(map_image, (0, 0))

    # Draw country polygons
    for country, data in countries.items():
        polygon = data["polygon"]
        color = GREEN if data["owned"] else RED
        pygame.draw.polygon(screen, color, polygon, 0)
        pygame.draw.polygon(screen, BLACK, polygon, 3)
        if country == selected_country:
            pygame.draw.polygon(screen, YELLOW, polygon, 5)
        if not data["owned"]:
            price_label = "Free" if first_purchase else f"${data['cost']}"
            price_text = font.render(price_label, True, BLACK)
            centroid = get_polygon_centroid(polygon)
            text_rect = price_text.get_rect(center=centroid)
            screen.blit(price_text, text_rect)

    # Draw upper main panel
    stats_rect = pygame.Rect(50, 10, 700, 50)
    pygame.draw.rect(screen, WHITE, stats_rect)
    pygame.draw.rect(screen, BLACK, stats_rect, 1)
    col_width = 140
    col1_x = 50
    col2_x = col1_x + col_width
    col3_x = col2_x + col_width
    col4_x = col3_x + col_width
    col5_x = col4_x + col_width
    text_y = 25
    money_text = font.render(f"${money}", True, BLACK)
    money_rect = money_text.get_rect(center=(col1_x + col_width // 2, text_y))
    screen.blit(money_text, money_rect)
    debt_text = font.render(f"${bank_debt}", True, BLACK)
    debt_rect = debt_text.get_rect(center=(col2_x + col_width // 2, text_y))
    screen.blit(debt_text, debt_rect)
    rep_text = font.render(f"{reputation}", True, BLACK)
    rep_rect = rep_text.get_rect(center=(col3_x + col_width // 2, text_y))
    screen.blit(rep_text, rep_rect)
    owned_text = font.render(f"{sum(1 for data in countries.values() if data['owned'])}/{len(countries)}", True, BLACK)
    owned_rect = owned_text.get_rect(center=(col4_x + col_width // 2, text_y))
    screen.blit(owned_text, owned_rect)
    date_text = font.render(date_str, True, BLACK)
    date_rect = date_text.get_rect(center=(col5_x + col_width // 2, text_y))
    screen.blit(date_text, date_rect)
    pygame.draw.line(screen, BLACK, (col1_x + col_width, 10), (col1_x + col_width, 60), 1)
    pygame.draw.line(screen, BLACK, (col2_x + col_width, 10), (col2_x + col_width, 60), 1)
    pygame.draw.line(screen, BLACK, (col3_x + col_width, 10), (col3_x + col_width, 60), 1)
    pygame.draw.line(screen, BLACK, (col4_x + col_width, 10), (col4_x + col_width, 60), 1)
    # Tooltips
    tooltip_text = None
    tooltip_x = 0
    if col1_rect.collidepoint(mouse_pos):
        income_sources = [f"{b['type']} in {b['country']}: ${countries[b['country']]['business_income']}/s" for b in active_businesses]
        tooltip_text = f"Money: ${money}"
        tooltip_text += "\nIncome from:\n" + ("\n".join(income_sources) if income_sources else "None")
        tooltip_x = col1_x + col_width // 2
    elif col2_rect.collidepoint(mouse_pos):
        tooltip_text = f"Bank Debt: ${bank_debt}\nInterest Owed: ${int(bank_interest)}"
        tooltip_x = col2_x + col_width // 2
    elif col3_rect.collidepoint(mouse_pos):
        tooltip_text = f"Reputation: {reputation}"
        tooltip_x = col3_x + col_width // 2
    elif col4_rect.collidepoint(mouse_pos):
        tooltip_text = f"Countries Owned: {sum(1 for data in countries.values() if data['owned'])}/{len(countries)}"
        tooltip_x = col4_x + col_width // 2
    elif col5_rect.collidepoint(mouse_pos):
        tooltip_text = f"Date: {date_str}"
        tooltip_x = col5_x + col_width // 2
    if tooltip_text:
        lines = tooltip_text.split('\n')
        max_width = max(dialog_font.size(line)[0] for line in lines)
        total_height = len(lines) * dialog_font.get_height()
        tooltip_rect = pygame.Rect(tooltip_x - max_width // 2, 75, max_width, total_height)
        tooltip_bg_rect = tooltip_rect.inflate(10, 10)
        pygame.draw.rect(screen, WHITE, tooltip_bg_rect)
        pygame.draw.rect(screen, BLACK, tooltip_bg_rect, 1)
        for i, line in enumerate(lines):
            tooltip_surface = dialog_font.render(line, True, BLACK)
            screen.blit(tooltip_surface, (tooltip_x - dialog_font.size(line)[0] // 2, 75 + i * dialog_font.get_height()))

    # Draw gang button
    button_color = DARK_GRAY if gang_button.collidepoint(mouse_pos) else GRAY
    pygame.draw.rect(screen, button_color, gang_button)
    pygame.draw.rect(screen, BLACK, gang_button, 1)
    gang_text = font.render("Gang", True, BLACK)
    gang_rect = gang_text.get_rect(center=gang_button.center)
    screen.blit(gang_text, gang_rect)
    if gang_button.collidepoint(mouse_pos):
        tooltip_text = f"Unassigned Gang Members: {len(gang_members)}"
        tooltip_surface = dialog_font.render(tooltip_text, True, BLACK)
        tooltip_rect = tooltip_surface.get_rect(center=(gang_button.centerx, gang_button.bottom + 20))
        tooltip_bg_rect = tooltip_rect.inflate(10, 10)
        pygame.draw.rect(screen, WHITE, tooltip_bg_rect)
        pygame.draw.rect(screen, BLACK, tooltip_bg_rect, 1)
        screen.blit(tooltip_surface, tooltip_rect)

    # Draw bank button
    button_color = DARK_GRAY if bank_button.collidepoint(mouse_pos) else GRAY
    pygame.draw.rect(screen, button_color, bank_button)
    pygame.draw.rect(screen, BLACK, bank_button, 1)
    bank_text = font.render("Bank", True, BLACK)
    bank_rect = bank_text.get_rect(center=bank_button.center)
    screen.blit(bank_text, bank_rect)
    if bank_button.collidepoint(mouse_pos):
        tooltip_text = f"Bank Debt: ${bank_debt}\nInterest Owed: ${int(bank_interest)}"
        tooltip_surface = dialog_font.render(tooltip_text, True, BLACK)
        tooltip_rect = tooltip_surface.get_rect(center=(bank_button.centerx, bank_button.bottom + 20))
        tooltip_bg_rect = tooltip_rect.inflate(10, 10)
        pygame.draw.rect(screen, WHITE, tooltip_bg_rect)
        pygame.draw.rect(screen, BLACK, tooltip_bg_rect, 1)
        screen.blit(tooltip_surface, tooltip_rect)

    # Draw pause button
    button_color = DARK_GRAY if pause_button.collidepoint(mouse_pos) else GRAY
    pygame.draw.rect(screen, button_color, pause_button)
    pygame.draw.rect(screen, BLACK, pause_button, 1)
    pause_text = font.render("Pause" if not paused else "Resume", True, BLACK)
    text_rect = pause_text.get_rect(center=(pause_button.centerx + 10, pause_button.centery))
    screen.blit(pause_text, text_rect)
    if not paused:
        pygame.draw.rect(screen, BLACK, (pause_button.x + 10, pause_button.y + 10, 5, 20))
        pygame.draw.rect(screen, BLACK, (pause_button.x + 20, pause_button.y + 10, 5, 20))
    else:
        pygame.draw.polygon(screen, BLACK, [
            (pause_button.x + 10, pause_button.y + 10),
            (pause_button.x + 25, pause_button.y + 20),
            (pause_button.x + 10, pause_button.y + 30)
        ])

    # Draw country panel
    if panel_active and panel_country:
        panel_rect = pygame.Rect(500, 150, 250, 230)
        pygame.draw.rect(screen, WHITE, panel_rect)
        pygame.draw.rect(screen, BLACK, panel_rect, 2)
        data = countries[panel_country]
        name_text = title_font.render(panel_country, True, BLACK)
        pop_text = font.render(f"Pop: {data['population']:,}", True, BLACK)
        gang_text = font.render(f"Gang: {len(country_gang_members[panel_country])}", True, BLACK)
        income_text = font.render(f"Income: ${data['business_income']}/s", True, BLACK)
        business_text = font.render(f"Business: {country_business[panel_country] or 'None'}", True, BLACK)
        screen.blit(name_text, (510, 160))
        screen.blit(pop_text, (510, 190))
        screen.blit(gang_text, (510, 210))
        screen.blit(income_text, (510, 230))
        screen.blit(business_text, (510, 250))
        pygame.draw.rect(screen, GRAY, panel_close_button)
        pygame.draw.rect(screen, BLACK, panel_close_button, 2)
        close_text = font.render("Close", True, BLACK)
        close_rect = close_text.get_rect(center=panel_close_button.center)
        screen.blit(close_text, close_rect)
        if not data["owned"]:
            pygame.draw.rect(screen, GRAY, panel_buy_button)
            pygame.draw.rect(screen, BLACK, panel_buy_button, 2)
            buy_text = font.render("Buy", True, BLACK)
            buy_rect = buy_text.get_rect(center=panel_buy_button.center)
            screen.blit(buy_text, buy_rect)

    # Draw gang panel
    if gang_panel_active:
        panel_x, panel_y = gang_panel_pos
        members_tab_button = pygame.Rect(panel_x, panel_y, 50, 30)
        business_tab_button = pygame.Rect(panel_x, panel_y + 30, 50, 30)
        location_tab_button = pygame.Rect(panel_x, panel_y + 60, 50, 30)
        vehicle_tab_button = pygame.Rect(panel_x, panel_y + 90, 50, 30)
        diplomacy_tab_button = pygame.Rect(panel_x, panel_y + 120, 50, 30)
        gang_panel_rect = pygame.Rect(panel_x + 50, panel_y, 250, 300)
        pygame.draw.rect(screen, WHITE, gang_panel_rect)
        pygame.draw.rect(screen, BLACK, gang_panel_rect, 2)
        pygame.draw.rect(screen, GRAY if current_gang_tab == "Members" else WHITE, members_tab_button)
        pygame.draw.rect(screen, BLACK, members_tab_button, 1)
        members_text = font.render("M", True, BLACK)
        screen.blit(members_text, members_text.get_rect(center=members_tab_button.center))
        pygame.draw.rect(screen, GRAY if current_gang_tab == "Business" else WHITE, business_tab_button)
        pygame.draw.rect(screen, BLACK, business_tab_button, 1)
        business_text = font.render("B", True, BLACK)
        screen.blit(business_text, business_text.get_rect(center=business_tab_button.center))
        pygame.draw.rect(screen, GRAY if current_gang_tab == "Location" else WHITE, location_tab_button)
        pygame.draw.rect(screen, BLACK, location_tab_button, 1)
        location_text = font.render("L", True, BLACK)
        screen.blit(location_text, location_text.get_rect(center=location_tab_button.center))
        pygame.draw.rect(screen, GRAY if current_gang_tab == "Vehicle" else WHITE, vehicle_tab_button)
        pygame.draw.rect(screen, BLACK, vehicle_tab_button, 1)
        vehicle_text = font.render("V", True, BLACK)
        screen.blit(vehicle_text, vehicle_text.get_rect(center=vehicle_tab_button.center))
        pygame.draw.rect(screen, GRAY if current_gang_tab == "Gang Diplomacy" else WHITE, diplomacy_tab_button)
        pygame.draw.rect(screen, BLACK, diplomacy_tab_button, 1)
        diplomacy_text = font.render("D", True, BLACK)
        screen.blit(diplomacy_text, diplomacy_text.get_rect(center=diplomacy_tab_button.center))
        # Tooltips for tabs
        if members_tab_button.collidepoint(mouse_pos):
            tooltip_text = "Members"
            tooltip_surface = dialog_font.render(tooltip_text, True, BLACK)
            tooltip_x = max(0, panel_x - 100)
            tooltip_rect = tooltip_surface.get_rect(topleft=(tooltip_x, panel_y + 5))
            tooltip_bg_rect = tooltip_rect.inflate(10, 10)
            pygame.draw.rect(screen, WHITE, tooltip_bg_rect)
            pygame.draw.rect(screen, BLACK, tooltip_bg_rect, 1)
            screen.blit(tooltip_surface, tooltip_rect)
        elif business_tab_button.collidepoint(mouse_pos):
            tooltip_text = "Business"
            tooltip_surface = dialog_font.render(tooltip_text, True, BLACK)
            tooltip_x = max(0, panel_x - 100)
            tooltip_rect = tooltip_surface.get_rect(topleft=(tooltip_x, panel_y + 35))
            tooltip_bg_rect = tooltip_rect.inflate(10, 10)
            pygame.draw.rect(screen, WHITE, tooltip_bg_rect)
            pygame.draw.rect(screen, BLACK, tooltip_bg_rect, 1)
            screen.blit(tooltip_surface, tooltip_rect)
        elif location_tab_button.collidepoint(mouse_pos):
            tooltip_text = "Location"
            tooltip_surface = dialog_font.render(tooltip_text, True, BLACK)
            tooltip_x = max(0, panel_x - 100)
            tooltip_rect = tooltip_surface.get_rect(topleft=(tooltip_x, panel_y + 65))
            tooltip_bg_rect = tooltip_rect.inflate(10, 10)
            pygame.draw.rect(screen, WHITE, tooltip_bg_rect)
            pygame.draw.rect(screen, BLACK, tooltip_bg_rect, 1)
            screen.blit(tooltip_surface, tooltip_rect)
        elif vehicle_tab_button.collidepoint(mouse_pos):
            tooltip_text = "Vehicle"
            tooltip_surface = dialog_font.render(tooltip_text, True, BLACK)
            tooltip_x = max(0, panel_x - 100)
            tooltip_rect = tooltip_surface.get_rect(topleft=(tooltip_x, panel_y + 95))
            tooltip_bg_rect = tooltip_rect.inflate(10, 10)
            pygame.draw.rect(screen, WHITE, tooltip_bg_rect)
            pygame.draw.rect(screen, BLACK, tooltip_bg_rect, 1)
            screen.blit(tooltip_surface, tooltip_rect)
        elif diplomacy_tab_button.collidepoint(mouse_pos):
            tooltip_text = "Gang Diplomacy"
            tooltip_surface = dialog_font.render(tooltip_text, True, BLACK)
            tooltip_x = max(0, panel_x - 150)
            tooltip_rect = tooltip_surface.get_rect(topleft=(tooltip_x, panel_y + 125))
            tooltip_bg_rect = tooltip_rect.inflate(10, 10)
            pygame.draw.rect(screen, WHITE, tooltip_bg_rect)
            pygame.draw.rect(screen, BLACK, tooltip_bg_rect, 1)
            screen.blit(tooltip_surface, tooltip_rect)
        # Members tab
        if current_gang_tab == "Members":
            buy_gang_member_button = pygame.Rect(panel_x + 60, panel_y + 30, 230, 25)
            pygame.draw.rect(screen, GRAY if money >= 150 else DARK_GRAY, buy_gang_member_button)
            pygame.draw.rect(screen, BLACK, buy_gang_member_button, 1)
            buy_text = font.render("Buy Gang Member ($150)", True, BLACK)
            buy_rect = buy_text.get_rect(center=buy_gang_member_button.center)
            screen.blit(buy_text, buy_rect)
            all_members = []
            for i, member in enumerate(gang_members):
                all_members.append((member, None, i))
            for country in countries:
                for i, member in enumerate(country_gang_members[country]):
                    all_members.append((member, country, i))
            for i, (member, country, index) in enumerate(all_members):
                member_text = font.render(f"{member} ({country or 'Unassigned'})", True, BLACK)
                screen.blit(member_text, (panel_x + 60, panel_y + 70 + i * 20))
                profile_button = pygame.Rect(panel_x + 270, panel_y + 70 + i * 20, 20, 20)
                assign_button = pygame.Rect(panel_x + 170, panel_y + 70 + i * 20, 90, 20)
                minus_button = pygame.Rect(panel_x + 295, panel_y + 70 + i * 20, 20, 20)
                pygame.draw.rect(screen, GRAY, profile_button)
                pygame.draw.rect(screen, BLACK, profile_button, 1)
                profile_text = font.render("P", True, BLACK)
                profile_rect = profile_text.get_rect(center=profile_button.center)
                screen.blit(profile_text, profile_rect)
                if not country:
                    pygame.draw.rect(screen, GRAY, assign_button)
                    pygame.draw.rect(screen, BLACK, assign_button, 1)
                    assign_text = font.render("Assign", True, BLACK)
                    assign_rect = assign_text.get_rect(center=assign_button.center)
                    screen.blit(assign_text, assign_rect)
                    pygame.draw.rect(screen, RED, minus_button)
                    pygame.draw.rect(screen, BLACK, minus_button, 1)
                    minus_text = font.render("-", True, BLACK)
                    minus_rect = minus_text.get_rect(center=minus_button.center)
                    screen.blit(minus_text, minus_rect)
        # Business tab
        elif current_gang_tab == "Business":
            choose_business_button = pygame.Rect(panel_x + 60, panel_y + 30, 230, 25)
            pygame.draw.rect(screen, GRAY, choose_business_button)
            pygame.draw.rect(screen, BLACK, choose_business_button, 1)
            choose_text = font.render("Start New Business", True, BLACK)
            choose_rect = choose_text.get_rect(center=choose_business_button.center)
            screen.blit(choose_text, choose_rect)
            if active_businesses:
                business_list_text = font.render("Active Businesses:", True, BLACK)
                screen.blit(business_list_text, (panel_x + 60, panel_y + 60))
                for i, business in enumerate(active_businesses):
                    business_text = font.render(f"{business['type']} in {business['country']}", True, BLACK)
                    screen.blit(business_text, (panel_x + 60, panel_y + 90 + i * 20))
                    relocate_button = pygame.Rect(panel_x + 170, panel_y + 90 + i * 20, 90, 20)
                    cancel_button = pygame.Rect(panel_x + 270, panel_y + 90 + i * 20, 20, 20)
                    pygame.draw.rect(screen, GRAY, relocate_button)
                    pygame.draw.rect(screen, BLACK, relocate_button, 1)
                    relocate_text = font.render("Relocate", True, BLACK)
                    relocate_rect = relocate_text.get_rect(center=relocate_button.center)
                    screen.blit(relocate_text, relocate_rect)
                    pygame.draw.rect(screen, RED, cancel_button)
                    pygame.draw.rect(screen, BLACK, cancel_button, 1)
                    cancel_text = font.render("X", True, BLACK)
                    cancel_rect = cancel_text.get_rect(center=cancel_button.center)
                    screen.blit(cancel_text, cancel_rect)
        # Location tab
        elif current_gang_tab == "Location":
            location_text = font.render(f"HQ: {first_bought_country or 'No HQ'}", True, BLACK)
            screen.blit(location_text, (panel_x + 60, panel_y + 30))
            change_location_button = pygame.Rect(panel_x + 60, panel_y + 60, 230, 25)
            pygame.draw.rect(screen, GRAY, change_location_button)
            pygame.draw.rect(screen, BLACK, change_location_button, 1)
            change_text = font.render("Change HQ Location", True, BLACK)
            change_rect = change_text.get_rect(center=change_location_button.center)
            screen.blit(change_text, change_rect)
        # Placeholder tabs
        elif current_gang_tab in ["Vehicle", "Gang Diplomacy"]:
            placeholder_text = font.render(f"{current_gang_tab} - Coming Soon", True, BLACK)
            screen.blit(placeholder_text, (panel_x + 60, panel_y + 30))
        # Close button
        gang_close_button = pygame.Rect(panel_x + 220, panel_y + 270, 80, 25)
        pygame.draw.rect(screen, GRAY, gang_close_button)
        pygame.draw.rect(screen, BLACK, gang_close_button, 2)
        close_text = font.render("Close", True, BLACK)
        close_rect = close_text.get_rect(center=gang_close_button.center)
        screen.blit(close_text, close_rect)
            # Draw confirmation dialog for buying countries
    if confirmation_active:
        dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
        pygame.draw.rect(screen, WHITE, dialog_rect)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2)
        cost = 0 if first_purchase else countries[confirmation_country]["cost"]
        confirm_text = dialog_font.render(f"Buy {confirmation_country} for {'free' if first_purchase else f'${cost}'}?", True, BLACK)
        screen.blit(confirm_text, (WIDTH // 2 - confirm_text.get_width() // 2, HEIGHT // 2 - 20))
        pygame.draw.rect(screen, GRAY, yes_button)
        pygame.draw.rect(screen, BLACK, yes_button, 2)
        yes_text = dialog_font.render("Yes", True, BLACK)
        yes_rect = yes_text.get_rect(center=yes_button.center)
        screen.blit(yes_text, yes_rect)
        pygame.draw.rect(screen, GRAY, no_button)
        pygame.draw.rect(screen, BLACK, no_button, 2)
        no_text = dialog_font.render("No", True, BLACK)
        no_rect = no_text.get_rect(center=no_button.center)
        screen.blit(no_text, no_rect)

    # Draw first confirmation dialog for buying gang members
    if buy_gang_first_confirm:
        dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
        pygame.draw.rect(screen, WHITE, dialog_rect)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2)
        confirm_text = dialog_font.render("Buy gang member for $150?", True, BLACK)
        screen.blit(confirm_text, (WIDTH // 2 - confirm_text.get_width() // 2, HEIGHT // 2 - 20))
        pygame.draw.rect(screen, GRAY, first_confirm_yes)
        pygame.draw.rect(screen, BLACK, first_confirm_yes, 2)
        yes_text = dialog_font.render("Yes", True, BLACK)
        yes_rect = yes_text.get_rect(center=first_confirm_yes.center)
        screen.blit(yes_text, yes_rect)
        pygame.draw.rect(screen, GRAY, first_confirm_no)
        pygame.draw.rect(screen, BLACK, first_confirm_no, 2)
        no_text = dialog_font.render("No", True, BLACK)
        no_rect = no_text.get_rect(center=first_confirm_no.center)
        screen.blit(no_text, no_rect)

    # Draw second confirmation dialog for buying gang members
    if buy_gang_second_confirm:
        dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
        pygame.draw.rect(screen, WHITE, dialog_rect)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2)
        confirm_text = dialog_font.render("Confirm: Buy gang member for $150?", True, BLACK)
        screen.blit(confirm_text, (WIDTH // 2 - confirm_text.get_width() // 2, HEIGHT // 2 - 20))
        pygame.draw.rect(screen, GRAY, second_confirm_yes)
        pygame.draw.rect(screen, BLACK, second_confirm_yes, 2)
        yes_text = dialog_font.render("Yes", True, BLACK)
        yes_rect = yes_text.get_rect(center=second_confirm_yes.center)
        screen.blit(yes_text, yes_rect)
        pygame.draw.rect(screen, GRAY, second_confirm_no)
        pygame.draw.rect(screen, BLACK, second_confirm_no, 2)
        no_text = dialog_font.render("No", True, BLACK)
        no_rect = no_text.get_rect(center=second_confirm_no.center)
        screen.blit(no_text, no_rect)

    # Draw confirmation dialog for selling gang members
    if sell_gang_confirm:
        dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
        pygame.draw.rect(screen, WHITE, dialog_rect)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2)
        confirm_text = dialog_font.render(f"Sell {gang_members[member_to_sell]} for $90?", True, BLACK)
        screen.blit(confirm_text, (WIDTH // 2 - confirm_text.get_width() // 2, HEIGHT // 2 - 20))
        pygame.draw.rect(screen, GRAY, sell_confirm_yes)
        pygame.draw.rect(screen, BLACK, sell_confirm_yes, 2)
        yes_text = dialog_font.render("Yes", True, BLACK)
        yes_rect = yes_text.get_rect(center=sell_confirm_yes.center)
        screen.blit(yes_text, yes_rect)
        pygame.draw.rect(screen, GRAY, sell_confirm_no)
        pygame.draw.rect(screen, BLACK, sell_confirm_no, 2)
        no_text = dialog_font.render("No", True, BLACK)
        no_rect = no_text.get_rect(center=sell_confirm_no.center)
        screen.blit(no_text, no_rect)

    # Draw confirmation dialog for cancelling businesses
    if cancel_business_confirm:
        dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
        pygame.draw.rect(screen, WHITE, dialog_rect)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2)
        business = active_businesses[cancel_business_index]
        confirm_text = dialog_font.render(f"Cancel {business['type']} in {business['country']} for $700?", True, BLACK)
        screen.blit(confirm_text, (WIDTH // 2 - confirm_text.get_width() // 2, HEIGHT // 2 - 20))
        pygame.draw.rect(screen, GRAY, cancel_business_yes)
        pygame.draw.rect(screen, BLACK, cancel_business_yes, 2)
        yes_text = dialog_font.render("Yes", True, BLACK)
        yes_rect = yes_text.get_rect(center=cancel_business_yes.center)
        screen.blit(yes_text, yes_rect)
        pygame.draw.rect(screen, GRAY, cancel_business_no)
        pygame.draw.rect(screen, BLACK, cancel_business_no, 2)
        no_text = dialog_font.render("No", True, BLACK)
        no_rect = no_text.get_rect(center=cancel_business_no.center)
        screen.blit(no_text, no_rect)

    # Draw business selection dialog
    if choose_business_dialog:
        dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
        pygame.draw.rect(screen, WHITE, dialog_rect)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2)
        title_text = dialog_font.render("Choose Business ($500)", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 60))
        pygame.draw.rect(screen, GRAY if money >= 500 else DARK_GRAY, gun_button)
        pygame.draw.rect(screen, BLACK, gun_button, 1)
        gun_text = dialog_font.render("Gun Production", True, BLACK)
        screen.blit(gun_text, (gun_button.x + 5, gun_button.y + 5))
        pygame.draw.rect(screen, GRAY if money >= 500 else DARK_GRAY, local_button)
        pygame.draw.rect(screen, BLACK, local_button, 1)
        local_text = dialog_font.render("Local Business", True, BLACK)
        screen.blit(local_text, (local_button.x + 5, local_button.y + 5))
        pygame.draw.rect(screen, GRAY if money >= 500 else DARK_GRAY, drug_button)
        pygame.draw.rect(screen, BLACK, drug_button, 1)
        drug_text = dialog_font.render("Drug Production", True, BLACK)
        screen.blit(drug_text, (drug_button.x + 5, drug_button.y + 5))
        pygame.draw.rect(screen, GRAY if money >= 500 else DARK_GRAY, tax_button)
        pygame.draw.rect(screen, BLACK, tax_button, 1)
        tax_text = dialog_font.render("Tax Frauds", True, BLACK)
        screen.blit(tax_text, (tax_button.x + 5, tax_button.y + 5))

    # Draw assign business dialog
    if assign_business_dialog:
        dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
        pygame.draw.rect(screen, WHITE, dialog_rect)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2)
        title_text = dialog_font.render(f"Assign {business_to_assign}", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 80))
        owned_countries = [country for country, data in countries.items() if data["owned"] and country_business[country] is None]
        for i, country in enumerate(owned_countries):
            country_button = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 - 60 + i * 30, 360, 25)
            pygame.draw.rect(screen, GRAY, country_button)
            pygame.draw.rect(screen, BLACK, country_button, 1)
            country_text = dialog_font.render(country, True, BLACK)
            screen.blit(country_text, (country_button.x + 5, country_button.y + 5))

    # Draw borrow money dialog
    if borrow_money_dialog:
        dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
        pygame.draw.rect(screen, WHITE, dialog_rect)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2)
        title_text = dialog_font.render("Borrow or Pay Debt", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 80))
        pygame.draw.rect(screen, GRAY, borrow_100)
        pygame.draw.rect(screen, BLACK, borrow_100, 1)
        text_100 = dialog_font.render("$100", True, BLACK)
        screen.blit(text_100, (borrow_100.x + 5, borrow_100.y + 5))
        pygame.draw.rect(screen, GRAY, borrow_500)
        pygame.draw.rect(screen, BLACK, borrow_500, 1)
        text_500 = dialog_font.render("$500", True, BLACK)
        screen.blit(text_500, (borrow_500.x + 5, borrow_500.y + 5))
        pygame.draw.rect(screen, GRAY, borrow_1000)
        pygame.draw.rect(screen, BLACK, borrow_1000, 1)
        text_1000 = dialog_font.render("$1000", True, BLACK)
        screen.blit(text_1000, (borrow_1000.x + 5, borrow_1000.y + 5))
        pygame.draw.rect(screen, GRAY, borrow_5000)
        pygame.draw.rect(screen, BLACK, borrow_5000, 1)
        text_5000 = dialog_font.render("$5000", True, BLACK)
        screen.blit(text_5000, (borrow_5000.x + 5, borrow_5000.y + 5))
        pygame.draw.rect(screen, GRAY, borrow_10000)
        pygame.draw.rect(screen, BLACK, borrow_10000, 1)
        text_10000 = dialog_font.render("$10000", True, BLACK)
        screen.blit(text_10000, (borrow_10000.x + 5, borrow_10000.y + 5))
        pygame.draw.rect(screen, GRAY, borrow_cancel)
        pygame.draw.rect(screen, BLACK, borrow_cancel, 1)
        cancel_text = dialog_font.render("Cancel", True, BLACK)
        screen.blit(cancel_text, (borrow_cancel.x + 5, borrow_cancel.y + 5))
        pygame.draw.rect(screen, GRAY if money >= bank_debt + bank_interest and bank_debt > 0 else DARK_GRAY, pay_debt_button)
        pygame.draw.rect(screen, BLACK, pay_debt_button, 1)
        pay_text = dialog_font.render("Pay Debt", True, BLACK)
        screen.blit(pay_text, (pay_debt_button.x + 5, pay_debt_button.y + 5))

    # Draw borrow confirmation dialog
    if borrow_confirm_active:
        dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
        pygame.draw.rect(screen, WHITE, dialog_rect)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2)
        rate = BORROW_INTEREST_RATES.get(borrow_amount, 0)
        confirm_text = dialog_font.render(f"Borrow ${borrow_amount}? Interest: {rate*100:.1f}%/s", True, BLACK)
        screen.blit(confirm_text, (WIDTH // 2 - confirm_text.get_width() // 2, HEIGHT // 2 - 20))
        pygame.draw.rect(screen, GRAY, borrow_confirm_yes)
        pygame.draw.rect(screen, BLACK, borrow_confirm_yes, 2)
        yes_text = dialog_font.render("Yes", True, BLACK)
        yes_rect = yes_text.get_rect(center=borrow_confirm_yes.center)
        screen.blit(yes_text, yes_rect)
        pygame.draw.rect(screen, GRAY, borrow_confirm_no)
        pygame.draw.rect(screen, BLACK, borrow_confirm_no, 2)
        no_text = dialog_font.render("No", True, BLACK)
        no_rect = no_text.get_rect(center=borrow_confirm_no.center)
        screen.blit(no_text, no_rect)

    # Draw change location dialog
    if change_location_dialog:
        dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
        pygame.draw.rect(screen, WHITE, dialog_rect)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2)
        title_text = dialog_font.render("Choose New HQ", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 80))
        owned_countries = [country for country, data in countries.items() if data["owned"]]
        for i, country in enumerate(owned_countries):
            country_button = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 - 60 + i * 30, 360, 25)
            pygame.draw.rect(screen, GRAY, country_button)
            pygame.draw.rect(screen, BLACK, country_button, 1)
            country_text = dialog_font.render(country, True, BLACK)
            screen.blit(country_text, (country_button.x + 5, country_button.y + 5))

    # Draw assign gang member dialog
    if assign_member_dialog:
        dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
        pygame.draw.rect(screen, WHITE, dialog_rect)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2)
        title_text = dialog_font.render("Assign Gang Member", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 80))
        owned_countries = [country for country, data in countries.items() if data["owned"]]
        for i, country in enumerate(owned_countries):
            country_button = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 - 60 + i * 30, 360, 25)
            pygame.draw.rect(screen, GRAY, country_button)
            pygame.draw.rect(screen, BLACK, country_button, 1)
            country_text = dialog_font.render(country, True, BLACK)
            screen.blit(country_text, (country_button.x + 5, country_button.y + 5))

    # Draw gang member profile dialog
    if profile_dialog:
        dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
        pygame.draw.rect(screen, WHITE, dialog_rect)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2)
        title_text = dialog_font.render(f"Profile: {profile_member}", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 80))
        location_text = dialog_font.render(f"Location: {profile_member_country or 'Unassigned'}", True, BLACK)
        screen.blit(location_text, (WIDTH // 2 - location_text.get_width() // 2, HEIGHT // 2 - 40))
        pygame.draw.rect(screen, GRAY, profile_close_button)
        pygame.draw.rect(screen, BLACK, profile_close_button, 2)
        close_text = dialog_font.render("Close", True, BLACK)
        close_rect = close_text.get_rect(center=profile_close_button.center)
        screen.blit(close_text, close_rect)
        if profile_member_country:
            pygame.draw.rect(screen, GRAY, unassign_button)
            pygame.draw.rect(screen, BLACK, unassign_button, 2)
            unassign_text = dialog_font.render("Unassign", True, BLACK)
            unassign_rect = unassign_text.get_rect(center=unassign_button.center)
            screen.blit(unassign_text, unassign_rect)
        else:
            pygame.draw.rect(screen, GRAY, sell_profile_button)
            pygame.draw.rect(screen, BLACK, sell_profile_button, 2)
            sell_text = dialog_font.render("Sell", True, BLACK)
            sell_rect = sell_text.get_rect(center=sell_profile_button.center)
            screen.blit(sell_text, sell_rect)

    # Draw business relocation dialog
    if relocate_business_dialog:
        dialog_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
        pygame.draw.rect(screen, WHITE, dialog_rect)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2)
        business = active_businesses[business_to_relocate]
        title_text = dialog_font.render(f"Relocate {business['type']}", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 80))
        owned_countries = [country for country, data in countries.items() if data["owned"] and country_business[country] is None]
        for i, country in enumerate(owned_countries):
            country_button = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 - 60 + i * 30, 360, 25)
            pygame.draw.rect(screen, GRAY, country_button)
            pygame.draw.rect(screen, BLACK, country_button, 1)
            country_text = dialog_font.render(country, True, BLACK)
            screen.blit(country_text, (country_button.x + 5, country_button.y + 5))

    # Draw message
    if message and current_time - message_timer < MESSAGE_DURATION:
        message_text = dialog_font.render(message, True, BLACK)
        message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        pygame.draw.rect(screen, WHITE, message_rect.inflate(20, 10))
        pygame.draw.rect(screen, BLACK, message_rect.inflate(20, 10), 1)
        screen.blit(message_text, message_rect)

    # Update display
    pygame.display.flip()

    # Cap frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
