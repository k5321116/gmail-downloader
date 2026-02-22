import flet as ft
import asyncio
from view_manager import ViewManager
from constants import Routes, UIConstants
from ui_components import UIComponents
class GmailAttachmentDownloaderApp:

    def __init__(self, page: ft.Page):
        self.page = page
        self._setup_page()
        
        self.view_manager = ViewManager(page)
        self._setup_routing()

    def _setup_page(self):
        """ページの初期設定"""
        self.page.title = UIConstants.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.SYSTEM
    
    async def run(self):
        await self.page.push_route(Routes.Home)

    def _setup_routing(self):
        """ルーティングの設定"""
        self.page.on_route_change = self._on_route_change
        #self.page.on_view_pop = self._on_view_pop

    def _on_route_change(self, route=None):
        """ルート変更時の処理"""
        self.page.views.clear()
        
        if self.page.route == Routes.Home:
            self.page.views.append(self.view_manager.create_home_view())
        """
        elif self.page.route == Routes.Result:
            scrollable_table = self.ui.create_scrollable_table()
            self.page.views.append(
                self.view_manager.create_result_view(scrollable_table)
            )
        """
        self.page.update()

def main(page: ft.Page):
    app = GmailAttachmentDownloaderApp(page)
    page.run_task(app.run)

if __name__ == "__main__":
    ft.app(target=main)