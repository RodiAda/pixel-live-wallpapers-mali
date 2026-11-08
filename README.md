# Old Pixel, OnePlus and Xiaomi live wallpapers on a Mali Pixel

Patches and tools that make old Pixel 1–7 live wallpaper ports, the OnePlus 8T / Cyberpunk 2077 wallpapers
and Xiaomi super wallpapers (Mars, Earth, Moon, Saturn, Snow Mountain) work on a Pixel 8 Pro
(Tensor G3, Mali-G715, Android 17).

No APKs are included. They belong to Google, Xiaomi, OnePlus and the people who ported them.
Download the original files from the links below, check the SHA-256, apply the patches and sign with your own key.
Offsets in this README are valid only for the exact versions listed.

## What breaks on Mali / recent Android

- **Strict GLSL.** Mali rejects shaders that Adreno accepted: a local variable shadowing a built-in (`map`),
  uniforms declared with different type or precision in vertex and fragment stages, `sampler2DArray`
  without a default precision. libGDX `ShaderProgram.pedantic` turns harmless unused uniforms into fatal errors.
- **`lowp` in vertex shaders is real fp16 on Mali.** Geometry collapses (Pixel 3 "Tactile" lost its objects).
  All `lowp` raised to `highp`.
- **No storage buffers in vertex shaders** (`GL_MAX_VERTEX_SHADER_STORAGE_BLOCKS = 0`, also through ANGLE).
  Unity 2019 instanced particles use one, so the shader fails and the wallpaper crashes.
- **Android 14+ background activity launch** blocks Pixel 5 "Conveyor" quiz activity unless the app holds
  `SYSTEM_ALERT_WINDOW`.
- **Pixel never sends `android.wallpaper.keyguardgoingaway`.** Xiaomi wrappers on Android 14+ wait for it,
  so the scene never lands after unlock.
- **Xiaomi originals call MIUI framework classes** (`android.provider.MiuiSettings`, `miui.os.Build`,
  `miui.util.FeatureParser`, …) that do not exist on Pixel.
- **libGDX race:** `AndroidLiveWallpaperService.onDestroy` nulls `app` but not `linkedEngine`;
  a late visibility change then calls `app.onPause()` on null.

## Sources

