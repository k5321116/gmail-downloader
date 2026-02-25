import flet as ft
from constants import UIConstants
from datetime import datetime
class UIComponents:

    def __init__(self):
        self.date_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31))
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

        self.directory_picker = ft.FilePicker()
        self.folder_path_input = ft.TextField(
            label="保存先フォルダ",
            value=UIConstants.DEFAULT_SAVE_PATH,
            read_only=True,
            expand=True
        )
    
    @staticmethod
    def _create_date_input(label: str, value: str) -> ft.TextField:
        """日付入力フィールドを作成"""
        return ft.TextField(
            label=f"{label}({UIConstants.DATE_FORMAT})",
            value=value,
            text_align=ft.TextAlign.CENTER,
            width=150,
        )
    
    def _create_datepicker_input(self, label, value, on_click):
        return ft.TextField(
            label=f"{label}({UIConstants.DATE_FORMAT})",
            value=value,
            on_click=on_click,
            suffix_icon=ft.IconButton(ft.Icons.CALENDAR_MONTH,
                                      on_click = None),
            width=200,
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
        self.download_btn = ft.ElevatedButton(
            UIConstants.DOWNLOAD_BTN_TEXT,
            icon=ft.Icons.FILE_DOWNLOAD,
            on_click=on_click,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
        )
        return self.download_btn
    
    def create_folder_select_button(self, on_click):
        self.folder_select_btn = ft.ElevatedButton(
            UIConstants.SELECT_FOLDER_TEXT,
            icon=ft.Icons.FOLDER_OPEN,
            on_click=on_click,
            disabled=False
        )
        return self.folder_select_btn

    def _create_data_table(self) -> ft.DataTable:
        """データテーブルを作成"""
        columns = [ft.DataColumn(ft.Text(header)) for header in UIConstants.TABLE_HEADERS]
        return ft.DataTable(
            columns=columns,
            rows=[],
            data_row_min_height=40,
            data_row_max_height=120,
            show_checkbox_column=False
        )
    
    def create_scrollable_table(self):
        """スクロール可能なテーブルを作成"""
        return ft.Column(
            controls=[self.data_table],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True
        )
            
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