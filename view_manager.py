import flet as ft
import asyncio
from constants import UIConstants, Routes

class ViewManager:

    def __init__(self, page, ui_components, event_handlers):
        self.page = page
        self.ui = ui_components
        self.event_handlers = event_handlers

    def create_home_view(self):
        self.ui.create_search_button(on_click=self.event_handlers.on_search_click)
        return ft.View(
                route=Routes.Home,
                    controls =[
                    ft.Column([
                        self._create_header(),
                        ft.Divider(),
                        self._create_search_section()
                    ],)
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER
            )
        

    def create_result_view(self, scrollable_table):
        current_count = self.event_handlers.state.get_download_count()
        download_btn = self.ui.create_download_button(
            count=current_count,
            on_click=self.event_handlers.on_download_click
        )
        return ft.View(
                route=Routes.Result,
                controls=[
                    ft.Column([
                        ft.AppBar(
                            title=ft.Text(UIConstants.SEARCH_RESULT_TITLE, color=ft.Colors.ON_SURFACE_VARIANT),
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            leading=ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=self.event_handlers.on_back_click
                            ),
                        ),
                        ft.Divider(),
                        scrollable_table
                    ], expand=True),
                    ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                        controls=[download_btn]
                    )
                ],
            )
    
    def create_confirm_view(self, count):
        # AppState から選択されたファイル名のみを抽出
        selected_files = self.event_handlers.state.selected_files
        file_names = [ft.Text(f"・{f[2]}", size=14) for f in selected_files] # f[2] が filename
        return ft.View(
            route=Routes.Confirm,
            scroll=ft.ScrollMode.AUTO, # ファイルが多い場合にスクロール可能にする
            controls=[
                ft.Column([
                    ft.Text("以下のファイルをダウンロードしますか？", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Column(file_names, spacing=5),
                        padding=20,
                        border_radius=10,
                        height = 200,
                    ),
                    ft.Text(f"合計: {count} 件", size=16),
                    ft.Row([
                        self.ui.folder_path_input,
                        self.ui.create_folder_select_button(
                            on_click=lambda _: (
                                self.page.run_task(
                                self._pick_directory)
                            )
                        ),
                    ]),
                    ft.Row([
                        ft.ElevatedButton(
                            UIConstants.CONFIRM_BTN_TEXT, 
                            on_click=self.event_handlers.on_confirm_download
                        ),
                        ft.OutlinedButton(
                            UIConstants.BACK_RESULT_BTN_TEXT, 
                            on_click=self.event_handlers.on_cancel_download
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
            ],
        )
    
    async def _pick_directory(self):
        path = await self.ui.directory_picker.get_directory_path(
            dialog_title=UIConstants.SELECT_FOLDER_TEXT
        )
        if path:
            self.ui.folder_path_input.value = path
            self.event_handlers.client.downloader.base_dir = path
            self.ui.folder_path_input.update()
            self.page.update()

    def _create_header(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    UIConstants.WELCOME_TEXT, 
                    size=30, 
                    weight=ft.FontWeight.BOLD
                )
            ],
        )
    
    def _create_search_section(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self.ui.after_input,                       
                self.ui.before_input, 
                self.ui.search_btn
            ],
        )