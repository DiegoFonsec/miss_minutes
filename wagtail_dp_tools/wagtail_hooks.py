from wagtail import hooks
from wagtail.admin.menu import MenuItem, SubmenuMenuItem, Menu
from django.urls import reverse

@hooks.register('register_admin_menu_item')
def register_dp_tools_menu():
    dp_tools_menu = Menu(items=[
        MenuItem(
            'CSRGenerator',
            reverse('csrgenerator_admin'),
            icon_name='code'
        ),
        MenuItem(
            'Slack',
            reverse('show_text'),
            icon_name='chat'
        ),
    ])

    return SubmenuMenuItem(
        'DP Tools',
        dp_tools_menu,
        icon_name='folder-open-1',
        order=9000
    )