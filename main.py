from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from datetime import datetime
from kivy.lang import Builder

# In-memory storage for user credentials
USER_CREDENTIALS = {}


class RegistrationScreen(Screen):                                                       
    def __init__(self, **kwargs):
        super(RegistrationScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        # Inputs for username and password
        self.username_input = TextInput(hint_text="Username", multiline=False)
        self.password_input = TextInput(hint_text="Password", multiline=False, password=True)

        # Register button
        register_button = Button(text="Register")
        register_button.bind(on_press=self.register)

        # Back button
        back_button = Button(text="Back")
        back_button.bind(on_press=self.go_back)

        # Add widgets to the layout
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(register_button)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def register(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        if username and password:
            if username in USER_CREDENTIALS:
                self.show_popup("Xtreme Gym World - Registration Error", "Username already exists.")
            else:
                USER_CREDENTIALS[username] = password
                self.show_popup("Xtreme Gym World - Success", "Registration successful!")
                self.manager.current = 'login'
        else:
            self.show_popup("Xtreme Gym World - Invalid Input", "Please enter both username and password.")

    def go_back(self, instance):
        self.manager.current = 'login'

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.username_input = TextInput(hint_text="Username", multiline=False)
        self.password_input = TextInput(hint_text="Password", multiline=False, password=True)
        login_button = Button(text="Login")
        register_button = Button(text="Register")
        login_button.bind(on_press=self.login)
        register_button.bind(on_press=self.go_to_registration)
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(login_button)
        layout.add_widget(register_button)
        self.add_widget(layout)

    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        if USER_CREDENTIALS.get(username) == password:
            self.manager.get_screen('main').set_username(username)
            self.manager.current = 'main'
        else:
            self.show_popup("Xtreme Gym World - Invalid credentials", "Please try again.")

    def go_to_registration(self, instance):
        self.manager.current = 'register'

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

class MainScreen(Screen):
    balance = 200
    initial_balance = 200
    popup_instance = None  # Track the current popup instance
    username = ''  # New attribute to store username
    logged_sales_total = 0  # Track total sales from logs

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.balance_label = Label(text=self.get_balance_text())
        self.option_button_layout = BoxLayout(orientation='vertical')
        options = [
            ("Daily Gym Workout", 1),
            ("Weekly Gym Workout", 2),
            ("Monthly Gym Workout", 3),
            ("Membership", 4),
            ("Personal Trainer", 5),
            ("Minus Sales", 6),
            ("Reset Sales", 8),
            ("Exit", 7)
        ]
        for text, option in options:
            button = Button(text=text)
            button.bind(on_press=lambda btn, opt=option: self.process_option(opt))
            self.option_button_layout.add_widget(button)

        # Log Sheet layout
        self.log_layout = BoxLayout(orientation='vertical')
        self.log_display = GridLayout(cols=1, size_hint_y=None)
        self.log_display.bind(minimum_height=self.log_display.setter('height'))
        self.log_scroll = ScrollView(size_hint=(1, 0.4), do_scroll_x=False, do_scroll_y=True)
        self.log_scroll.add_widget(self.log_display)

        self.log_input = TextInput(hint_text="Enter log", size_hint_y=None, height=30)
        log_button = Button(text="Add Log", size_hint_y=None, height=50)
        log_button.bind(on_press=self.add_log)

        self.log_layout.add_widget(self.log_scroll)
        self.log_layout.add_widget(self.log_input)
        self.log_layout.add_widget(log_button)

        layout.add_widget(self.balance_label)
        layout.add_widget(self.option_button_layout)
        layout.add_widget(self.log_layout)
        self.add_widget(layout)

    def set_username(self, username):
        self.username = username
        self.update_balance_label()  # Update balance label to include username

    def process_option(self, option):
        if option == 7:
            self.manager.current = 'login'
            return
        elif option == 8:
            self.reset_sales()
            self.add_log_to_display("Sales have been reset.")
            return
        elif option == 4:  # Membership
            self.show_membership_selection()
            return
        elif option == 2:  # Weekly Gym Workout
            self.show_weekly_gym_workout_options()
            return
        elif option == 1:  # Daily Gym Workout
            self.show_daily_gym_workout_options()
            return
        elif option == 3:  # Monthly Gym Workout
            self.show_monthly_gym_workout_options()
            return

        layout = BoxLayout(orientation='vertical')
        self.profit_input = TextInput(hint_text="Enter profit", multiline=False)
        process_button = Button(text="Process")
        process_button.bind(on_press=lambda btn: self.handle_option(option))
        layout.add_widget(self.profit_input)
        layout.add_widget(process_button)

        if self.popup_instance:
            self.popup_instance.dismiss()  # Close any existing popup before opening a new one

        self.popup_instance = Popup(title="Xtreme Gym World - Enter Profit", content=layout, size_hint=(None, None), size=(400, 200))
        self.popup_instance.open()

    def handle_option(self, option):
        try:
            profit = int(self.profit_input.text)
            if option in [1, 2, 3, 4, 5]:
                self.handle_sales(profit, 200000 if option in [1, 3] else 2000)
            elif option == 6:
                self.handle_minus_sales(profit, 2000)
        except ValueError:
            self.show_popup("Xtreme Gym World - Invalid Input", "Please enter valid numbers.")

        if option == 1:  # Daily Gym Workout
            self.add_log_to_display(f"Daily Gym Workout: Php {profit}")
        elif option == 2:  # Weekly Gym Workout
            self.add_log_to_display(f"Weekly Gym Workout: Php {profit}")
        elif option == 3:  # Monthly Gym Workout
            self.add_log_to_display(f"Monthly Gym Workout: Php {profit}")
        elif option == 5:  # Personal Trainer
            self.add_log_to_display(f"Personal Trainer: Php {profit}")
        elif option == 6:  # Minus Sales
            self.add_log_to_display(f"Minus Sales: Php {profit}")

    def show_daily_gym_workout_options(self):
        layout = BoxLayout(orientation='vertical')

        # TextInput for additional details
        self.details_input = TextInput(hint_text="Enter details", size_hint_y=None, height=30)

        membership_button = Button(text="Membership Workout")
        non_membership_button = Button(text="Non-Membership Workout")
        student_button = Button(text="Student Workout")
        membership_button.bind(on_press=self.handle_membership_workout)
        non_membership_button.bind(on_press=self.handle_non_membership_workout)
        student_button.bind(on_press=self.handle_student_workout)

        layout.add_widget(self.details_input)
        layout.add_widget(membership_button)
        layout.add_widget(non_membership_button)
        layout.add_widget(student_button)

        if self.popup_instance:
            self.popup_instance.dismiss()  # Close any existing popup before opening a new one

        self.popup_instance = Popup(title="Xtreme Gym World - Daily Gym Workout Options", content=layout, size_hint=(None, None), size=(400, 300))
        self.popup_instance.open()

    def handle_membership_workout(self, instance):
        details = self.details_input.text.strip()
        self.add_log_to_display(f"Membership Workout: Details - {details}")
        self.handle_sales(90, 200000)  # Example price and max_value
        self.close_popup()

    def handle_non_membership_workout(self, instance):
        details = self.details_input.text.strip()
        self.add_log_to_display(f"Non-Membership Workout: Details - {details}")
        self.handle_sales(199, 200000)  # Example price and max_value
        self.close_popup()

    def handle_student_workout(self, instance):
        details = self.details_input.text.strip()
        self.add_log_to_display(f"Student Workout: Details - {details}")
        self.handle_sales(60, 200000)  # Example price and max_value
        self.close_popup()

    def show_weekly_gym_workout_options(self):
        layout = BoxLayout(orientation='vertical')

        # TextInput for additional details
        self.details_input = TextInput(hint_text="Enter additional details", size_hint_y=None, height=30)

        one_week_button = Button(text="1 Week")
        two_weeks_button = Button(text="2 Weeks")
        one_week_button.bind(on_press=self.handle_one_week_workout)
        two_weeks_button.bind(on_press=self.handle_two_weeks_workout)

        layout.add_widget(self.details_input)
        layout.add_widget(one_week_button)
        layout.add_widget(two_weeks_button)

        if self.popup_instance:
            self.popup_instance.dismiss()  # Close any existing popup before opening a new one

        self.popup_instance = Popup(title="Xtreme Gym World - Weekly Gym Workout Options", content=layout, size_hint=(None, None), size=(400, 300))
        self.popup_instance.open()

    def handle_one_week_workout(self, instance):
        details = self.details_input.text.strip()
        self.add_log_to_display(f"Weekly Gym Workout - 1 Week: Details - {details}")
        self.handle_sales(389, 200000)  # Example price and max_value
        self.close_popup()

    def handle_two_weeks_workout(self, instance):
        details = self.details_input.text.strip()
        self.add_log_to_display(f"Weekly Gym Workout - 2 Weeks: Details - {details}")
        self.handle_sales(699, 200000)  # Example price and max_value
        self.close_popup()

    def show_membership_selection(self):
        layout = BoxLayout(orientation='vertical')

        # TextInput for additional details
        self.details_input = TextInput(hint_text="Enter additional details", size_hint_y=None, height=30)

        silver_button = Button(text="Silver Membership")
        gold_button = Button(text="Gold Membership")
        silver_button.bind(on_press=self.select_silver_membership)
        gold_button.bind(on_press=self.select_gold_membership)

        layout.add_widget(self.details_input)
        layout.add_widget(silver_button)
        layout.add_widget(gold_button)

        if self.popup_instance:
            self.popup_instance.dismiss()  # Close any existing popup before opening a new one

        self.popup_instance = Popup(title="Xtreme Gym World - Select Membership", content=layout, size_hint=(None, None), size=(400, 250))
        self.popup_instance.open()

    def select_silver_membership(self, instance):
        details = self.details_input.text.strip()
        self.handle_membership("Silver Membership", 399, details)
        self.close_popup()

    def select_gold_membership(self, instance):
        details = self.details_input.text.strip()
        self.handle_membership("Gold Membership", 599, details)
        self.close_popup()

    def handle_membership(self, membership_type, price, details):
        self.add_log_to_display(f"{membership_type}: Php {price} - Details: {details}")
        self.handle_sales(price, 200000)  # Update balance with the membership price

    def handle_sales(self, profit, max_value):
        if profit > max_value:
            self.show_popup("Xtreme Gym World - Error", "Over price!!!!!")
        elif profit > 0:
            MainScreen.balance += profit
            self.update_balance_label()
            self.show_popup("Xtreme Gym World - Success", f"Added to sales: Php {profit}")
        else:
            self.show_popup("Xtreme Gym World - Error", "Amount should be positive.")

    def handle_minus_sales(self, profit, max_value):
        if profit > max_value:
            self.show_popup("Xtreme Gym World - Error", "Over price!!!!!")
        elif profit > 0:
            if MainScreen.balance >= profit:
                MainScreen.balance -= profit
                self.update_balance_label()
                self.show_popup("Xtreme Gym World - Success", f"Minus to sales: Php {profit}")
            else:
                self.show_popup("Xtreme Gym World - Error", "Failed to minus sales.")
        else:
            self.show_popup("Xtreme Gym World - Error", "Amount should be positive.")

    def reset_sales(self):
        MainScreen.balance = MainScreen.initial_balance
        self.logged_sales_total = 0  # Reset logged sales total
        self.update_balance_label()
        self.clear_log_entries()  # Clear log entries when sales are reset

    def clear_log_entries(self):
        self.log_display.clear_widgets()  # Remove all widgets from the GridLayout

    def update_balance_label(self):
        self.balance_label.text = self.get_balance_text()

    def get_balance_text(self):
        now = datetime.now()
        total_sales = MainScreen.balance + self.logged_sales_total
        return f"Total Sales as of {now.strftime('%Y-%m-%d %H:%M:%S')} by {self.username}: Php {total_sales}"

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

    def close_popup(self):
        if self.popup_instance:
            self.popup_instance.dismiss()
            self.popup_instance = None

    def add_log(self, instance):
        log_text = self.log_input.text.strip()
        if log_text:
            try:
                # Extract profit from log text if it follows the pattern "Description: Php X"
                if 'Php' in log_text:
                    profit = int(log_text.split('Php')[1].strip())
                    self.logged_sales_total += profit
                self.add_log_to_display(log_text)
                self.log_input.text = ""
            except ValueError:
                self.show_popup("Xtreme Gym World - Invalid Log Entry", "Log entry format is incorrect.")

    def add_log_to_display(self, log_text):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = Label(text=f"{now} - {self.username} - {log_text}", size_hint_y=None, height=30)
        self.log_display.add_widget(log_entry)
        self.log_scroll.scroll_to(log_entry)

    def show_monthly_gym_workout_options(self):
        layout = BoxLayout(orientation='vertical')

        # TextInput for additional details
        self.details_input = TextInput(hint_text="Enter additional details", size_hint_y=None, height=30)

        one_month_button = Button(text="1 Month Workout")
        three_months_button = Button(text="3 Months Workout")
        six_months_button = Button(text="6 Months Workout")
        one_year_button = Button(text="1 Year Workout")
        one_month_button.bind(on_press=self.handle_one_month_workout)
        three_months_button.bind(on_press=self.handle_three_months_workout)
        six_months_button.bind(on_press=self.handle_six_months_workout)
        one_year_button.bind(on_press=self.handle_one_year_workout)

        layout.add_widget(self.details_input)
        layout.add_widget(one_month_button)
        layout.add_widget(three_months_button)
        layout.add_widget(six_months_button)
        layout.add_widget(one_year_button)

        if self.popup_instance:
            self.popup_instance.dismiss()  # Close any existing popup before opening a new one

        self.popup_instance = Popup(title="Xtreme Gym World - Monthly Gym Workout Options", content=layout, size_hint=(None, None), size=(400, 300))
        self.popup_instance.open()

    def handle_one_month_workout(self, instance):
        details = self.details_input.text.strip()
        self.add_log_to_display(f"Monthly Gym Workout - 1 Month: Details - {details}")
        self.handle_sales(999, 200000)  # Example price and max_value
        self.close_popup()

    def handle_three_months_workout(self, instance):
        details = self.details_input.text.strip()
        self.add_log_to_display(f"Monthly Gym Workout - 3 Months: Details - {details}")
        self.handle_sales(2699, 200000)  # Example price and max_value
        self.close_popup()

    def handle_six_months_workout(self, instance):
        details = self.details_input.text.strip()
        self.add_log_to_display(f"Monthly Gym Workout - 6 Months: Details - {details}")
        self.handle_sales(4999, 200000)  # Example price and max_value
        self.close_popup()

    def handle_one_year_workout(self, instance):
        details = self.details_input.text.strip()
        self.add_log_to_display(f"Monthly Gym Workout - 1 Year: Details - {details}")
        self.handle_sales(8999, 200000)  # Example price and max_value
        self.close_popup()

class GymApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegistrationScreen(name='register'))
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == '__main__':
    GymApp().run()
