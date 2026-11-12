package pixelfix;

import android.app.WallpaperInfo;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.drawable.Drawable;
import android.service.wallpaper.WallpaperService;
import android.view.SurfaceHolder;
import java.lang.reflect.Field;

public final class Preview {
    private Preview() {}

    public static boolean realEngineActive(Object service) {
        Object player = null;
        Boolean preview = null;
        try {
            for (Class<?> c = service.getClass(); c != null; c = c.getSuperclass()) {
                for (Field f : c.getDeclaredFields()) {
                    if (f.getType().getName().endsWith("MrePlayer")) {
                        f.setAccessible(true);
                        player = f.get(service);
                    } else if (f.getName().equals("mIsPreview") && f.getType() == boolean.class) {
                        f.setAccessible(true);
                        preview = f.getBoolean(service);
                    }
                }
            }
        } catch (Throwable t) {
            return false;
        }
        return player != null && preview != null && !preview;
    }

    public static void draw(Context context, SurfaceHolder holder) {
        if (holder == null || holder.getSurface() == null || !holder.getSurface().isValid()) {
            return;
        }
        Canvas canvas = holder.lockCanvas();
        if (canvas == null) {
            return;
        }
        try {
            canvas.drawColor(Color.BLACK);
            Drawable thumb = thumbnail(context);
            if (thumb != null) {
                int cw = canvas.getWidth(), ch = canvas.getHeight();
                int dw = Math.max(1, thumb.getIntrinsicWidth()), dh = Math.max(1, thumb.getIntrinsicHeight());
                float scale = Math.max(cw / (float) dw, ch / (float) dh);
                int w = Math.round(dw * scale), h = Math.round(dh * scale);
                int l = (cw - w) / 2, t = (ch - h) / 2;
                thumb.setBounds(l, t, l + w, t + h);
                thumb.draw(canvas);
            }
        } catch (Throwable ignored) {
        } finally {
            holder.unlockCanvasAndPost(canvas);
        }
    }

    private static Drawable thumbnail(Context context) {
        try {
            PackageManager pm = context.getPackageManager();
            Intent intent = new Intent(WallpaperService.SERVICE_INTERFACE).setPackage(context.getPackageName());
            for (ResolveInfo ri : pm.queryIntentServices(intent, PackageManager.GET_META_DATA)) {
                if (ri.serviceInfo != null && ri.serviceInfo.name.equals(context.getClass().getName())) {
                    return new WallpaperInfo(context, ri).loadThumbnail(pm);
                }
            }
        } catch (Throwable ignored) {
        }
        return null;
    }
}
