package com.miui.miwallpaper.earth.superwallpaper;

import android.view.SurfaceHolder;
import pixelfix.Preview;

public class PixelEarthSuperWallpaper extends EarthSuperWallpaper {
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
            Preview.draw(PixelEarthSuperWallpaper.this, holder);
        }

        @Override
        public void onVisibilityChanged(boolean visible) {
            if (visible) {
                Preview.draw(PixelEarthSuperWallpaper.this, getSurfaceHolder());
            }
        }
    }
}
