# pixel-preview-fix

Xiaomi Filament super wallpapers (Earth, Moon) create a new `*MrePlayer` in every engine's `onCreate` and keep it,
together with `mIsPreview`, in fields of the service. On MIUI previews run in a separate `*PreviewSuperWallpaper`
service and process. Pixel's wallpaper picker previews the same service the active wallpaper runs in, so a preview
replaces the active wallpaper's player and preview flag: the wallpaper freezes and ignores screen/unlock events.

`Pixel{Earth,Moon}SuperWallpaper` extends the original service. When a non-preview engine with a player already
exists, `onCreateEngine` returns a plain engine that only draws the wallpaper thumbnail. The manifest service name is
switched to the subclass (`poolstr.py`), so the wallpaper has to be set again after updating.

Build (android.jar from platform-35, `src` plus `compile-only` on the classpath, compile-only classes not in the dex):

```
javac --release 11 -cp android.jar -d cls $(find src compile-only -name '*.java')
rm cls/com/miui/miwallpaper/*/superwallpaper/{Earth,Moon}SuperWallpaper.class
d8 --min-api 26 --lib android.jar --output out $(find cls <compiled miui-stubs classes> -name '*.class')
```

The resulting dex (stubs + these classes) replaces the stubs `classesN.dex`. `filamentsuper.py` patches
`filamentPause` (pause only when the screen is off or nothing is visible) and `getRefreshRate` (30).
