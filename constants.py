from dataclasses import dataclass
from typing import Set, Tuple


class Routes:
    Home = '/home'
    Result = '/result'
    Confirm = '/confirm'
    Empty = '/empty'

class UIConstants:
    APP_TITLE = "Gmail Attachment Downloader"
    WELCOME_TEXT = "ようこそGmail Attachment Downloaderへ"
    SEARCH_BTN_TEXT = "検索開始"
    CONFIRM_BTN_TEXT = "はい"
    DOWNLOAD_BTN_TEXT = "確認画面へ"
    SEARCH_RESULT_TITLE = "検索結果"
    BACK_RESULT_BTN_TEXT = "検索結果に戻る"

    DATE_FORMAT = "YYYY/MM/DD"
    DEFAULT_START_DATE = "2026/02/15"
    DEFAULT_END_DATE = "2026/02/16"
    DATE_PICKER_HELP_TEXT = "日付を選択してください"

    NO_FILE_SELECTED = "ファイルを選択してください"
    DOWNLOAD_COMPLETE = "ダウンロード完了！"

    TABLE_HEADERS = ["選択", "日付", "件名", "添付ファイル"]
    SUBJECT_MAX_LENGTH = 20

    SELECT_FOLDER_TEXT = "保存フォルダを選択"
    DEFAULT_SAVE_PATH = "downloads/"

@dataclass
class AppState:
    """アプリケーションの状態を管理"""
    selected_files: Set[Tuple[str, str, str]]
    checkbox_map: dict
    
    def __init__(self):
        self.selected_files = set()
        self.checkbox_map = {}
    
    def add_file(self, message_id: str, attachment_id: str, filename: str):
        """選択ファイルを追加"""
        self.selected_files.add((message_id, attachment_id, filename))
    
    def remove_file(self, message_id: str, attachment_id: str, filename: str):
        """選択ファイルを削除"""
        self.selected_files.discard((message_id, attachment_id, filename))
    
    def clear_checkboxes(self):
        """チェックボックスマップをクリア"""
        self.checkbox_map.clear()
    
    def get_download_count(self) -> int:
        """選択されているファイル数を取得"""
        return len(self.selected_files)
