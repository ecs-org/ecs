

def deliver(self, message, To=None, From=None):
    """
    Takes a fully formed email message and delivers it to ecs.ecsmail.mail.send_mail
    This gets monkey patched into lamson relay, to add support for standard ecs.ecsmail sending in case lamson
    somehow wants to send email (why ?, no idea)
    """
    from ecs.ecsmail.mail import send_mail
    
    recipient = To or message['To']
    sender = From or message['From']

    send_mail("[postmaster]", message, sender, recipient)        
