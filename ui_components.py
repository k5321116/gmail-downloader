import flet as ft
from constants import UIConstants
class UIComponents:

    def __init__(self):
        self.after_input = self._create_date_input(
            "開始日",
            UIConstants.DEFAULT_START_DATE
        )
        self.before_input = self._create_date_input(
            "終了日",
            UIConstants.DEFAULT_END_DATE
        )
        self.search_btn = None
        self.download_btn = None
        self.data_table = self._create_data_table()
    
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
            icon=ft.Icons.SEARCH,
            on_click=on_click
        )
        return self.search_btn
    
    def create_download_button(self, count, on_click) -> ft.ElevatedButton:
        """ダウンロードボタンを作成"""
        if self.download_btn is not None:
            self.download_btn.text = f"{count}個のファイルを{UIConstants.DOWNLOAD_BTN_TEXT}"
            self.download_btn.disabled = True if count == 0 else False
            return self.download_btn
        
        self.download_btn = ft.ElevatedButton(
            f"{count}個のファイルを{UIConstants.DOWNLOAD_BTN_TEXT}",
            icon=ft.Icons.FILE_DOWNLOAD,
            on_click=on_click,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            disabled=True if count == 0 else False
        )
        return self.download_btn

    def _create_data_table(self) -> ft.DataTable:
        """データテーブルを作成"""
        columns = [ft.DataColumn(ft.Text(header)) for header in UIConstants.TABLE_HEADERS]
        return ft.DataTable(
            columns=columns,
            rows=[],
            data_row_min_height=40,
            data_row_max_height=120,
            show_checkbox_column=True
        )
    
    def create_scrollable_table(self):
        """スクロール可能なテーブルを作成"""
        return ft.Column(
            controls=[self.data_table],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True
        )
    
    def update_download_button_text(self, count: int):
        """ダウンロードボタンのテキストを更新"""
        print(f"Debug: ボタンの更新命令を受け取りました。現在のカウント={count}")
        if self.download_btn:
            self.download_btn.text = f"{count}個のファイルを{UIConstants.DOWNLOAD_BTN_TEXT}"
            self.download_btn.disabled = (count == 0)
            self.download_btn.update()
            
    def create_file_checkbox(self, filename: str, on_change) -> ft.Checkbox:
        """ファイル選択用チェックボックスを作成"""
        return ft.Checkbox(
            label=filename,
            value=False,
            on_change=on_change
        )
    
    def create_file_checkboxes_container(self, checkboxes: list) -> ft.Column:
        """チェックボックスのコンテナを作成"""
        return ft.Column(
            controls=checkboxes,
            spacing=0,
            scroll=ft.ScrollMode.AUTO
        )