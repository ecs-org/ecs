

def deliver(self, message, To=None, From=None):
    """
    Takes a fully formed email message and delivers it to ecs.ecsmail.mail.deliver
    This gets monkey patched into lamson relay, to add support for standard ecs.ecsmail sending in case lamson
    somehow wants to send email (why ?, no idea, just as backup, in case lamson somehow wants to send mail)
    """
    from ecs.ecsmail.mail import deliver as ecsmail_deliver
    
    recipient = To or message['To']
    sender = From or message['From']
    ecsmail_deliver(recipient, "[postmaster]", message, sender)
