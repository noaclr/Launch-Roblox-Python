import requests
import subprocess
import time
from urllib.parse import urlencode, quote

class AuthenticationError(Exception):
    pass

def fetchAuthTicket(cookie):
    cookies = {".ROBLOSECURITY": cookie}
    r = requests.get("https://auth.roblox.com/v1/client-assertion", cookies=cookies)
    print(r.text)
    if "Authentication token is missing" in r.text:
        raise AuthenticationError("You forgot to provide a valid .ROBLOSECURITY cookie.")
    elif "User is not authenticated" in r.text:
        raise AuthenticationError("You provided an invalid .ROBLOSECURITY cookie.")
    clientAssertion = r.json()["clientAssertion"]
    
    r = requests.post("https://auth.roblox.com/v2/logout", cookies=cookies)
    csrfToken = r.headers.get("x-csrf-token")
    
    payload = {"clientAssertion": clientAssertion}
    headers = {"x-csrf-token": csrfToken, "Referer": "https://www.roblox.com/"}
    
    r = requests.post("https://auth.roblox.com/v1/authentication-ticket", data=payload, cookies=cookies, headers=headers)
    authTicket = r.headers.get("rbx-authentication-ticket")

    return authTicket

def launchRoblox(placeId, cookie):
    query = urlencode({
        "request": "RequestGame",
        "browserTrackerId": "", # dont have to set lol dumb analytics or smth
        "placeId": placeId,
        "isPlayTogetherGame": "false",
        "referredByPlayerId": 0,
        "joinAttemptId": "", # also dont gotta set this analytics too
        "joinAttemptOrigin": "PlayButton",
    })
    encodedPlaceUrl = quote(f"https://www.roblox.com/Game/PlaceLauncher.ashx?{query}", safe="")
    launchTime = int(time.time())
    robloxURI = (
        "roblox-player:1"
        + "+launchmode:play"
        + f"+gameinfo:{fetchAuthTicket(cookie)}"
        + f"+launchtime:{launchTime}"
        + f"+placelauncherurl:{encodedPlaceUrl}"
        + f"+browsertrackerid:"
        + "+robloxLocale:en_us"
        + "+gameLocale:en_us"
        + "+channel:"
        + "+LaunchExp:InApp"
    )
    try:
        subprocess.run([
            "powershell.exe",
            "-NoProfile",
            "-Command",
            f'Start-Process -FilePath "{robloxURI}"'
        ], check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["cmd.exe", "/c", "start", "", robloxURI], check=False)

launchRoblox(2753915549, "")
