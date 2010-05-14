import re


def strip_subject(subject):
    return re.match('(Re:\s)?(.*)', subject).group(2).strip()


def get_threads(messages):
    threads = []

    messages = list(messages)

    while messages:
        message = messages[0]
        thread = [message]
        while message.reply_to:
            thread.append(message.reply_to)
            message = message.reply_to

        for message in thread:
            if message in messages:
                messages.remove(message)

        threads.append({
            'subject': strip_subject(thread[0].subject),
            'messages': thread,
        })

    return threads


