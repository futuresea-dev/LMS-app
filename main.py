#!/usr/bin/env python3

# Barare By Kourva
# Github: https://github.com/Kourva

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
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from email_validator import validate_email, EmailNotValidError
import json
import urllib
import os

# KIVY config file
with open("main.kv") as kv:
    Builder.load_string(kv.read())

HOST_URL = 'http://localhost:8000/'


# Login menu screens class
class LoginMenuScreen(Screen):

    # Check login password
    def login(self, email, password, errorlable):
        if email != "":
            if email != '':
                params = json.dumps({'username': email, 'password': password})
                headers = {'Content-type': 'application/json',
                        'Accept': 'application/json'}
                req = UrlRequest(HOST_URL+'login/', method='POST', on_success=self.user_home_welcome, on_failure=self.user_login_error, req_body=params,
                                req_headers=headers)
                
        else:
            errorlable.text = "[b][color=#FF0000][font=RobotoMono-Regular]Login Failed! Try Again[/font][/color][/b]"

    def user_home_welcome(self, result, response):
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
        self.manager.get_screen("Profile").ids.profile_txt.text = "[b]Member ID:\n[color=#FF0000]    " + str(id) + " [/color]\n\nUsername:[color=#FF0000]\n    " + str(username) + "[/color]\n\nEmail:\n[color=#FF0000]    " + str(email) + "[/color]\n\n"
        self.manager.current = 'MainMenu'

    def user_login_error(self, *args):
        self.errorlable.text = "[b][color=#FF0000][font=RobotoMono-Regular]Login Failed! Try Again[/font][/color][/b]"


# Main menu screen class
class MainMenuScreen(Screen):
    pass

# Profile screen class
class ProfileScreen(Screen):
    pass

# About menu screen class
class AboutMenuScreen(Screen):
    pass


class RegisterMenuScreen(Screen):

    def register(self, username, email, password, errorlabel):
        try:
            validation = validate_email(email)
            email = validation.email
            if username != "" and password != "":
                params = json.dumps({'email': email, 'password': password, 'username': username})
                headers = {'Content-type': 'application/json',
                        'Accept': 'application/json'}
                req = UrlRequest(HOST_URL+'register/', method='POST', on_success=self.user_verify_email,
                                on_failure=self.user_register_error, req_body=params,
                                req_headers=headers)

            else:
                errorlabel.text = "[b][color=#FF0000][font=RobotoMono-Regular]Register Failed! Please fill in all inputs with valid information.[/font][/color][/b]"
        except EmailNotValidError as e:
            errorlabel.text = "[b][color=#FF0000][font=RobotoMono-Regular]Register Failed! Please fill in all inputs with valid information.[/font][/color][/b]"
    
    def user_verify_email(self, result, req):
        self.manager.current = 'LoginMenu'

    def user_register_error(self, *args):
        self.errorlabel.text = "[b][color=#FF0000][font=RobotoMono-Regular]Register Failed! Please fill in all inputs with valid information.[/font][/color][/b]"

# Main class
class LMSApp(App):
    userToken = ""
    userInfo = ""
    profile_txt = ""
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

        # About menu screen
        self.AboutMenuScreen = AboutMenuScreen(name='AboutMenu')
        self.root.add_widget(self.AboutMenuScreen)

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
