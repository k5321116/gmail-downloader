import flet as ft
from ui_components import UIComponents
from constants import UIConstants, Routes

class ViewManager:

    def __init__(self, page):
        self.page = page
        self.ui = UIComponents()

    def create_home_view(self):

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