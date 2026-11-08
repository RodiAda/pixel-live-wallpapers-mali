#!/bin/bash
S=${ANDROID_SERIAL:?set ANDROID_SERIAL}
OUT=$1
: > $OUT
adb -s $S shell svc power stayon true
adb -s $S shell am force-stop com.google.android.apps.wallpaper
for c in $(adb -s $S shell cmd package query-services -a android.service.wallpaper.WallpaperService --brief | grep -E 'com.breel|pixel7' | tr -d ' \r'); do
  adb -s $S shell input keyevent KEYCODE_WAKEUP
  adb -s $S logcat -c
  adb -s $S shell am start -W -a android.service.wallpaper.CHANGE_LIVE_WALLPAPER --ecn android.service.wallpaper.extra.LIVE_WALLPAPER_COMPONENT "$c" >/dev/null 2>&1
  sleep 9
  log=$(adb -s $S logcat -d -v brief AndroidRuntime:E '*:S' | grep -A4 'FATAL EXCEPTION' | grep -E 'Exception|Error|shader|L000|S000' | grep -v 'FATAL EXCEPTION' | head -3 | tr '\n' ' ')
  died=$(adb -s $S logcat -d | grep -c 'has died.*\(breel\|pixel7\)')
  if [ -n "$log" ]; then echo "FAIL $c :: $log" >> $OUT; else echo "OK   $c (died=$died)" >> $OUT; fi
  adb -s $S shell input keyevent KEYCODE_BACK
  sleep 1
done
adb -s $S shell svc power stayon false
echo DONE >> $OUT
