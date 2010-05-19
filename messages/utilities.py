import re


def strip_subject(subject):
    return re.match('(Re:\s)?(.*)', subject).group(2).strip()


def get_threads(messages):
    # FIXME: this function fails, if the message timestamps are not correct
    messages = sorted(messages, key=lambda m: m.timestamp)

    threads = []

    while messages:
        message = messages[0]
        thread = [message]
        replies = list(message.replies.all())
        while replies:
            thread += replies

            # flatten 2-dimensional lists to 1-dimensional
            # [[1,2,3], [4,5,6]] => [1,2,3,4,5,6]
            replies = sum([list(reply.replies.all()) for reply in replies], []) 

        for message in thread:
            if message in messages:
                messages.remove(message)

        thread = sorted(thread, key=lambda m: m.timestamp, reverse=True)

        threads.insert(0, {
            'subject': strip_subject(thread[0].subject),
            'messages': thread,
        })


    return threads


