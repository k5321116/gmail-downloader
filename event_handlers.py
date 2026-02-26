import flet as ft
import asyncio
from collections import defaultdict
from gmail_utils import GmailClient
from constants import UIConstants, AppState, Routes
from datetime import timezone, timedelta

class EventHandlers:
    """イベントハンドラを管理するクラス"""
    
    def __init__(self, page, ui_components):
        self.page = page
        self.ui = ui_components
        self.state = AppState()
        self.client = GmailClient()

    async def on_search_click(self, e):
        """検索ボタンクリック時の処理"""
        loading_dialog = ft.AlertDialog(
            content=ft.Row(
                [
                    ft.ProgressRing(), 
                    ft.Container(content=ft.Text("検索中..."), padding=ft.padding.only(left=10))
                ],
                tight=True,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            modal=True, # ダイアログの外側をクリックしても閉じないようにする
        )

        # ダイアログを表示
        self.page.dialog = loading_dialog
        self.page.dialog.open = True
        self.ui.search_btn.disabled = True
        self.page.update()

        try:
            df = await asyncio.to_thread(
                self.client.search_attachments,
                self.ui.after_input.value, 
                self.ui.before_input.value
            )

            self.page.dialog.open = False
            self.page.update()

            if df is not None and not df.empty:
                self.state.clear_checkboxes()
                self.ui.data_table.rows.clear()

                for _, row in df.iterrows():
                    self._create_table_row(row)

                self.page.go(Routes.Result)
                self._update_ui()
            else:
                self.page.go(Routes.Empty)
        except Exception as ex:
            self.page.dialog.open = False

        finally:
            self.ui.search_btn.disabled = False
            self.page.update()
    
    def on_calendar_click(self, e, target_input):
        self.ui.date_picker.data = target_input
        self.page.dialog = self.ui.date_picker
        self.page.dialog.open = True
        self.page.update()

    def on_date_change(self, e):
        if e.control.value:
            target_input = e.control.data
            date_value = e.control.value
            jst = timezone(timedelta(hours=9))
            date_value_jst = date_value.astimezone(jst)
            target_input.value = f"{date_value_jst.year}/{date_value_jst.month:02d}/{date_value_jst.day:02d}"
            target_input.update()
            self.ui.date_picker.open = False
            self.page.update()
    def on_download_click(self, e):
        count = self.state.get_download_count()
        if count == 0:
            self._show_snackbar(UIConstants.NO_FILE_SELECTED)
            return
        self.page.go(Routes.Confirm)

    def on_confirm_download(self, e):
        """ダウンロードボタンクリック時の処理"""
        try:
            # 2. AppState に保存されたタプルを1つずつ取り出して実行
            for m_id, a_id, fname in self.state.selected_files:
                # Client の downloader を直接使って個別保存
                self.client.downloader.download_attachments(
                    message_id=m_id,
                    attachment_id=a_id,
                    filename=fname
                )
            
            self._show_snackbar(UIConstants.DOWNLOAD_COMPLETE)
            
        except Exception as ex:
            self._show_snackbar(f"エラーが発生しました: {ex}")
            
        finally:
            self.ui.download_btn.disabled = False
            self.page.update()
            self._show_snackbar(UIConstants.DOWNLOAD_COMPLETE)
            self.page.go(Routes.Home)

    def on_directory_result(self, e: ft.FilePicker):
        print(f"on_directory_result fired: {e.path}")  # ← 追加
        
        if e.path:
            # 1. UI上のテキストを更新
            self.ui.folder_path_input.value = e.path
            self.ui.folder_path_input.update()
            self.client.downloader.base_dir = e.path
            
            self._show_snackbar(f"保存先を確定: {e.path}")

    def on_cancel_download(self, e):
        """ダウンロードキャンセル時の処理"""
        self.page.go(Routes.Result)

    def on_back_click(self, e):
        """戻るボタンクリック時の処理"""
        self.page.go(Routes.Home)

    def _create_table_row(self, row):
        """テーブルの行を作成"""
        message_id = row["ID"]
        attachments = row["Attachments"]
        
        # ファイルごとのチェックボックスを作成
        checkbox_list = []
        for attachment in attachments:
            filename = attachment['filename']
            aid = attachment['attachmentId']
            checkbox = self.ui.create_file_checkbox(
                filename,
                on_change=lambda e, m=message_id, a=aid, f=filename: self.on_file_check(e, m, a, f)
            )
            checkbox.data = aid
            checkbox_list.append(checkbox)
        
        self.state.checkbox_map[message_id] = checkbox_list
        file_checkboxes_container = self.ui.create_file_checkboxes_container(checkbox_list)
        
        row_checkbox = ft.Checkbox(
            value=False,
            on_change=lambda e, rid=message_id: self.on_row_checkbox_change(e, rid)
        )

        self.ui.data_table.rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(content=row_checkbox),  # 行選択用チェックボックス
                    ft.DataCell(ft.Text(row["Date"])),
                    ft.DataCell(ft.Text(row["Subject"][:UIConstants.SUBJECT_MAX_LENGTH])),
                    ft.DataCell(content=file_checkboxes_container),
                ],
            )
        )
        
        # 行のチェックボックスもマップに保存（後で同期に使う）
        self.state.checkbox_map[f"{message_id}_row"] = row_checkbox

    def on_file_check(self, e, message_id: str, attach_id: str, filename: str):
        """個別ファイルのチェックボックス変更時の処理"""
        if e.control.value:
            self.state.add_file(message_id, attach_id, filename)
        else:
            self.state.remove_file(message_id, attach_id, filename)

        self._update_row_checkbox(message_id)
        
        self._update_ui(e.control)

    def _update_row_checkbox(self, message_id: str):
        row_checkbox_key = f"{message_id}_row"
        if row_checkbox_key not in self.state.checkbox_map:
            return
        
        row_checkbox = self.state.checkbox_map[row_checkbox_key]

        if message_id in self.state.checkbox_map:
            all_checked = all(cb.value for cb in self.state.checkbox_map[message_id])
            any_checked = any(cb.value for cb in self.state.checkbox_map[message_id])
            row_checkbox.value = all_checked
            row_checkbox.update()

    def on_row_checkbox_change(self, e, message_id: str):
        is_selected = e.control.value
        
        if message_id in self.state.checkbox_map:
            for checkbox in self.state.checkbox_map[message_id]:
                checkbox.value = is_selected
                filename = checkbox.label
                aid = checkbox.data
                
                if is_selected:
                    self.state.add_file(message_id, aid, filename)
                else:
                    self.state.remove_file(message_id, aid, filename)
                
                checkbox.update()
        
        self._update_ui()
    
    def _update_ui(self, control=None):
        """UIを更新"""
        count = self.state.get_download_count()
        if control:
            control.update()
        if self.page:
            self.page.update()

    def _show_snackbar(self, message: str):
        """スナックバーを表示"""
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()

    def on_select_all(self, e):
        """表示されているすべてのファイルを選択状態にする"""
        for message_id, checkboxes in self.state.checkbox_map.items():
            # '_row' で終わるキー（行全体のチェックボックス）はスキップ
            if isinstance(message_id, str) and message_id.endswith("_row"):
                checkboxes.value = True
                checkboxes.update()
                continue
            
            # 各ファイルのチェックボックスを更新
            for cb in checkboxes:
                cb.value = True
                # AppStateへの追加処理 (message_id, attach_id, filename)
                # cb.data には attach_id を入れている前提
                self.state.add_file(message_id, cb.data, cb.label)
                cb.update()
        
        self._update_ui()

    def on_clear_all(self, e):
        """すべての選択を解除する"""
        for message_id, checkboxes in self.state.checkbox_map.items():
            if isinstance(message_id, str) and message_id.endswith("_row"):
                checkboxes.value = False
                checkboxes.update()
                continue

            for cb in checkboxes:
                cb.value = False
                self.state.remove_file(message_id, cb.data, cb.label)
                cb.update()
        
        self.state.selected_files.clear() # 集合を空にする
        self._update_ui()