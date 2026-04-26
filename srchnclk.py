import os
import ctypes
import pyautogui
import time
from datetime import datetime, timedelta

#---------------------------------------------------

TARGET_HOUR = 6
TARGET_MIN  = 30
IMAGE_DIR = "images"

#---------------------------------------------------

ES_CONTINUOUS       = 0x80000000
ES_SYSTEM_REQUIRED  = 0x00000002
ES_DISPLAY_REQUIRED = 0x00000001

def stay_awake( awake ):
    if awake:
        flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    else:
        flags = ES_CONTINUOUS
    
    ctypes.windll.kernel32.SetThreadExecutionState( flags )

def get_position( img_path ):
    retry = 5
    while retry > 0:
        pos = pyautogui.locateCenterOnScreen( img_path, confidence=0.8 )
        if pos:
            return pos
        retry -= 1
        time.sleep( 1 )

images = []
for f in os.listdir( IMAGE_DIR ):
    if f.endswith( ".png" ):
        images.append( os.path.join( IMAGE_DIR, f ) )

if not images:
    exit()

while True:
    try:
        for img in images:
            print( f"{img} をテストしています...", end="", flush=True )
            try:
                pos = get_position( img )
                print( "OK" )
            except pyautogui.ImageNotFoundException:
                print( "座標の取得に失敗" )
                print( "何かキーを押して再試行..." )
                input()
                raise Exception( "RETRY" )
        break
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        if str( e ) == "RETRY":
            continue
        else:
            print( type( e ) )
            exit()

now = datetime.now()
target = now.replace( hour=TARGET_HOUR, minute=TARGET_MIN, second=0, microsecond=0 )
if now > target:
    target += timedelta( days=1 )

target_unix = target.timestamp()

print( f"直近の {TARGET_HOUR}時 {TARGET_MIN}分 を待っています" )

stay_awake( True )
try:
    while True:
        now_unix = time.time()
        print( f"\r残り { int( target_unix - now_unix ) } 秒     ", end="", flush=True )
        if now_unix >= target_unix:
            print( "指定時間に到達しました。クリックを試行します..." )
            for img in images:
                print( f"{img}: ", end="" )
                try:
                    pos = get_position( img )
                    pyautogui.click( pos )
                    print( "OK" )
                except pyautogui.ImageNotFoundException:
                    print( "座標の取得に失敗" )
                time.sleep( 2 )
            break
        elif target_unix - now_unix < 10:
            pyautogui.moveRel(  1, 0 )
            pyautogui.moveRel( -1, 0 )
        time.sleep( 1 )
    print( "終了" )
    input()

except KeyboardInterrupt:
    pass

finally:
    stay_awake( False )
