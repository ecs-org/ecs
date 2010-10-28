

def deliver(self, message, To=None, From=None):
        """
        Takes a fully formed email message and delivers it to the
        configured relay server.

        You can pass in an alternate To and From, which will be used in the
        SMTP send lines rather than what's in the message.
        """
        from ecs.ecsmail import mail
        
        recipient = To or message['To']
        sender = From or message['From']

        mail.send_mail("[postmaster]", message, sender, recipient)        
        