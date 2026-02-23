import flet as ft
from ui_components import UIComponents
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
        download_btn = self.ui.create_download_button(on_click=None)
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
                        controls=[download_btn]
                    )
                ],
            )
    
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