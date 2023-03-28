import re
def valid_link(url):
    youtube_urls_test = ['']
    youtube_urls_test.pop(0)
    youtube_urls_test.append(url)
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(m\.youtube|youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match != None:
        return url
    else:
        raise Exception('NOT VALID URL')