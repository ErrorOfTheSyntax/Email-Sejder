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
        self.email_sender = "EmailSender@gmail.com"
        self.email_password = "EmailPassword"
        self.email_receivers = ["targetEmails@gmail.com"]
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
        
    #Stops the program if it is called
    def stop_program(self):
        self.loop = False

    #This function adds targets to the array called "email_reveivers"
    #It looks in the array for "," as that is the way of seperating emails
    #If "," isnt in the email given, then only one email will be added (that one)
    #If "," is in the email, it splits the email at each point "," is found
    #This splits each email into their own index within the email_list array
    #It then loops through the email_list and adds them to the email_receiverse
    #It checks each email to check if it matches the regex pattern
    #If it is a full match, then it is added to the email_receiverse
    
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

    #Simple function that changes the amount of time the email will be sent
    def change_amount(self, amount):
        self.amount_send = int(amount)

    #This function removes emails from the email_receivers list
    #The user can specify individual indexes e.g 0,1 and it will remove them
    #The user can also remove all items from a certain point
    #e.g 2:
    
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

    #This funciton simply changes the body of the email
    
    def change_body(self, new_body):
        self.body = new_body
        self.display_body = f"Body of email: {self.body}"
    
    #Basically in the message that is displayed in the screen, I onlt want to
    #display the body if the user wants to so the display_body variable is "" untill this function is called
    
    def display_body_email(self):
        self.display_body = f"Body of email: {self.body}"

    #This function simply changes the subject of the email
    
    def change_subject(self, new_subject):
        self.subject = new_subject
        self.display_subject = f"Subject of email: {self.subject}"
        
    #Basically in the message that is displayed in the screen, I onlt want to
    #display the subject if the user wants to so the display_subject variable is "" untill this function is called
    
    def display_subject_email(self):
        self.display_subject = f"Subject of email: {self.subject}"

    #This loops through the email list given in the choice variable
    #It used smtp to send the email from the email_sender account
    #It loggs in using the email_password
    
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
    
    #This function checks if there are any new emails in the inbox of the email sender
    #If not it will simple check again
    #If there is a new email it will display it and stop checking
    
    def check_mail(self):
        self.responses = checkEmail()
        print("Awating an email response.")
        while True:
            if self.responses is None:
                self.responses = checkEmail()
            else:
                print(f"Email response: {self.responses}")
                break
            
    #This stops the thread that checks for a response.
    
    def stop_checking_mail(self):
        self.stop_checking_mail = True
        
    #This uses threds to check the inbox of the email sender.
    #It constantly runs the check_mail function in the background.
    #Only if an email is found will it display anything.
    #If there is a new email it will display it and stop checking.
    #The user can also stop the thread using a keyboard Interrupt.
    
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
            
    #This is simple message outlining what the program can do.
    
    def displayInfo(self):
        os.system("cls")
        helpMenue = input("""THIS PROGRAM IS USED FOR SENDING EMAILS
This can be used to spamming etc
Using the -x options, sends an email and then using a thread waits for a response from any one of the emails.
This is just a test project so nothing serouus.

To exit this help menue press enter""")
        
    #This funciton find the indexes at which the target is found and adds that to a list

    def find_indexes(self,input_str, target):
        indexes = []
        for index, char in enumerate(input_str):
            if char == target:
                indexes.append(index)
        return indexes
    
    #This funciton takes in a stirng which is the users input/choice
    #This function loops through and splits each command within the input
    #This is done by splitting where there is a " -" in the input
    #It then returns a new list with all the individual commands 
    #They can then be looped through and executed
    
    def split_commands(self, input_str):
            commands = []
            current_command = ""
            words = input_str.split()
            
            for word in words:
                if word.startswith('-'):
                    if current_command:
                        commands.append(current_command)
                    current_command = word
                else:
                    current_command += " " + word
            
            if current_command:
                commands.append(current_command)
            
            return commands
        
    #These are all the options the user can select
    #They then execute the appropriate function based on the choice given
    
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
            self.send_emails(choice=choice[3:])
            print("Emails sent successfully")
            self.response()
            
        elif choice.startswith("--help") or choice.startswith("-h"):
            self.displayInfo()
    
    #Displays the menue and all the possible commands
    
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
                    commandList = self.split_commands(choice)
                    
                    for command in commandList:
                        self.options(command)
                    
                else:
                    self.options(choice)
                
            if self.send:
                self.send_emails()

        except KeyboardInterrupt:
            print("Stopping the program... ")
            sys.exit()
            
user_options = UserOptions()

user_options.run()
