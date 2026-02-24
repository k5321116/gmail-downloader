import flet as ft
from collections import defaultdict
from gmail_utils import GmailClient
from constants import UIConstants, AppState, Routes


class EventHandlers:
    """イベントハンドラを管理するクラス"""
    
    def __init__(self, page, ui_components):
        self.page = page
        self.ui = ui_components
        self.state = AppState()
        self.client = GmailClient()

    def on_search_click(self, e):
        """検索ボタンクリック時の処理"""
        self.ui.search_btn.disabled = True
        self.page.update()
        
        print(f"検索開始: {self.ui.after_input.value} から {self.ui.before_input.value}")

        df = self.client.search_attachments(self.ui.after_input.value, self.ui.before_input.value)
        if df is not None:
            self.state.clear_checkboxes()
            self.ui.data_table.rows.clear()

            for _, row in df.iterrows():
                self._create_table_row(row)

                self.page.go(Routes.Result)
        self.ui.search_btn.disabled = False
        self.page.update()

    def on_download_click(self, e):
        """ダウンロードボタンクリック時の処理"""
        if not self.state.selected_files:
            self._show_snackbar(UIConstants.NO_FILE_SELECTED)
            return
        
        self.ui.download_btn.disabled = True
        self.page.update()

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
                lambda e, m=message_id, a=aid, f=filename: self.on_file_check(e, m, a, f)
            )
            checkbox.data = aid
            checkbox_list.append(checkbox)
        
        self.state.checkbox_map[message_id] = checkbox_list
        file_checkboxes_container = self.ui.create_file_checkboxes_container(checkbox_list)
        
        # 行を追加
        self.ui.data_table.rows.append(
            ft.DataRow(
                selected=False,
                on_select_change=lambda e, rid=message_id: self.on_row_select(e, rid),
                cells=[
                    ft.DataCell(ft.Text(row["Date"])),
                    ft.DataCell(ft.Text(row["Subject"][:UIConstants.SUBJECT_MAX_LENGTH])),
                    ft.DataCell(content=file_checkboxes_container),
                ],
            )
        )

    def on_file_check(self, e, message_id: str, attach_id: str, filename: str):
        """個別ファイルのチェックボックス変更時の処理"""
        if e.control.value:
            self.state.add_file(message_id, attach_id, filename)
        else:
            self.state.remove_file(message_id, attach_id, filename)
        
        self._update_ui(e.control)

    def on_row_select(self, e, message_id: str):
        """行選択時の処理（メール全体の選択/解除）"""
        current_row = next((r for r in self.ui.data_table.rows if r.cells[0].content.value == message_id), None)
        if not current_row:
            return
        
        is_selected = e.data == "true"
        current_row.selected = is_selected
        
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
        self.ui.update_download_button_text(count)
        if control:
            control.update()
        self.page.update()

    def _show_snackbar(self, message: str):
        """スナックバーを表示"""
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()