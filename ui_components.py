import flet as ft
from constants import UIConstants

class UIComponents:

    def __init__(self):
        self.after_input = self._create_date_input(
            "開始日(yyyy/mm/dd)",
            UIConstants.DEFAULT_START_DATE
        )
        self.before_input = self._create_date_input(
            "終了日(yyyy/mm/dd)",
            UIConstants.DEFAULT_END_DATE
        )
        self.search_btn = None
        self.download_btn = None
        #self.data_table = self._create_data_table()
    
    @staticmethod
    def _create_date_input(label: str, value: str) -> ft.TextField:
        """日付入力フィールドを作成"""
        return ft.TextField(
            label=f"{label}({UIConstants.DATE_FORMAT})",
            value=value,
            text_align=ft.TextAlign.CENTER,
            width=150
        )
    
    def create_search_button(self, on_click) -> ft.ElevatedButton:
        """検索ボタンを作成"""
        self.search_btn = ft.ElevatedButton(
            UIConstants.SEARCH_BTN_TEXT,
            icon="search",
            on_click=on_click
        )
        return self.search_btn
    
    def create_download_button(self, on_click) -> ft.ElevatedButton:
        """ダウンロードボタンを作成"""
        self.download_btn = ft.ElevatedButton(
            UIConstants.DOWNLOAD_BTN_TEXT,
            icon=ft.Icons.FILE_DOWNLOAD,
            on_click=on_click,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE
        )
        return self.download_btn