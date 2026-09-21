import socket


def check_domain(domain: str = 'letrusto.com') -> dict:
    result = {'domain': domain, 'spf': 'NOT_FOUND', 'dkim': 'NOT_VERIFIABLE_WITHOUT_SELECTOR', 'dmarc': 'NOT_FOUND'}
    try:
        txt = socket.gethostbyname_ex(domain)
        result['domain_resolves'] = bool(txt[2])
    except OSError: result['domain_resolves'] = False
    try:
        import dns.resolver
        records = [str(record) for record in dns.resolver.resolve(domain, 'TXT')]
        result['spf'] = 'FOUND' if any('v=spf1' in record.lower() for record in records) else 'NOT_FOUND'
        dmarc = [str(record) for record in dns.resolver.resolve('_dmarc.' + domain, 'TXT')]
        result['dmarc'] = 'FOUND' if any('v=dmarc1' in record.lower() for record in dmarc) else 'NOT_FOUND'
    except Exception: result['lookup_note'] = 'Install dnspython for TXT-record checks; no DNS changes were made.'
    return result
