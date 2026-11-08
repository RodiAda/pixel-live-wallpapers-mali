# miui-stubs

Stub classes for MIUI framework members that Xiaomi super wallpapers call. Added to the APK as the next `classesN.dex`.

`android/content/*`, `android/view/View.java`, `android/net/Uri.java`, `android/os/Process.java` are compile-only and must not go into the dex.

```
javac --release 11 -d cls $(find . -name '*.java')
rm -r cls/android/content cls/android/view cls/android/net cls/android/os
d8 --min-api 26 --output . --classpath . $(find cls -name '*.class')
mv classes.dex miui-stubs.dex
```
