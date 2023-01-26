#!/usr/bin/env python3

# This app made by futuresea-dev
# Github: https://github.com/futuresea-dev

# Imports
import random
from sys import exit
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from email_validator import validate_email, EmailNotValidError
import json
from widgets.searching_text import SearchingText
from kivymd.uix.gridlayout import MDGridLayout
import requests
from kivymd.uix.screen import MDScreen
from kivymd.uix.gridlayout import MDGridLayout
import webbrowser
from datetime import datetime
from kivy.lang import Builder
import threading
from kivy.clock import mainthread
from kivymd.toast import toast
from kivymd.app import MDApp
from widgets.hover_icon_button import HoverIconButton
from widgets.hover_flat_button import HoverFlatButton
from widgets.custom_scroll import CustomScroll
from widgets.searching_text import SearchingText
from kivy.properties import ListProperty, StringProperty, NumericProperty
from functools import partial

# KIVY config file
with open("main.kv") as kv:
    Builder.load_string(kv.read())

HOST_URL = 'http://192.168.113.171:8000/'
userToken = StringProperty('')
favList = []

# Login menu screens class


class LoginMenuScreen(Screen):

    # Check login password
    def login(self, email, password):
        if email != "" and password != '':
            params = json.dumps({'username': email, 'password': password})
            headers = {'Content-type': 'application/json',
                       'Accept': 'application/json'}
            req = UrlRequest(HOST_URL+'login/', method='POST', on_success=self.user_home_welcome, on_failure=self.user_login_error, req_body=params,
                             req_headers=headers)

        else:
            toast("Please. fill the input fields")

    def user_home_welcome(self, result, response):
        global userToken
        userToken = response['token']
        token = 'jwt ' + response['token']
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': token}
        req = UrlRequest(HOST_URL+'api/user/', method='GET', on_success=self.go_to_home, on_failure=self.user_login_error,
                         req_headers=headers)

    def go_to_home(self, result, response):
        id = response[0]["id"]
        username = response[0]["username"]
        email = response[0]["email"]
        self.manager.get_screen("Profile").ids.profile_txt.text = "[b]Member ID:\n[color=#FF0000]    " + str(
            id) + " [/color]\n\nUsername:[color=#FF0000]\n    " + str(username) + "[/color]\n\nEmail:\n[color=#FF0000]    " + str(email) + "[/color]\n\n"
        toast("login success!")
        self.manager.get_screen("MainMenu").search("")
        self.manager.get_screen("FavoriteMenu").search()
        self.manager.get_screen("MainMenu").add_book_widgets()
        self.manager.current = 'MainMenu'

    def user_login_error(self, result, response):

        if len(response) == 0:
            toast("Login Failed! Try Again")
        else:
            error = ""
            if 'username' in response:
                error += response['username'][0] + "\n"
            if 'password' in response:
                error += response['password'][0] + "\n"
            if 'non_field_errors' in response:
                error += response['non_field_errors'][0] + "\n"
            if error == "":
                toast(
                    "Login Failed! Try Again")
            else:
                toast(error)


# Main menu screen class
class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backend = BooksBackend()
        self.results = None
    pass

    @mainthread
    def add_book_widgets(self):
        global favList
        if self.results:
            self.ids.scroll_box.remove_widget(self.searching_text)
            for result in self.results:
                result_widget = BookCard()
                result_widget.ids.cover.source = str(result[2])
                result_widget.ids.book_name.text = str(result[0])
                result_widget.ids.author_name.text = str(result[1])
                result_widget.ids.book_summary.text = '...'
                result_widget.description = str(result[4])
                result_widget.ids.book_price.text = str(result[5])
                result_widget.link = str(result[3])
                for fav in favList:
                    if fav['book']['id'] == result[6]:
                        result_widget.ids.favorite_btn.text = "Remove Favorite"
                        break
                else:
                    result_widget.ids.favorite_btn.text = "Add Favorite"
                result_widget.ids.favorite_area.custom_id = result[6]
                self.ids.scroll_box.add_widget(result_widget)
        else:
            self.searching_text.text = "No results"
        self.ids.scroller.scroll_y = 1
        self.ids.search_button.disabled = False
        self.ids.search_button.canvas.get_group(
            'hidden')[0].rgba = (0, 0, 0, 0)

    def search(self, query):
        self.ids.scroll_box.clear_widgets()
        self.searching_text = SearchingText()
        self.ids.scroll_box.add_widget(self.searching_text)
        self.thread = threading.Thread(
            target=self.search_thread, args=(query,))
        self.thread.daemon = True
        self.thread.start()

    @mainthread
    def no_internet(self):
        self.ids.scroll_box.remove_widget(self.searching_text)

    def search_thread(self, query):
        self.results = None
        self.results = self.backend.scrape_all(query.strip())

        if self.results is None:
            self.no_internet()
            return

        self.add_book_widgets()

    def description(self, instance):
        if instance.ids.book_summary.text == "...":
            instance.ids.book_summary.text = instance.description
        else:
            instance.ids.book_summary.text = "..."

    def set_favorite(self, instance):
        global userToken
        custom_id = instance.ids.favorite_area.custom_id
        btn_txt = instance.ids.favorite_btn.text
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': 'jwt ' + userToken}
        params = json.dumps(
            {'book': int(custom_id)})
        if "Add" in btn_txt:
            req = UrlRequest(HOST_URL+'api/favorite/', method='POST', on_success=partial(self.success_add_toast, instance), on_failure=self.fail_add_toast, req_body=params,
                             req_headers=headers)
        else:
            req = UrlRequest(HOST_URL+'api/favorite/', method='Delete', on_success=partial(self.success_delete_toast, instance), on_failure=self.fail_delete_toast, req_body=params,
                             req_headers=headers)

    def success_add_toast(self, instance, result, response):
        toast('Add Favorite Success')
        # self.search(self.ids.searchbar.text)
        instance.ids.favorite_btn.text = "Remove Favorite"

    def fail_add_toast(self, result, response):
        toast('Add Favorite Failed')

    def success_delete_toast(self, instance, result, response):
        toast('Remove Favorite Success')
        # self.search(self.ids.searchbar.text)
        instance.ids.favorite_btn.text = "Add Favorite"

    def fail_delete_toast(self, result, response):
        toast('Remove Favorite Failed')