| package | source | version | SHA-256 of the file used |
|---|---|---|---|
| com.breel.geswallpapers (Pixel 1) | iKirby, [XDA: All Google Pixel Live Wallpapers (1-5)](https://xdaforums.com/t/port-app-11-0-all-google-pixel-live-wallpapers-1-5.4180417/) | 10 (29) | |
| com.breel.wallpapers (Pixel 2) | same thread | 11 (30) | |
| com.breel.wallpapers18 (Pixel 3) | same thread | 12 (31) | |
| com.breel.wallpapers19 (Pixel 4, has Doodle V2/V3) | Pranav Pandey, [APKMirror](https://www.apkmirror.com/apk/pranav-pandey/) | 10 PP-7.0+ arm64 (29) | |
| com.breel.wallpapers20 (Pixel 5, has Conveyor) | iKirby, same XDA thread | 13 (33) | |
| com.breel.wallpapers20a (Pixel 4a, Eclipse) | iKirby, same XDA thread | 13 (33) | |
| com.google.pixel7.livewallpaper | [XDA: All Pixel 1-8 live wallpapers apk ports](https://xdaforums.com/t/all-pixel-1-8-live-wallpapers-apk-ports.4483407/) | 2.0 (9355839) | |
| com.oneplus.wallpaper.linuxct (OnePlus 8T) | linuxct, [XDA article](https://www.xda-developers.com/download-oneplus-8t-live-wallpapers-any-android-device) | 1.0.2.20211117 | `b83e7bceab39eb8a1383e56a80a9690660a3a74ddd76717b41b489d9b16cfc27` |
| net.oneplus.wallpaperresources.linuxct (Cyberpunk 2077) | linuxct, [XDA thread](https://forum.xda-developers.com/t/8-0-oneplus-cyberpunk-2077-edition-live-wallpapers-ported-to-any-android-device.4164033/) | 2.0.1.200916023912.182b9b6-linuxct | `58a1d0bb96f0350aa10083e9ce95ae86650af53c26d82dc3f2a24d3079278df1` |
| com.miui.miwallpaper.mars (5 scenes, Unity 2019) | Ouxyl, [APKMirror](https://www.apkmirror.com/apk/ouxyl/superwallpapermars-ouxyls-mod) | ALPHA-2.6.561-11211547-ogl-64-fix1 | `ac5a8f0b554aa4bcc5cf83975ec0d1210a84633bcee70a2dc1ba77400d746229` |
| com.miui.miwallpaper.mars (Xiaomi original, Unity 2022) | Xiaomi, [APKMirror](https://www.apkmirror.com/apk/xiaomi-inc/superwallpapermars/) | ALPHA-2.6.574-11131423-ogl-64 | `9800c1ce4f0c0005c541670d3f31bb021cf23db698fe6d4cc027f9775162ac17` |
| com.miui.miwallpaper.snowmountain | Xiaomi, [APKMirror](https://www.apkmirror.com/apk/xiaomi-inc/) (SuperWallpaperSnowmountain) | ALPHA-2.6.572-07311113-ogl-64 | `41c0971171ec5b01d0c2c7cb920b0c7f47598b67e7fc4b0cc5008ac599d43689` |
| com.miui.miwallpaper.saturn | Xiaomi, [APKMirror](https://www.apkmirror.com/apk/xiaomi-inc/) (SuperWallpaperSaturn) | ALPHA-2.6.574-11141617-ogl-64 | `f8ec9c7b9b7662778df6bdbd98373998dc71185424cb8bf1d6fabb52f4ade593` |
| com.miui.miwallpaper.earth | Xiaomi, [APKMirror](https://www.apkmirror.com/apk/xiaomi-inc/superwallpaperearth/) | ALPHA-2.6.575-09041449-ogl-64 | `eb2370c4e66e06c321b7cd05713eee802e2e9dfe95527f5bc85af009fc568fa1` |
| com.miui.miwallpaper.moon | Xiaomi, [APKMirror](https://www.apkmirror.com/apk/xiaomi-inc/) (The Moon Super wallpapers) | ALPHA-2.6.575-09041449-ogl-64 | `807ae48b09ab8185a72d2b77c39465f5d0ec88e4bea7e159fbded0bcefa05d25` |

For Xiaomi pick builds whose name ends in `ogl-64`. `vulkan` builds and 32-bit linuxct builds (`armeabi-v7a` only)
are untested; the latter do not install on 64-bit-only Pixels.

Installed unpatched and working: ustwo Live Data, Pokémon, `com.google.pixel.wallpapers23` (Pixel 8).

## Patches

### Pixel (breel, libGDX)

All packages:
- every `lowp` in shaders → `highp`;
- `ShaderProgram.pedantic` → false (`tools/dexpatch.py`);
- `AndroidWallpaperEngine.onPause`: null check reads `app` instead of `linkedEngine` (`tools/gdxpause.py`).

| package | extra |
|---|---|
| Pixel 1 | `earth.frag` precision |
| Pixel 3 | surfandturf: local `map` renamed; tactile background precision |
| Pixel 4 | `planet.vert`: `u_light` declared `vec3` as in the fragment stage |
| Pixel 5 | phong shader precision; manifest `WRITE_EXTERNAL_STORAGE` → `SYSTEM_ALERT_WINDOW`, then `adb shell appops set com.breel.wallpapers20 SYSTEM_ALERT_WINDOW allow` (Conveyor settings activity) |
| Pixel 7 | `settingsSliceUri` authority `pixel` → `pixel7` in resources.arsc (colour settings) |

Validate shaders with `tools/check.py <extracted-apk-dir>` (glslang, `#include` expansion, vert/frag link check).

### OnePlus 8T and Cyberpunk 2077

- `depth.frag`, `shape.frag`: `precision highp sampler2DArray;`, `lowp` → `highp`.
- `WallpaperContract$Images.getImageDir` made public, it is called from another package (`tools/dexpublic.py`).
- `VideoEngine.onCompletion`: the `releaseMediaPlayer` call (0x421448) replaced by nops, so the
  Cyberpunk video stops on its last frame instead of going black.
- Resources package: package name and provider authority `…linuxct` → `…linuxct.wakawaka` (manifest and arsc,
  `tools/poolstr.py`, `tools/arscstr.py`); app 1.0.2 looks for resources only under that name.
- Use "OnePlus Wallpaper Config" → "Always On Mod" or "Long Mod". The plain variant only plays on OnePlus
  fingerprint unlock events.

### Xiaomi super wallpapers, common wrapper (`tools/buildmiui.py`)

`buildmiui.py src.apk out.apk bt=<android build-tools dir> [pkg=old=>new] [labelref=0x..=>0x..] [label=old=>new]`
with `KS_PASS` (and optionally `KEYSTORE`, `KS_ALIAS`) in the environment. It does:

- `tools/miuisuper.py` on the dex with `basesuperwallpaper.SuperWallpaper`, found by symbol, not offset:
  - `SystemBuildUtils.isAndroidUAtLeast()` → false: screen and unlock come from
    `SCREEN_ON`/`SCREEN_OFF`/`USER_PRESENT` broadcasts instead of wallpaper commands Pixel never sends;
  - strings `android.wallpaper.goingtosleep` / `wakingup` → `…q`, so the two notification paths
    do not fight (the camera went back to AOD right after unlock);
  - `UnityPlayer.quit()` on the 10 s init timeout removed (a process started with the screen off was
    killed and crashed on unlock);
  - `unityPause()` pauses only when the screen is off or no surface is visible; MIUI paused 5 s after
    every event, which froze the scene and the accelerometer tilt on the home screen;
  - `getRefreshRate()` → 30 (was the display rate, up to 120);
  - `SuperWallpaperEngine.onCreate` no longer writes the process-wide `mIsPreview`: a picker preview
    engine created after the real one set it and all lock/unlock handling stopped;
- MIUI stubs (`tools/miui-stubs`, see `BUILD.md` there) added as the next `classesN.dex`;
- the `…PreviewSuperWallpaper` service loses its `android.service.wallpaper` meta-data (`tools/axmlhide.py`),
  otherwise the picker lists the wallpaper twice and fails when the second one is chosen;
- `supportsAmbientMode` → false (`tools/axmlbool.py`): it requires the privileged `AMBIENT_WALLPAPER`
  permission and setting the wallpaper fails with `SecurityException`;
- optional label replacement.

AOD fly-in (dark far view → lock view when the screen turns on) needs two settings the wrapper reads;
`doze_always_on` is already 1 on Pixel:

```
adb shell settings put secure aod_using_super_wallpaper 1
adb shell settings put system lock_wallpaper_provider_authority com.android.thememanager.theme_lock_live_wallpaper
```

Pixel does not draw the wallpaper on AOD, so the far view is visible only for the moment the screen wakes.

Per package:

| package | engine | extra |
|---|---|---|
| Snow Mountain | Unity 2022.3.33f1 | `label=四姑娘山=>Снежная гора` (optional) |
| Mars (Xiaomi) | Unity 2022.3.33f1 | `pkg=com.miui.miwallpaper.mars=>com.miui.miwallpaper.marsx` plus the arsc package name, to install next to the Ouxyl port. One wallpaper, 5 landing sites: `adb shell am broadcast -a miui.miwallpaper.action.LAND_CHANGE --ei position N` (0–4) |
| Saturn | Unity 2022.3.33f1 | `labelref=0x7f0f0032=>0x7f0f0033`: the service label is the bare word "saturn", point it at the title string |
| Earth | Google Filament | — |
| Moon | Google Filament | before `buildmiui.py`, nop the two `Settings.Global.putLong/putInt` calls in `MoonPhaseUpdateHelper.notifyAllMoonPhaseChangeChecked` (classes.dex 0x3e3e30, 0x3e3e42): writing global settings needs `WRITE_SECURE_SETTINGS` and crashes the service; the in-process callbacks still deliver the phase |

### Mars, Ouxyl port (Unity 2019.3.15f1)

Everything from the common wrapper section done by hand (offsets for this build:
`unityPause` 0x59b8f0, `getRefreshRate` 0x59b308, `SuperWallpaper$2.handleMessage` quit at 0x598b20,
`isAndroidUAtLeast` 0x5a1748), plus:

- **Particles/Standard Unlit**: 8 GLES vertex variants read `unity_ParticleInstanceData` from a storage buffer.
  The buffer is removed with UnityPy and instanced particles are moved off-screen
  (`tools/findssbo.py`, `tools/patchssbo.py`, asset `assets/bin/Data/0000000000000000f000000000000000`).
- **libunity pointer table**: the China-branch 2019.3.15f1 tracks pointers in 5 windows of 4 GB (`addr >> 32`).
  A sixth window gives index −1 and SIGSEGV on about 60 % of starts. Widened to 32 GB windows
  (`addr >> 35`, level-1 index bits 25–34, 1024+1 entries, counter at +0x2000): 13 instructions in
  `tools/libunity-mars-ptrtable.patches.txt`.
- **One process per scene** (`:mars0` … `:mars4`, `tools/axmlprocess.py`): two UnityPlayers in one process
  (active scene plus a preview of another) crashed both.
- **Landing direction** (libil2cpp `CameraCtrl`, angle helper 0x8cf650): `b.pl` at 0x8cf7d0 → `b`, so the
  landing turn keeps the planet's idle direction instead of the shortest way back.
- **Landing time** 0x8cec80–0x8ceca0: constant `20/H` → `(10 + |angle|/16)/H` (`H = planetLandRotHSpeed = 35`).
- Author string "Ported by t.me/AppPorts" emptied in resources.arsc.

## Rebuilding an APK

```
python3 tools/rezip.py src.apk unsigned.apk classes.dex=patched/classes.dex ...
zipalign -f -P 16 4 unsigned.apk aligned.apk
apksigner sign --ks your.jks --out final.apk aligned.apk
```

`rezip.py` keeps each entry's compression method (native libs must stay stored) and drops the old signature.
Everything in `tools/` that edits a dex fixes the SHA-1 and Adler-32 checksums.
Keep your key: updating a package signed with a different key means uninstalling it and losing its settings.

## Tools

| tool | what it does |
|---|---|
| `check.py` | glslang validation of extracted shaders with `#include` expansion and vert/frag link check |
| `dexpatch.py` | libGDX `ShaderProgram.pedantic` → false |
| `gdxpause.py` | libGDX `onPause` null-check fix |
| `dexpublic.py` | make a method and its class public |
| `dexcode.py` | crude disassembler for one method |
| `arscstr.py`, `poolstr.py` | replace strings in resources.arsc / binary XML string pools |
| `axmlattr.py` | point an attribute of one element at another pool string |
| `axmlprocess.py` | give each wallpaper service its own process |
| `axmlhide.py` | hide one service from wallpaper pickers |
| `axmlbool.py` | flip a boolean attribute in binary XML |
| `findssbo.py`, `patchssbo.py` | find and strip vertex-stage storage buffers in Unity shaders (UnityPy, lz4) |
| `miuisuper.py`, `buildmiui.py` | Xiaomi super wallpaper wrapper fixes and full build |
| `rezip.py` | rebuild an APK with replaced entries |
| `sweep.sh` | open every live wallpaper preview over adb and log crashes (`ANDROID_SERIAL` required) |

## License

The tools and patch descriptions are MIT licensed (see `LICENSE`). The wallpapers are not part of this repository.
