'''
Created on May 13, 2022

Modified on May 16, 2022

@author: by hilee
'''

import pyrebase
import urllib

import time
import json
import sys, os

firebaseconfig={
    "apiKey": "AIzaSyCDUZO9ejB8LzKPtGB0_5xciByJvYI4IzY",
    "authDomain": "igrins2-hk.firebaseapp.com",
    "databaseURL": "https://igrins2-hk-default-rtdb.firebaseio.com",
    "projectId": "igrins2-hk",
    "storageBucket": "igrins2-hk.appspot.com",
    "messagingSenderId": "700525312748",
    "appId": "1:700525312748:web:71f4d67f89edda46d2c3c9",
    "measurementId": "G-GBDTV34X02"
}


#Read
def start_download_from_firebase(db):
    while True:
        last_dict = db.child("BasicHK").order_by_child("datetime").limit_to_last(1).get()
        if last_dict is None:
            #print("[start_download_from_firebase", "if last_dict is None:]")
            yield "Error"
        else:
            #print("[start_download_from_firebase", "else:]")
            item = last_dict[0].val()
            yield item
            

def main():
 
    print('================================================\n'
           'IGRINS House Keeping Status Downloader for Firebase\n'
           '                                Ctrl + C to exit\n'
           '================================================\n')
    while True:
        firebase = pyrebase.initialize_app(firebaseconfig)
        db = firebase.database()
        #print("[firebase = pyrebase.initialize_app(firebaseconfig)]")

        fb = start_download_from_firebase(db)
        try:
            while True:
                sleep_time = 60
                r = next(fb)
                if r == "Same":
                    print("Skipping, same as the last entry.")
                elif r == "Error":
                    print("Error reading the file, retrying in 10s.")
                    sleep_time = 10
                else:
                    json.dump(r, open("/DCS/HK_db.json", "w"))
                    cur_t = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                    print("Downloaded", r["date"], r["time"], "(", cur_t, ")")

                time.sleep(sleep_time)
                #print("[2nd while]")

        except KeyboardInterrupt:
            print("Quit.")
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        except:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
