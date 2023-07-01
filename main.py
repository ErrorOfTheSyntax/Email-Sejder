from email.message import EmailMessage
import ssl
import smtplib
from datetime import datetime
import os
import re
from colorama import Fore
from time import sleep
import textArt
import threading
from emailReciever import checkEmail
import sys
import signal

class UserOptions:
    def __init__(self):
        self.email_sender = "EmailName@gmail.com"
        self.email_password = "EmailPassword"
        self.email_receivers = ["enter@emails.com"]
        self.subject = "REQUIRED"
        self.body = "REQUIRED"
        self.amount_send = 1
        self.send = False
        self.loop = True
        self.regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        self.display_body = ""
        self.display_subject = ""
        self.display_error = ""
        self.responses = ""
        
        
        
    def down_by_one(self, arr):
        for i in range(len(arr)):
            arr[i] = int(arr[i]) - 1

    def stop_program(self):
        self.loop = False

    def add_target(self, email):
        if "," in email:
            email_list = email.split(",")
            email_list = [email.strip() for email in email_list]
            self.display_error = ""
            for i in range(len(email_list)):
                if re.fullmatch(self.regex, email_list[i]):
                    self.email_receivers.append(email_list[i])
                else:
                    if self.display_error == "":
                        self.display_error = f"Invalid Email Addres(s) [{email_list[i]}]"
                    else:
                        self.display_error = f"{self.display_error} [{email_list[i]}]"
        elif re.fullmatch(self.regex, email):
            self.email_receivers.append(email)
            self.display_error = ""
        else:
            if self.display_error != "":
                self.display_error = f"{self.display_error} [{email}]"
            else:
                self.display_error = f"Invalid Email Addres(s) [{email}]"

    def change_amount(self, amount):
        self.amount_send = int(amount)

    def remove_target(self, indexes):
        if ":" in indexes:
            indexOfColon = indexes.index(":")
            number = int(indexes[:indexOfColon])
            if number < len(self.email_receivers):
                del self.email_receivers[number:]
        try:
            to_remove = [int(idx) for idx in indexes.split(",")]
            to_remove = sorted(to_remove, reverse=True)
            
            for idx in to_remove:
                if 0 <= idx < len(self.email_receivers):
                    del self.email_receivers[idx]
        except ValueError:
            pass


    def change_body(self, new_body):
        self.body = new_body
        self.display_body = f"Body of email: {self.body}"

    def display_body_email(self):
        self.display_body = f"Body of email: {self.body}"

    def change_subject(self, new_subject):
        self.subject = new_subject
        self.display_subject = f"Subject of email: {self.subject}"

    def display_subject_email(self):
        self.display_subject = f"Subject of email: {self.subject}"

    def send_emails(self,choice=None):
        self.send = True
        self.loop = False
        if choice is not None:
            
            indexes = choice.split(",")
            indexes = [int(element) for element in indexes]
            self.email_receivers = [self.email_receivers[int(i)] for i in indexes]
            
        for _ in range(self.amount_send):
            context = ssl.create_default_context()
            for receiver in self.email_receivers:
                email_msg = EmailMessage()
                email_msg["From"] = self.email_sender
                email_msg["To"] = receiver
                email_msg["Subject"] = self.subject
                email_msg.set_content(self.body)

                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                    smtp.login(self.email_sender, self.email_password)
                    smtp.sendmail(self.email_sender, receiver, email_msg.as_string())
        
    def check_mail(self):
        self.responses = checkEmail()
        print("Awating an email response.")
        while True:
            if self.responses is None:
                self.responses = checkEmail()
            else:
                print(f"Email response: {self.responses}")
                break
    def stop_checking_mail(self):
        self.stop_checking_mail = True
        
    def response(self):
        emailThread = threading.Thread(target=self.check_mail)
        emailThread.start()
        try:
            while emailThread.is_alive():
                sleep(1)
        except KeyboardInterrupt:
            self.stop_checking_mail()
            print("Stopping email checking.")
            os.kill(os.getpid(), signal.SIGINT)
            
            quit()
            
            
    def displayInfo(self):
        os.system("cls")
        helpMenue = input("""THIS PROGRAM IS USED FOR SENDING EMAILS
This can be used to spamming etc
Using the -x options, sends an email and then using a thread waits for a response from any one of the emails.
This is just a test project so nothing serouus.

To exit this help menue press enter""")
    def find_indexes(self,input_str, target):
        indexes = []
        for index, char in enumerate(input_str):
            if char == target:
                indexes.append(index)
        return indexes
        commandList = inputString.split("-")
        commandList = [email.strip() for email in commandList]; del(commandList)[0]
        commandList = [f"-{item}" for item in commandList]
    def options(self,choice):
        if choice.startswith("-attack"):
                    
            if len(choice) >7:
                self.send_emails(choice=choice[8:])
                if len(self.email_receivers) > 1:
                    print(f"Attacking emails\n{self.email_receivers}")
                else:
                    print(f"Attacking the email\n{self.email_receivers}")
            else:
                self.send_emails()
                if len(self.email_receivers) > 1:
                    print(f"Attacking emails\n{self.email_receivers}")
                else:
                    print(f"Attacking the email\n{self.email_receivers}")
            print("Email sent successfully.")
        elif choice.startswith("-stop"):
            print("Stopping The Program")
            self.stop_program()
        elif choice.startswith("-a"):
            self.add_target(choice[3:])
        elif choice.startswith("-t"):
            self.change_amount(choice[3:])
        elif choice.startswith("-r"):
            self.remove_target(choice[3:])
        elif choice.startswith("-dc"):
            self.change_body(choice[4:])
        elif choice.startswith("-d"):
            self.display_body_email()
        elif choice.startswith("-sc"):
            self.change_subject(choice[4:])
        elif choice.startswith("-s"):
            self.display_subject_email()
        elif choice.startswith("-x"):
            self.send_emails()
            print("Emails sent successfully")
            self.response()
            
        elif choice.startswith("--help") or choice.startswith("-h"):
            self.displayInfo()
    
    def run(self):
    
        try:
            while not self.send and self.loop:
                current_datetime = datetime.now()
                formatted_datetime = current_datetime.strftime(r"%Y-%m-%d%H%M")
                os.system("cls")
                choice = input(Fore.RED + f"""
{formatted_datetime}                                                        
{textArt.displayArt()}
Email Spammer
Current targets: {self.email_receivers}
Current email amount = {self.amount_send}
{self.display_body}
{self.display_subject}\n
[To execute multiple commands please seperate with a space e.g -a em@em.com -dc Example]
-attack : sends the emails to all listed email. [For individual emails: -attack [index(s)] (seperate with commas)]
-stop : stops the program
-a [email]: adds target [To add multiple email addresses seperate with ","]
-t [amount]: change amount of time the email is sent
-r [index]: remove a target
-d : displays body of email
-dc [new body] : change body of email
-s : displays subject
-sc [new subject] : change subject of email
-x : attack and wait for response
--help or -h : Tells you about the program
{self.display_error}
""")            
                
                if len(self.find_indexes(choice,"-")) > 1:
                    commandList = choice.split("-")
                    print(commandList)
                    for command in commandList[1:]:
                        self.options(f"-{command.strip()}")
                    
                else:
                    self.options(choice)
                
            if self.send:
                self.send_emails()

        except KeyboardInterrupt:
            print("Stopping the program... ")
            sys.exit()
            
user_options = UserOptions()

user_options.run()
