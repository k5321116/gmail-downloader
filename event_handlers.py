import flet as ft
from collections import defaultdict
from gmail_utils import GmailClient
from constants import UIConstants, AppState, Routes
from ui_components import UIComponents


class EventHandlers:
    """イベントハンドラを管理するクラス"""
    
    def __init__(self, page, ui_components):
        self.page = page
        self.ui = ui_components
        self.state = AppState()
        #self.client = GmailClient()

    def on_search_click(self, e):
        """検索ボタンクリック時の処理"""
        self.ui.search_btn.disabled = True
        self.page.update()
        
        print(f"検索開始: {self.ui.after_input.value} から {self.ui.before_input.value}")

        self.ui.search_btn.disabled = False
        self.page.go(Routes.Result)

    def on_back_click(self, e):
        """戻るボタンクリック時の処理"""
        self.page.go(Routes.Home)


