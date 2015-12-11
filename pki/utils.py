def get_subject(cn, email):
    subject_bits = (
        ('CN', cn),
        ('C', 'AT'),
        ('ST', 'Vienna'),
        ('localityName', 'Vienna'),
        ('O', 'Ethik Komission der med. Uni. Wien'),
        ('OU', 'Internal'),
        ('emailAddress', email),
    )
    return ''.join('/%s=%s' % bit for bit in subject_bits)
