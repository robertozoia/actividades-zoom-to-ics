
import urllib


def zoom_join_urlscheme_desktop(confno, pwd, uname=None):
    
    payload = { 
        'confno': confno,
        'pwd': pwd,
    }
    if uname:
        payload['uname'] = uname

    r = "zoommtg://zoom.us/join?{}".format(
        urllib.parse.urlencode(payload)
    )
    return r


def zoom_join_urlscheme_mobile(confno, pwd, uname=None):
    
    payload = { 
        'confno': confno,
        'pwd': pwd,
    }
    if uname:
        payload['uname'] = uname

    r = "zoomus://zoom.us/join?{}".format(
        urllib.parse.urlencode(payload)
    )
    return r
