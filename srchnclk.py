import os
import sys
import getopt
import ctypes
import pyautogui
import time
from datetime import datetime, timedelta

#---------------------------------------------------

g_prefs = {
    "TargetHour": 6,
    "TargetMin" : 30,
    "ImageDir"  : "images"
}

#---------------------------------------------------

def stay_awake( awake ):
    ES_CONTINUOUS       = 0x80000000
    ES_SYSTEM_REQUIRED  = 0x00000002
    ES_DISPLAY_REQUIRED = 0x00000001

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

def parse_args( args_array ):
    if not args_array or len( args_array ) < 2:
        raise ValueError( "Invalid arguments" )
    
    hour, min = [ int( x ) for x in args_array[0].split( ":" ) ]

    if not ( hour >= 0 and hour < 23 ) or not( min >= 0 and min < 60 ):
        raise ValueError( "Invalid time format" )
    g_prefs["TargetHour"] = hour
    g_prefs["TargetMin"]  = min

    dir = args_array[1]
    if not os.path.isdir( dir ):
        raise ValueError( "No such image directory" )
    g_prefs["ImageDir"] = dir

try:
    parse_args( sys.argv[1:] )
except Exception as e:
    print( e )
    print( "Usage: %s TARGET_TIME[hh:mm] TARGET_DIR" % os.path.basename( sys.argv[0] ) )
    exit( 1 )

images = []
for f in os.listdir( g_prefs["ImageDir"] ):
    if f.endswith( ".png" ):
        images.append( os.path.join( g_prefs["ImageDir"], f ) )

if not images:
    print( "画像が見つかりませんでした" )
    exit( 1 )

while True:
    try:
        for img in images:
            print( f"{img} をテストしています...", end="", flush=True )
            try:
                pos = get_position( img )
                print( "OK" )
            except pyautogui.ImageNotFoundException:
                print( "座標の取得に失敗" )
                print( "Enterキーを押して再試行..." )
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
target = now.replace( hour=g_prefs["TargetHour"], minute=g_prefs["TargetMin"], second=0, microsecond=0 )
if now > target:
    target += timedelta( days=1 )

target_unix = target.timestamp()

print( f"直近の {g_prefs["TargetHour"]}時 {g_prefs["TargetMin"]}分 を待っています" )

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

except KeyboardInterrupt:
    stay_awake( False )
    sys.exit( 0 )

except Exception as e:
    import traceback
    traceback.print_exc()

stay_awake( False )
print( "Enterキーを押して終了..." )
input()
