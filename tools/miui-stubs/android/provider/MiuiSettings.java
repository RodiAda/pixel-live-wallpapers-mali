package android.provider;
import android.content.ContentResolver;
public class MiuiSettings {
    public static class System {
        public static boolean getBoolean(ContentResolver cr, String name, boolean def) { return def; }
    }
}