class BooksBackend():

    def scrape_all(self, text):
        try:
            page = requests.get(
                f"{HOST_URL}api/book/?search={text}").json()
            if page["count"] == 0:
                return False
            ids = []
            titles = []
            authors = []
            descriptions = []
            book_covers = []
            links = []
            prices = []
            items = page["results"]
            for i in items:
                try:
                    ids.append(i["id"])
                except BaseException:
                    ids.append("Could not find")
                try:
                    titles.append(i["name"])
                except BaseException:
                    titles.append("Could not find")
                try:
                    authors.append(i["author"]["name"])
                except BaseException:
                    authors.append('Could not find')
                try:
                    links.append(i["book_cover"])
                except BaseException:
                    links.append(
                        "http://books.google.com/books/content?id=QiM9EAAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api")
                try:
                    descriptions.append(i["description"])
                except BaseException:
                    descriptions.append("NONE")
                try:
                    book_covers.append(
                        i["book_cover"])
                except BaseException:
                    book_covers.append(
                        "https://www.archgard.com/assets/upload_fallbacks/image_not_found-54bf2d65c203b1e48fea1951497d4f689907afe3037d02a02dcde5775746765c.png")
                try:
                    prices.append(
                        i['price'])
                except BaseException:
                    prices.append("Not Listed")

            return [[titles[i], authors[i], book_covers[i], links[i],
                     descriptions[i], prices[i], ids[i]] for i in range(0, len(items))]
        except Exception as e:
            return None


class FavoriteBackend():

    def scrape_all(self):
        try:
            global userToken
            global favList
            headers = {'Content-type': 'application/json',
                       'Accept': 'application/json',
                       'Authorization': 'jwt ' + userToken}
            page = requests.get(
                f"{HOST_URL}api/favorite/", headers=headers).json()
            if len(page) == 0:
                favList = []
                return False

            ids = []
            titles = []
            authors = []
            descriptions = []
            book_covers = []
            links = []
            prices = []
            favList = page
            for i in favList:
                try:
                    ids.append(i['book']["id"])
                except BaseException:
                    ids.append("Could not find")
                try:
                    titles.append(i['book']["name"])
                except BaseException:
                    titles.append("Could not find")
                try:
                    authors.append(i['book']["author"]["name"])
                except BaseException:
                    authors.append('Could not find')
                try:
                    links.append(i['book']["book_cover"])
                except BaseException:
                    links.append(
                        "http://books.google.com/books/content?id=QiM9EAAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api")
                try:
                    descriptions.append(i['book']["description"])
                except BaseException:
                    descriptions.append("NONE")
                try:
                    book_covers.append(
                        i['book']["book_cover"])
                except BaseException:
                    book_covers.append(
                        "https://www.archgard.com/assets/upload_fallbacks/image_not_found-54bf2d65c203b1e48fea1951497d4f689907afe3037d02a02dcde5775746765c.png")
                try:
                    prices.append(
                        i['book']['price'])
                except BaseException:
                    prices.append("Not Listed")

            return [[titles[i], authors[i], book_covers[i], links[i],
                     descriptions[i], prices[i], ids[i]] for i in range(0, len(favList))]
        except Exception as e:
            favList = []
            return None

# Book Card class


class BookCard(MDGridLayout):
    pass
# Profile screen class


class ProfileScreen(Screen):
    pass

# Favorite menu screen class


class FavoriteMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backend = FavoriteBackend()
        self.results = None
    pass

    @mainthread
    def add_book_widgets(self):
        if self.results:
            self.ids.scroll_box.remove_widget(self.searching_text)
            for result in self.results:
                result_widget = BookCard()
                result_widget.ids.cover.source = str(result[2])
                result_widget.ids.book_name.text = str(result[0])
                result_widget.ids.author_name.text = str(result[1])
                result_widget.ids.book_summary.text = '...'
                result_widget.description = str(result[4])
                result_widget.ids.book_price.text = str(result[5])
                result_widget.link = str(result[3])
                result_widget.ids.favorite_btn.text = "Remove Favorite"
                result_widget.ids.favorite_area.custom_id = result[6]

                self.ids.scroll_box.add_widget(result_widget)
        else:
            self.searching_text.text = "No results"
        self.ids.scroller.scroll_y = 1

    def search(self):
        self.ids.scroll_box.clear_widgets()
        self.searching_text = SearchingText()
        self.ids.scroll_box.add_widget(self.searching_text)
        self.thread = threading.Thread(
            target=self.search_thread, args=())
        self.thread.daemon = True
        self.thread.start()

    @ mainthread
    def no_internet(self):
        self.ids.scroll_box.remove_widget(self.searching_text)

    def search_thread(self):
        self.results = None
        self.results = self.backend.scrape_all()

        if self.results is None:
            self.no_internet()
            return

        self.add_book_widgets()

    def description(self, instance):
        if instance.ids.book_summary.text == "...":
            instance.ids.book_summary.text = instance.description
        else:
            instance.ids.book_summary.text = "..."

    def set_favorite(self, instance):
        global userToken
        custom_id = instance.ids.favorite_area.custom_id
        btn_txt = instance.ids.favorite_btn.text
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': 'jwt ' + userToken}
        params = json.dumps(
            {'book': int(custom_id)})
        if "Remove" in btn_txt:
            req = UrlRequest(HOST_URL+'api/favorite/', method='Delete', on_success=self.success_delete_toast, on_failure=self.fail_delete_toast, req_body=params,
                             req_headers=headers)

    def success_delete_toast(self, result, response):
        toast('Remove Favorite Success')
        self.search()

    def fail_delete_toast(self, result, response):
        toast('Remove Favorite Failed')


class BookCard(GridLayout):
    pass


class RegisterMenuScreen(Screen):

    def register(self, username, email, password):
        try:
            validation = validate_email(email)
            email = validation.email
            if username != "" and password != "":
                params = json.dumps(
                    {'email': email, 'password': password, 'username': username})
                headers = {'Content-type': 'application/json',
                           'Accept': 'application/json'}
                req = UrlRequest(HOST_URL+'register/', method='POST', on_success=self.user_verify_email,
                                 on_failure=self.user_register_error, req_body=params,
                                 req_headers=headers)

            else:
                toast(
                    "Register Failed! Please fill in all inputs with valid information.")
        except EmailNotValidError as e:
            toast("Register Failed! Please fill in all inputs with valid information.")

    def user_verify_email(self, result, req):
        toast("Register Success. Please login.")
        self.manager.current = 'LoginMenu'

    def user_register_error(self, result, response):
        if len(response) == 0:
            toast("Register Failed! Please fill in all inputs with valid information.")
        else:
            error = ""
            if 'username' in response:
                error += response['username'][0] + "\n"
            if 'password' in response:
                error += response['password'][0] + "\n"
            if error == "":
                toast(
                    "Register Failed! Please fill in all inputs with valid information.")
            else:
                toast(error)


# Main class


class LMSApp(MDApp):

    userInfo = ""
    color_theme = 'dark'
    bg_color = ListProperty([29 / 255, 29 / 255, 29 / 255, 1])
    tile_color = ListProperty([40 / 255, 40 / 255, 40 / 255, 1])
    raised_button_color = ListProperty([52 / 255, 52 / 255, 52 / 255, 1])
    text_color = ListProperty([1, 1, 1, 1])
    title_text_color = ListProperty([1, 1, 1, 1])
    accent_color = ListProperty([0.5, 0.7, 0.5, 1])
    search_icon = StringProperty('magnify')
    search_icon_tooltip = StringProperty('Search')
    cursor_width = NumericProperty(3)
    home_icon = StringProperty('home')
    home_icon_tooltip = StringProperty('Back')
    add_icon = StringProperty('plus-circle-outline')
    add_icon_tooltip = StringProperty('Create new')
    # Build function

    def build(self):

        # root screen manager
        self.root = ScreenManager()

        # Login menu screen
        self.LoginMenuScreen = LoginMenuScreen(name='LoginMenu')
        self.root.add_widget(self.LoginMenuScreen)

        # Main menu screen
        self.MainMenuScreen = MainMenuScreen(name='MainMenu')
        self.root.add_widget(self.MainMenuScreen)

        # Favorite menu screen
        self.FavoriteMenuScreen = FavoriteMenuScreen(name='FavoriteMenu')
        self.root.add_widget(self.FavoriteMenuScreen)

        # Profile screen
        self.ProfileScreen = ProfileScreen(name='Profile')
        self.root.add_widget(self.ProfileScreen)

        # Register screen
        self.RegisterMenu = RegisterMenuScreen(name='RegisterMenu')
        self.root.add_widget(self.RegisterMenu)

        # Set current screen to Login menu and return root
        self.root.current = 'LoginMenu'
        return self.root


# run the class
LMSApp().run()
