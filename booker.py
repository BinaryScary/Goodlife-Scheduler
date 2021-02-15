import requests
import schedule
import time
import datetime
import dateutil.parser

# edit to match your credentials, club, and time you want to book
username = ""
password = ""
clubID = 000

dayDelta = 7
timeDelta = 17 # 5:00pm

def scheduleBooking():
    print("[+] Attempting to find booking, current time %s" % datetime.datetime.now())
    # bookings open 7 days advance at 12am
    date = (datetime.date.today() + datetime.timedelta(days=dayDelta)).strftime("%Y-%m-%d")

    # closest booking time (could provide a range but you will probably get the first booking)
    bookingTime = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=dayDelta), datetime.time(timeDelta))

    # workout times request
    burp0_url = "https://www.goodlifefitness.com:443/content/goodlife/en/book-workout/jcr:content/root/responsivegrid/workoutbooking.GetWorkoutSlots.%d.%s.json" % (clubID,date)
    burp0_headers = {"User-Agent": "Mozilla/5.0 (Windows CE; en-US; rv:1.9.0.20) Gecko/20110704 Firefox/37.0", "Accept": "application/json, text/plain, */*", "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3", "Accept-Encoding": "gzip, deflate", "Connection": "close", "Referer": "https://www.goodlifefitness.com/book-workout.html"}
    resp = requests.get(burp0_url, headers=burp0_headers)

    # workouts for requested day
    workouts = resp.json()["map"]["response"][0]["workouts"]

    # get identifier
    identifier = 0
    for i in workouts:
        if dateutil.parser.parse(i["dateTime"],ignoretz=True) > bookingTime:
            print("[+] Found booking %s at time %s" % (i["identifier"],i["dateTime"]))

            if i["availableSlots"] == 0:
                print("[-] No available spots for booking %s" % i["identifier"])
                continue

            identifier = i["identifier"]
            break

    # auth request
    burp0_url = "https://www.goodlifefitness.com:443/content/experience-fragments/goodlife/header/master/jcr:content/root/responsivegrid/header.AuthenticateMember.json"
    burp0_headers = {"User-Agent": "Mozilla/5.0 (Windows CE; en-US; rv:1.9.0.20) Gecko/20110704 Firefox/37.0", "Accept": "application/json, text/plain, */*", "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3", "Accept-Encoding": "gzip, deflate", "CSRF-Token": "undefined", "Content-Type": "multipart/form-data; boundary=---------------------------133337152940597921353192389504", "Origin": "https://www.goodlifefitness.com", "Connection": "close", "Referer": "https://www.goodlifefitness.com/home.html"}
    burp0_data = "-----------------------------133337152940597921353192389504\r\nContent-Disposition: form-data; name=\"login\"\r\n\r\n%s\r\n-----------------------------133337152940597921353192389504\r\nContent-Disposition: form-data; name=\"passwordParameter\"\r\n\r\n%s\r\n-----------------------------133337152940597921353192389504--\r\n" % (username,password)
    resp = requests.post(burp0_url, headers=burp0_headers, data=burp0_data)

    if (not resp.ok):
        print("[!] Login failed")
        quit()

    # session token
    token = resp.cookies["secureLoginToken"]

    # booking request
    burp0_url = "https://www.goodlifefitness.com:443/content/goodlife/en/book-workout/jcr:content/root/responsivegrid/workoutbooking.CreateWorkoutBooking.json"
    burp0_cookies = {"secureLoginToken": token}
    burp0_headers = {"User-Agent": "Mozilla/5.0 (Windows CE; en-US; rv:1.9.0.20) Gecko/20110704 Firefox/37.0", "Accept": "application/json, text/plain, */*", "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3", "Accept-Encoding": "gzip, deflate", "CSRF-Token": "undefined", "Content-Type": "multipart/form-data; boundary=---------------------------374420118612092359992056587160", "Origin": "https://www.goodlifefitness.com", "Connection": "close", "Referer": "https://www.goodlifefitness.com/book-workout.html"}
    burp0_data = "-----------------------------374420118612092359992056587160\r\nContent-Disposition: form-data; name=\"clubId\"\r\n\r\n%s\r\n-----------------------------374420118612092359992056587160\r\nContent-Disposition: form-data; name=\"timeSlotId\"\r\n\r\n%s\r\n-----------------------------374420118612092359992056587160--\r\n" % (clubID, identifier)
    resp = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data)

    if(resp.status_code == 200):
        print("[+] Successful Booking, waiting 12 hours for next booking")
    else:
        print("[-] Booking unsuccessful")
        print(resp.text)

    return resp.status_code

# attempt multiple bookings
def attemptBooking():
    # attempt booking every 5 seconds for 10 minutes
    for i in range(120):
        if scheduleBooking() == 200:
            return
        time.sleep(5)

if __name__ == "__main__":
    print("[+] Starting booker at 24:00 every day")
    # schedule.every().day.at("00:00").do(attemptBooking)
    schedule.every().day.at("00:00").do(scheduleBooking)

    # print("[+] Starting booker every hour")
    # schedule.every().hour.do(scheduleBooking)

    while 1:
        schedule.run_pending()
        time.sleep(1)

# view bookings
# burp0_url = "https://www.goodlifefitness.com:443/content/goodlife/en/member-details/jcr:content/root/responsivegrid/myaccount/myclasses/myworkouts.GetMemberWorkoutBookings.2020-12-11.json"
# burp0_cookies = {"secureLoginToken": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIzOTQyNTciLCJmaXJzdE5hbWUiOiJcIlNhbVwiIiwibGFzdE5hbWUiOiJcIldvbmdcIiIsImVtYWlsIjoiXCJzYW1fd29uZzE1NkBob3RtYWlsLmNvbVwiIiwiaWF0IjoxNjA3NzA3MDc5LCJleHAiOjE2MDc4Nzk4Nzl9.nv17Ee-pAiN4tmC3RKgwPB03tdKKbrUzG0p1BmppTS0"}
# burp0_headers = {"User-Agent": "Mozilla/5.0 (Windows CE; en-US; rv:1.9.0.20) Gecko/20110704 Firefox/37.0", "Accept": "application/json, text/plain, */*", "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3", "Accept-Encoding": "gzip, deflate", "Connection": "close", "Referer": "https://www.goodlifefitness.com/member-details.html"}
# requests.get(burp0_url, headers=burp0_headers, cookies=burp0_cookies)
