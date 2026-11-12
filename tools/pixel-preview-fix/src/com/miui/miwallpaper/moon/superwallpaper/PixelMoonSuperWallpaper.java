package com.miui.miwallpaper.moon.superwallpaper;

import android.view.SurfaceHolder;
import pixelfix.Preview;

public class PixelMoonSuperWallpaper extends MoonSuperWallpaper {
    @Override
    public Engine onCreateEngine() {
        if (Preview.realEngineActive(this)) {
            return new ThumbnailEngine();
        }
        return super.onCreateEngine();
    }

    class ThumbnailEngine extends Engine {
        @Override
        public void onSurfaceRedrawNeeded(SurfaceHolder holder) {
            Preview.draw(PixelMoonSuperWallpaper.this, holder);
        }

        @Override
        public void onVisibilityChanged(boolean visible) {
            if (visible) {
                Preview.draw(PixelMoonSuperWallpaper.this, getSurfaceHolder());
            }
        }
    }
}
