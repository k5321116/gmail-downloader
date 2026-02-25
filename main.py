import flet as ft
import asyncio
from view_manager import ViewManager
from constants import Routes, UIConstants
from ui_components import UIComponents
from event_handlers import EventHandlers
class GmailAttachmentDownloaderApp:

    def __init__(self, page: ft.Page):
        self.page = page
        self._setup_page()
        
        self.ui = UIComponents()
        self.event_handlers = EventHandlers(self.page, self.ui)
        self.view_manager = ViewManager(self.page, self.ui, self.event_handlers)
        self._setup_routing()

    async def run(self):
        self.page.overlay.append(self.ui.date_picker)
        self.ui.directory_picker.on_result = self.event_handlers.on_directory_result
        self.ui.date_picker.on_change = lambda e: self.event_handlers.on_date_change(e)

        self.page.update()

        await self.page.push_route(Routes.Home)

    def _setup_page(self):
        """ページの初期設定"""
        self.page.title = UIConstants.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[ft.Locale("ja", "JP")],
        current_locale=ft.Locale("ja", "JP")
    )

    def _setup_routing(self):
        """ルーティングの設定"""
        self.page.on_route_change = self._on_route_change
        self.page.on_view_pop = self._on_view_pop

    def _on_route_change(self, route=None):
        """ルート変更時の処理"""
        self.page.views.clear()
        
        if self.page.route == Routes.Home:
            self.page.views.append(self.view_manager.create_home_view())
        elif self.page.route == Routes.Result:
            scrollable_table = self.ui.create_scrollable_table()
            self.page.views.append(
                self.view_manager.create_result_view(scrollable_table)
            )
        elif self.page.route == Routes.Confirm:
            count = self.event_handlers.state.get_download_count()
            self.page.views.append(
                self.view_manager.create_confirm_view(count)
            )
        self.page.update()
    
    async def _on_view_pop(self, e):
        """戻るボタンを押したときの処理"""
        if e.view is not None:
            self.page.views.remove(e.view)
            top_view = self.page.views[-1]
            await self.page.push_route(top_view.route)

def main(page: ft.Page):
    app = GmailAttachmentDownloaderApp(page)
    page.run_task(app.run)

if __name__ == "__main__":
    ft.app(target=main)