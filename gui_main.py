import asyncio
import flet as ft
from gmail_utils import GmailClient


def get_data_table_columns(header):
    return [ft.DataColumn(ft.Text(t)) for t in header]

def main(page: ft.Page):
    page.title = "Gmail Attachment Downloader"
    page.theme_mode = ft.ThemeMode.SYSTEM
    after_input = ft.TextField(label="開始日(yyyy/mm/dd)", value="2026/02/10", text_align=ft.TextAlign.CENTER, width=150)
    before_input = ft.TextField(label="終了日(yyyy/mm/dd)", value="2026/02/16", text_align=ft.TextAlign.CENTER, width=150)
    client = GmailClient()
    selected_ids = set()
    selected_files = set()

    checkbox_map = {}

    def on_file_check(e, mid, filename):
        if e.control.value:
            selected_files.add((mid, filename))
        else:
            selected_files.discard((mid, filename))
        
        update_button_text()
        e.control.update()
        page.update()

    def on_row_select(e, rid):
        """行のチェックボックスが操作されたら、そのメールの全ファイルを連動させる"""
        is_selected = e.control.selected
        
        # そのメールに属する全チェックボックスを操作
        if rid in checkbox_map:
            for cb in checkbox_map[rid]:
                cb.value = is_selected
                # selected_files の更新
                fname = cb.label
                if is_selected:
                    selected_files.add((rid, fname))
                else:
                    selected_files.discard((rid, fname))
                cb.update()
        
        update_button_text()
        page.update()

    def update_button_text():
        """ボタンのテキストを一元管理"""
        download_btn.text = f"{len(selected_files)}個のファイルをダウンロード"

    def download_click(e):

        if not selected_files:
            page.snack_bar = ft.SnackBar(ft.Text("ファイルを選択してください"))
            page.snack_bar.open = True
            page.update()
            return
        
        from collections import defaultdict
        download_tasks = defaultdict(list)
        for mid, fname in selected_files:
            download_tasks[mid].append(fname)

        for mid, filenames in download_tasks.items():
            client.download_attachments(mid, save_dir='downloads', target_filenames=filenames)

        page.snack_bar = ft.SnackBar(ft.Text("ダウンロード完了！"))
        page.snack_bar.open = True
        page.update()

    def search_click(e):

        search_btn.disabled = True
        page.update()

        print(f"検索開始: {after_input.value} から {before_input.value}")
        df = client.get_messages_summary(after_input.value, before_input.value)

        data_table.rows.clear()
        checkbox_map.clear()
        for _, row in df.iterrows():
            mid = row["ID"]
            filenames = row["添付ファイル名"]

            checkbox_list = []
            for fname in filenames:
                cb = ft.Checkbox(
                    label=fname,
                    value=False,
                    on_change=lambda e, m=mid, f=fname: on_file_check(e, m, f)
                )
                checkbox_list.append(cb)

            checkbox_map[mid] = checkbox_list
            file_checkboxes_container = ft.Column(controls=checkbox_list, spacing=0)
            file_checkboxes_container.scroll = ft.ScrollMode.AUTO

            data_table.rows.append(
                ft.DataRow(
                    selected=False,
                    on_select_change=lambda e, rid=mid: on_row_select(e, rid),
                    cells=[
                        ft.DataCell(ft.Text(row["日付"])),
                        ft.DataCell(ft.Text(row["件名"][:20])),
                        ft.DataCell(content=file_checkboxes_container),
                    ],
                )
            )
        search_btn.disabled = False
        page.go("/result")

    header = ["日付", "件名", "添付ファイル名"]
    data_table = ft.DataTable(
        #show_checkbox_column=True,
        data_row_min_height=40,
        data_row_max_height=120,
        columns = get_data_table_columns(header),
        rows= [],
    )

    col = ft.Column(
        controls=[data_table],
        scroll=ft.ScrollMode.ALWAYS,
        expand=True
    )

    search_btn = ft.ElevatedButton("検索開始", icon="search", on_click=search_click)
    download_btn = ft.ElevatedButton("ダウンロードを開始する",
                                    icon=ft.Icons.FILE_DOWNLOAD, 
                                    on_click=download_click,
                                    bgcolor=ft.Colors.BLUE_700,
                                    color=ft.Colors.WHITE
                                     )

    def route_change():
        # ホーム画面
        if page.route == "/home":
            page.views.clear() # ページを一度クリアする 
            page.views.append(
                ft.View(
                    route="/home",
                    controls =[
                        ft.Column([
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls= [
                                        ft.Text("ようこそGmail Attachment Downloaderへ", size=30, weight=ft.FontWeight.BOLD),
                                                ],
                                        ),
                                ft.Divider(),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[after_input, before_input, search_btn],
                                        ),
                        ],)
                    ],
                )
            )
        # storeページ
        elif page.route == "/result":
            page.views.append(
                ft.View(
                    route="/result",
                    controls=[
                        ft.Column([
                            ft.AppBar(title=ft.Text("検索結果", color=ft.Colors.ON_SURFACE_VARIANT)),
                            ft.Divider(),
                            col
                        ], expand=True),
                        ft.Row(
                            controls=[download_btn]
                        )
                    ],
                )
            )

        page.update()

    # ←を押したときの処理
    async def view_pop(e):
        if e.view is not None:
            # 現在のページを除外する
            page.views.remove(e.view)

            # 1つ下のページに遷移する
            top_view = page.views[-1]
            print(top_view.route)
            await page.push_route(top_view.route)

    # 戻るボタンを押したときの処理
    page.on_view_pop = view_pop

    # ルート変更時の処理
    page.on_route_change = route_change

    # 初期画面(route = "/")に移動
    asyncio.create_task(page.push_route("/home"))

if __name__ == "__main__":
    ft.app(target=main)