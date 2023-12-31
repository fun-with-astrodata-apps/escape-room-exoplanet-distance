import random
import threading

import pygame
from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive


# 初始化pygame
pygame.init()

# 設定視窗的大小及標題
width, height = 1024, 768
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('逃出天文鎖-系外行星與你的距離')

# 設定顏色
WHITE = '#FFFFFF'
GOLD = '#FFD700'
BLACK = '#000000'
DARK_RED = '#8B0000'

# 設定遊戲首頁及密室的背景圖片
background_menu = pygame.image.load('./assets/background_menu.jpg')
background_menu = pygame.transform.scale(background_menu, (width, height))
background_room = pygame.image.load('./assets/background_room.jpg')
background_room = pygame.transform.scale(background_room, (width, height))

# 設定字型
font_path = './assets/NotoSansTC-Black.ttf'
title_font = pygame.font.Font(font_path, 60)
subtitle_font = pygame.font.Font(font_path, 30)
text_font = pygame.font.Font(font_path, 20)

# 設定按鈕參數
button_color = DARK_RED
button_width, button_height = 200, 50
exoplanet_button_rect = pygame.Rect(20, 20, button_width, button_height)
distance_converter_button_rect = pygame.Rect(width - 220, 20, button_width, button_height)
enter_room_button_rect = pygame.Rect(width // 2 - 100, height // 3 + 50, button_width, button_height)

# 呈現遊戲開始畫面的函式
def display_menu_page():
    # 放置背景圖
    screen.blit(background_menu, (0, 0))

    # 放置主標題、副標題和作者資訊
    title = title_font.render('逃出天文鎖-系外行星與你的距離', True, GOLD)
    subtitle = subtitle_font.render('為了逃脫《天文鎖》密室，請你解開系外行星與你的距離', True, GOLD)
    author_info = text_font.render('由astrobackhacker.tw製作', True, GOLD)
    screen.blit(title, (width // 2 - title.get_width() // 2, height // 6 - 15))
    screen.blit(subtitle, (width // 2 - subtitle.get_width() // 2, height // 6 + 60))
    screen.blit(author_info, (width // 2 - author_info.get_width() // 2, height - 35))

    # 放置進入密室的按鈕
    pygame.draw.rect(screen, button_color, enter_room_button_rect)
    enter_button_text = subtitle_font.render('進入密室', True, WHITE)
    screen.blit(enter_button_text, (enter_room_button_rect.x + (enter_room_button_rect.width - enter_button_text.get_width()) // 2, enter_room_button_rect.y + (enter_room_button_rect.height - enter_button_text.get_height()) // 2))


# 呈現正在載入系外行星資料畫面的函式
def display_loading_page():
    screen.fill(BLACK)
    loading_text = subtitle_font.render('正在載入系外行星資料...', True, WHITE)
    screen.blit(loading_text, (width // 2 - loading_text.get_width() // 2, height // 2 - loading_text.get_height() // 2))
    pygame.display.flip()


# 從NASA Exoplanet Archive載入系外行星資料的函式
def load_exoplanet_data():
    global exoplanet_data
    exoplanet_table = NasaExoplanetArchive.query_criteria(
        table='pscomppars', select='pl_name, sy_dist'
    )
    exoplanet_data = exoplanet_table.to_pandas()
    exoplanet_data = exoplanet_data.dropna(subset=['sy_dist'])
    exoplanet_data.sort_values(by='pl_name', inplace=True, ignore_index=True)
    exoplanet_data = exoplanet_data.rename(
        columns={
            'pl_name': '行星名稱',
            'sy_dist': '與地球的距離(秒差距)'
        }
    )


# 呈現密室畫面的函式
def display_room_page(planet_name):
    # 放置背景圖
    screen.blit(background_room, (0, 0))

    # 放置對話框及密室描述
    pygame.draw.rect(screen, BLACK, (0, height - 100, width, 100))
    room_description = f'你身處在一個系外行星主題的密室，左邊牆上掛著NASA提供的系外行星列表，右邊則有一台距離轉換器。要逃出這個密室，你需要解開{planet_name}這個系外行星與你的距離。'
    room_description_sentences = room_description.split('。')
    room_description_sentences = [sentence + '。' for sentence in room_description_sentences if sentence]
    y_text = height - 80
    for sentence in room_description_sentences:
        rendered_text = text_font.render(sentence, True, GOLD)
        screen.blit(rendered_text, (10, y_text))
        y_text += text_font.size(sentence)[1]

    # 放置按鈕
    pygame.draw.rect(screen, button_color, exoplanet_button_rect)
    exoplanet_button_text = text_font.render('查看系外行星列表', True, WHITE)
    screen.blit(exoplanet_button_text, (exoplanet_button_rect.x + 20, exoplanet_button_rect.y + 7))
    pygame.draw.rect(screen, button_color, distance_converter_button_rect)
    distance_converter_button_text = text_font.render('啟動距離轉換器', True, WHITE)
    screen.blit(distance_converter_button_text, (distance_converter_button_rect.x + 20, distance_converter_button_rect.y + 7))


# 初始化遊戲狀態、系外行星資料載入的變數及執行緒
game_state = 'menu'
exoplanet_data = None
loading_thread = None
selected_exoplanet_name = None

# 遊戲主循環
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == 'menu' and enter_room_button_rect.collidepoint(event.pos):
                game_state = 'loading'
                # 建立並啟動新執行緒以載入系外行星資料
                loading_thread = threading.Thread(target=load_exoplanet_data)
                loading_thread.start()
            if game_state == 'room':                    
                if exoplanet_button_rect.collidepoint(event.pos):
                    print('系外行星列表按鈕被點擊')
                    print(exoplanet_data)
                elif distance_converter_button_rect.collidepoint(event.pos):
                    print('距離轉換器按鈕被點擊')

    # 依據遊戲狀態更新畫面
    if game_state == 'menu':
        display_menu_page()
    elif game_state == 'loading':
        display_loading_page()
        # 檢查執行緒是否還在運行
        if not loading_thread.is_alive():
            selected_exoplanet_name = random.choice(exoplanet_data['行星名稱'])
            game_state = 'room'
    elif game_state == 'room':
        display_room_page(selected_exoplanet_name)

    pygame.display.flip()

# 關閉pygame程式結束遊戲主循環
pygame.quit()
