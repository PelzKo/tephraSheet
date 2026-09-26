from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from catalog import views as catalog_views
from characters.views import admin_mode, general, levelup, sheet, wizard

urlpatterns = [
    path("", general.character_list, name="character_list"),
    path("c/new/", general.character_new, name="character_new"),
    path("c/<int:pk>/", sheet.sheet_view, name="sheet"),
    path("c/<int:pk>/unlock/", general.unlock_view, name="unlock"),
    path("c/<int:pk>/lock/", general.lock_view, name="lock"),
    path("c/<int:pk>/password/", general.password_view, name="password"),
    path("c/<int:pk>/delete/", general.delete_view, name="delete_character"),
    path("c/<int:pk>/wizard/", wizard.wizard, name="wizard"),
    path("c/<int:pk>/wizard/<int:step>/", wizard.wizard, name="wizard_step"),
    path("c/<int:pk>/play/<slug:action>/", sheet.play_action, name="play"),
    path("c/<int:pk>/levelup/", levelup.levelup, name="levelup"),
    path("c/<int:pk>/levelup/options/", levelup.levelup_options, name="levelup_options"),
    path("c/<int:pk>/augments/", levelup.augments_view, name="augments"),
    path("c/<int:pk>/admin-mode/", admin_mode.toggle_admin, name="toggle_admin"),
    path("c/<int:pk>/misc/", admin_mode.misc_adjust, name="misc_adjust"),
    path("c/<int:pk>/edit/", admin_mode.edit_choices, name="edit_choices"),
    path("c/<int:pk>/items/<int:item_id>/", catalog_views.inventory_item_edit, name="inventory_item_edit"),
    path("catalog/", catalog_views.catalog_list, name="catalog"),
    path("catalog/new/", catalog_views.item_create, name="item_create"),
    path("catalog/<int:pk>/edit/", catalog_views.item_edit, name="item_edit"),
    path("catalog/<int:pk>/add/", catalog_views.add_to_inventory, name="add_to_inventory"),
    path("catalog/import/", catalog_views.import_view, name="catalog_import"),
    path("catalog/import/template.csv", catalog_views.import_template, name="catalog_import_template"),
    path("gm/login/", general.GMLoginView.as_view(), name="gm_login"),
    path("gm/logout/", auth_views.LogoutView.as_view(next_page="character_list"), name="gm_logout"),
    path("gm/", general.gm_settings, name="gm_settings"),
    path("gm/password/<int:pk>/", general.gm_reset_password, name="gm_reset_password"),
    path("admin/", admin.site.urls),
]
